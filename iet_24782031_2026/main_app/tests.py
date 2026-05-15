from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Report


class ReportCreateViewTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_user(
            username='adminlaporan',
            password='password123',
            is_admin=True,
            is_member=False,
        )

    def test_admin_can_create_report_without_posting_status(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse('report_create'),
            data={
                'title': 'Lampu jalan mati',
                'category': 'INFRASTRUCTURE',
                'description': 'Lampu jalan di depan balai kota mati sejak kemarin.',
                'location': 'Jalan Utama',
            },
        )

        self.assertRedirects(response, reverse('report_list'))
        self.assertEqual(Report.objects.count(), 1)

        report = Report.objects.get()
        self.assertEqual(report.status, 'REPORTED')


class ReportApiCitizenWorkflowTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.citizen = User.objects.create_user(
            username='warga',
            password='password123',
            is_admin=False,
            is_member=True,
        )
        self.other_citizen = User.objects.create_user(
            username='warga_lain',
            password='password123',
            is_admin=False,
            is_member=True,
        )
        self.admin_user = User.objects.create_user(
            username='adminapi',
            password='password123',
            is_admin=True,
            is_member=False,
        )

    def test_citizen_creates_draft_report_with_anonymity(self):
        self.client.force_authenticate(self.citizen)

        response = self.client.post(
            reverse('report-list'),
            data={
                'title': 'Sampah menumpuk',
                'category': 'ENVIRONMENT',
                'description': 'Sampah belum diangkut selama dua hari.',
                'location': 'Jalan Mawar',
                'is_anonymous': True,
                'status': 'RESOLVED',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        report = Report.objects.get()
        self.assertEqual(report.status, 'DRAFT')
        self.assertEqual(report.reporter, self.citizen)
        self.assertTrue(report.is_anonymous)
        self.assertEqual(response.data['reporter'], 'Warga Anonim')

    def test_citizen_can_submit_own_draft(self):
        self.client.force_authenticate(self.citizen)
        report = Report.objects.create(
            title='Drainase tersumbat',
            category='INFRASTRUCTURE',
            description='Air menggenang setelah hujan.',
            location='Jalan Kenanga',
            reporter=self.citizen,
            status='DRAFT',
        )

        response = self.client.post(reverse('report-submit', kwargs={'pk': report.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report.refresh_from_db()
        self.assertEqual(report.status, 'REPORTED')

    def test_citizen_cannot_see_other_citizen_draft(self):
        own_draft = Report.objects.create(
            title='Draft sendiri',
            category='ENVIRONMENT',
            description='Masih draft.',
            location='Rumah',
            reporter=self.citizen,
            status='DRAFT',
        )
        Report.objects.create(
            title='Draft warga lain',
            category='SECURITY',
            description='Tidak boleh terlihat.',
            location='Lokasi lain',
            reporter=self.other_citizen,
            status='DRAFT',
        )
        self.client.force_authenticate(self.citizen)

        response = self.client.get(reverse('report-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item['id'] for item in response.data], [own_draft.id])

    def test_admin_does_not_receive_citizen_drafts_from_api(self):
        Report.objects.create(
            title='Draft warga',
            category='ENVIRONMENT',
            description='Belum dikirim.',
            location='Jalan Melati',
            reporter=self.citizen,
            status='DRAFT',
        )
        submitted = Report.objects.create(
            title='Sudah masuk',
            category='HEALTH',
            description='Perlu ditangani.',
            location='Puskesmas',
            reporter=self.citizen,
            status='REPORTED',
        )
        self.client.force_authenticate(self.admin_user)

        response = self.client.get(reverse('report-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item['id'] for item in response.data], [submitted.id])

