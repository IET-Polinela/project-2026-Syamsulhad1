from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APITestCase

from main_app.models import Report
from main_app.api_views import ReportViewSet
from main_app.serializers import ReportSerializer
from usermanagement_24782031.serializers import RegisterSerializer


User = get_user_model()


class PublicPagesAndUserManagementTests(TestCase):
    def test_about_and_contacts_pages_render(self):
        about_response = self.client.get(reverse('about'))
        contacts_response = self.client.get(reverse('contacts'))

        self.assertEqual(about_response.status_code, 200)
        self.assertTemplateUsed(about_response, 'about/about.html')
        self.assertEqual(contacts_response.status_code, 200)
        self.assertTemplateUsed(contacts_response, 'contacts/contacts.html')

    def test_register_page_get_initializes_form(self):
        response = self.client.get('/accounts/register/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        self.assertIn('form', response.context)
        self.assertEqual(
            response.context['form'].fields['password1'].widget.attrs['class'],
            'form-control',
        )

    def test_register_view_creates_member_user(self):
        payload = {
            'first_name': 'Ayu',
            'last_name': 'Warga',
            'username': 'ayu_warga',
            'email': 'ayu@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }

        response = self.client.post('/accounts/register/', payload)

        self.assertRedirects(response, '/accounts/login/')
        user = User.objects.get(username='ayu_warga')
        self.assertTrue(user.is_member)
        self.assertFalse(user.is_admin)
        self.assertEqual(str(user), 'ayu_warga')

    def test_register_view_rejects_invalid_payload(self):
        response = self.client.post('/accounts/register/', {
            'username': 'bad_register',
            'password1': 'abc',
            'password2': 'different',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='bad_register').exists())

    def test_login_success_invalid_and_logout(self):
        User.objects.create_user(username='login_user', password='StrongPass123!')

        invalid_response = self.client.post('/accounts/login/', {
            'username': 'login_user',
            'password': 'wrong-password',
        })
        self.assertEqual(invalid_response.status_code, 200)

        valid_response = self.client.post('/accounts/login/', {
            'username': 'login_user',
            'password': 'StrongPass123!',
        })
        self.assertRedirects(valid_response, '/')

        logout_response = self.client.post('/accounts/logout/')
        self.assertRedirects(logout_response, '/')

    def test_register_serializer_create_hashes_password(self):
        serializer = RegisterSerializer(data={
            'username': 'serializer_user',
            'password': 'StrongPass123!',
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.username, 'serializer_user')
        self.assertTrue(user.check_password('StrongPass123!'))


class DashboardCoverageTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='dashboard_admin',
            password='StrongPass123!',
            is_admin=True,
        )
        self.citizen = User.objects.create_user(
            username='dashboard_citizen',
            password='StrongPass123!',
            is_admin=False,
        )
        Report.objects.create(
            title='Laporan Baru',
            category='INFRASTRUCTURE',
            description='Jalan rusak',
            location='Jalan Merdeka',
            status='REPORTED',
            reporter=self.citizen,
        )
        Report.objects.create(
            title='Laporan Selesai',
            category='SECURITY',
            description='Sudah ditangani',
            location='Alun-alun',
            status='RESOLVED',
            reporter=self.citizen,
        )

    def test_dashboard_rejects_non_admin_user(self):
        self.client.login(username='dashboard_citizen', password='StrongPass123!')

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('report_list'))

    def test_dashboard_admin_context_contains_statistics(self):
        self.client.login(username='dashboard_admin', password='StrongPass123!')

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')
        self.assertEqual(response.context['total_reports'], 2)
        self.assertEqual(response.context['resolved_reports'], 1)
        self.assertEqual(len(response.context['status_stats']), 5)
        self.assertEqual(len(response.context['category_stats']), 5)

    def test_dashboard_stats_json_contains_latest_reports(self):
        response = self.client.get(reverse('dashboard_stats'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['total_reports'], 2)
        self.assertEqual(data['resolved_reports'], 1)
        self.assertEqual(data['latest_reported'][0]['title'], 'Laporan Baru')
        self.assertEqual(data['latest_resolved'][0]['title'], 'Laporan Selesai')


class ReportApiBranchCoverageTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='api_admin',
            password='StrongPass123!',
            is_admin=True,
        )
        self.citizen = User.objects.create_user(
            username='api_citizen',
            password='StrongPass123!',
            is_admin=False,
        )
        self.other = User.objects.create_user(
            username='api_other',
            password='StrongPass123!',
            is_admin=False,
        )

        self.citizen_draft = Report.objects.create(
            title='Draft Saya',
            category='INFRASTRUCTURE',
            description='Draft warga',
            location='Rumah',
            status='DRAFT',
            reporter=self.citizen,
        )
        self.citizen_reported = Report.objects.create(
            title='Laporan Saya',
            category='HEALTH',
            description='Laporan warga',
            location='Puskesmas',
            status='REPORTED',
            reporter=self.citizen,
        )
        self.other_reported = Report.objects.create(
            title='Laporan Orang Lain',
            category='SECURITY',
            description='Laporan warga lain',
            location='Pasar',
            status='REPORTED',
            reporter=self.other,
        )
        self.other_draft = Report.objects.create(
            title='Draft Orang Lain',
            category='ENVIRONMENT',
            description='Draft warga lain',
            location='Taman',
            status='DRAFT',
            reporter=self.other,
        )

    def _result_ids(self, response):
        payload = response.data
        if isinstance(payload, dict) and 'results' in payload:
            payload = payload['results']
        return {item['id'] for item in payload}

    def _viewset_with_request(self, user, data):
        class DummyRequest:
            pass

        request = DummyRequest()
        request.user = user
        request.data = data

        viewset = ReportViewSet()
        viewset.request = request
        return viewset

    def _serializer_for(self, report):
        class DummySerializer:
            def __init__(self, instance):
                self.instance = instance

            def save(self, **kwargs):
                for field, value in kwargs.items():
                    setattr(self.instance, field, value)
                self.instance.save()

        return DummySerializer(report)

    def test_admin_list_excludes_drafts(self):
        self.client.force_authenticate(self.admin)

        response = self.client.get(reverse('report-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = self._result_ids(response)
        self.assertIn(self.citizen_reported.id, ids)
        self.assertIn(self.other_reported.id, ids)
        self.assertNotIn(self.citizen_draft.id, ids)
        self.assertNotIn(self.other_draft.id, ids)

    def test_citizen_my_reports_and_feed_tabs(self):
        self.client.force_authenticate(self.citizen)

        my_response = self.client.get(reverse('report-list'), {'tab': 'my_reports'})
        feed_response = self.client.get(reverse('report-list'), {'tab': 'feed'})

        self.assertEqual(my_response.status_code, status.HTTP_200_OK)
        self.assertEqual(feed_response.status_code, status.HTTP_200_OK)
        self.assertSetEqual(
            self._result_ids(my_response),
            {self.citizen_draft.id, self.citizen_reported.id},
        )
        self.assertSetEqual(
            self._result_ids(feed_response),
            {self.other_reported.id},
        )

    def test_admin_cannot_create_or_delete_report(self):
        self.client.force_authenticate(self.admin)

        create_response = self.client.post(reverse('report-list'), {
            'title': 'Laporan Admin',
            'category': 'INFRASTRUCTURE',
            'description': 'Admin mencoba membuat laporan',
            'location': 'Balai kota',
        }, format='json')
        delete_response = self.client.delete(
            reverse('report-detail', kwargs={'pk': self.citizen_reported.id})
        )

        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_update_status_rules(self):
        self.client.force_authenticate(self.admin)

        success_response = self.client.patch(
            reverse('report-detail', kwargs={'pk': self.citizen_reported.id}),
            {'status': 'VERIFIED'},
            format='json',
        )
        draft_response = self.client.patch(
            reverse('report-detail', kwargs={'pk': self.citizen_draft.id}),
            {'status': 'VERIFIED'},
            format='json',
        )
        invalid_response = self.client.patch(
            reverse('report-detail', kwargs={'pk': self.other_reported.id}),
            {'status': 'DRAFT'},
            format='json',
        )

        self.assertEqual(success_response.status_code, status.HTTP_200_OK)
        self.citizen_reported.refresh_from_db()
        self.assertEqual(self.citizen_reported.status, 'VERIFIED')
        self.assertEqual(draft_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_perform_update_rejects_draft_reports(self):
        viewset = self._viewset_with_request(self.admin, {'status': 'VERIFIED'})
        serializer = self._serializer_for(self.citizen_draft)

        with self.assertRaises(PermissionDenied):
            viewset.perform_update(serializer)

    def test_admin_perform_update_direct_success_uses_serializer_save(self):
        viewset = self._viewset_with_request(self.admin, {'status': 'IN_PROGRESS'})
        serializer = self._serializer_for(self.other_reported)

        viewset.perform_update(serializer)

        self.other_reported.refresh_from_db()
        self.assertEqual(self.other_reported.status, 'IN_PROGRESS')

    def test_viewset_default_permissions_branch(self):
        viewset = ReportViewSet()
        viewset.action = 'metadata'

        permissions = viewset.get_permissions()

        self.assertIsInstance(permissions, list)

    def test_citizen_update_and_delete_rules(self):
        self.client.force_authenticate(self.citizen)

        submit_draft_response = self.client.patch(
            reverse('report-detail', kwargs={'pk': self.citizen_draft.id}),
            {'status': 'REPORTED'},
            format='json',
        )
        forbidden_update_response = self.client.patch(
            reverse('report-detail', kwargs={'pk': self.other_reported.id}),
            {'status': 'RESOLVED'},
            format='json',
        )
        forbidden_delete_response = self.client.delete(
            reverse('report-detail', kwargs={'pk': self.citizen_reported.id})
        )

        self.assertEqual(submit_draft_response.status_code, status.HTTP_200_OK)
        self.citizen_draft.refresh_from_db()
        self.assertEqual(self.citizen_draft.status, 'REPORTED')
        self.assertEqual(forbidden_update_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(forbidden_delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_citizen_can_delete_own_draft(self):
        self.client.force_authenticate(self.citizen)

        response = self.client.delete(
            reverse('report-detail', kwargs={'pk': self.citizen_draft.id})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Report.objects.filter(pk=self.citizen_draft.id).exists())

    def test_submit_action_success_and_validation_errors(self):
        self.client.force_authenticate(self.citizen)

        success_response = self.client.post(
            reverse('report-submit', kwargs={'pk': self.citizen_draft.id})
        )
        non_draft_response = self.client.post(
            reverse('report-submit', kwargs={'pk': self.citizen_reported.id})
        )

        self.client.force_authenticate(self.other)
        not_owner_response = self.client.post(
            reverse('report-submit', kwargs={'pk': self.citizen_draft.id})
        )

        self.assertEqual(success_response.status_code, status.HTTP_200_OK)
        self.citizen_draft.refresh_from_db()
        self.assertEqual(self.citizen_draft.status, 'REPORTED')
        self.assertEqual(non_draft_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(not_owner_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_report_serializer_rejects_invalid_category_and_handles_unknown_reporter(self):
        invalid_serializer = ReportSerializer(data={
            'title': 'Kategori Salah',
            'category': 'Tidak Ada',
            'description': 'Kategori tidak sesuai pilihan',
            'location': 'Bandung',
        })
        orphan_report = Report.objects.create(
            title='Tanpa Reporter',
            category='ENVIRONMENT',
            description='Laporan impor lama tanpa reporter',
            location='Arsip',
            status='REPORTED',
            reporter=None,
        )
        orphan_serializer = ReportSerializer(orphan_report, context={})

        self.assertFalse(invalid_serializer.is_valid())
        self.assertIn('category', invalid_serializer.errors)
        self.assertEqual(orphan_serializer.data['reporter'], 'Tidak diketahui')
