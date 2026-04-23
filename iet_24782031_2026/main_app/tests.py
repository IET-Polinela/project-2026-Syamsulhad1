from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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

