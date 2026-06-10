import random

from django.core.management.base import BaseCommand
from faker import Faker

from main_app.models import Report


fake = Faker('id_ID')


class Command(BaseCommand):
    help = 'Generate contextual fake reports for SmartReport'

    def add_arguments(self, parser):
        parser.add_argument('num_records', type=int, help='Jumlah data')

    def handle(self, *args, **kwargs):
        num_records = kwargs['num_records']

        context_data = {
            'INFRASTRUCTURE': {
                'titles': [
                    'Lubang Besar di Tengah Jalan',
                    'Aspal Mengelupas Parah',
                    'Jalan Bergelombang Bahayakan Motor',
                    'Ambles di Dekat Drainase',
                ],
                'desc': (
                    'Ditemukan kerusakan fasilitas infrastruktur yang cukup serius. '
                    'Mohon segera ditangani sebelum membahayakan pengguna jalan.'
                ),
            },
            'ENVIRONMENT': {
                'titles': [
                    'Tumpukan Sampah Liar',
                    'Bau Menyengat Sampah Menumpuk',
                    'TPS Melebihi Kapasitas',
                    'Sampah Menutup Saluran Air',
                    'Saluran Air Mampet',
                    'Drainase Meluap Saat Hujan',
                ],
                'desc': (
                    'Warga mengeluhkan masalah lingkungan yang mengganggu aktivitas. '
                    'Kondisi ini perlu segera ditindaklanjuti agar tidak semakin parah.'
                ),
            },
            'PUBLIC_FACILITY': {
                'titles': [
                    'Penerangan Jalan Umum Mati',
                    'Lampu Jalan Berkedip',
                    'Bangku Taman Rusak',
                    'Halte Bus Perlu Perbaikan',
                    'Toilet Umum Tidak Terawat',
                    'Fasilitas Bermain Anak Rusak',
                ],
                'desc': (
                    'Warga melaporkan fasilitas publik yang tidak berfungsi dengan baik. '
                    'Mohon dilakukan pengecekan dan perbaikan agar dapat digunakan kembali.'
                ),
            },
            'SECURITY': {
                'titles': [
                    'Aksi Vandalisme Fasilitas Umum',
                    'Pencurian Kabel Telepon',
                    'Laporan Kerumunan Mencurigakan',
                    'Gangguan Ketertiban Umum',
                ],
                'desc': (
                    'Dibutuhkan patroli tambahan di area ini karena laporan warga '
                    'terkait aktivitas yang mencurigakan pada jam malam.'
                ),
            },
            'HEALTH': {
                'titles': [
                    'Genangan Air Rawan Penyakit',
                    'Bau Limbah Mengganggu Warga',
                    'Sarang Nyamuk di Area Permukiman',
                    'Keluhan Sanitasi Lingkungan',
                ],
                'desc': (
                    'Warga melaporkan kondisi yang berpotensi mengganggu kesehatan '
                    'masyarakat sekitar dan membutuhkan pengecekan petugas.'
                ),
            },
        }

        status_choices = ['REPORTED', 'VERIFIED', 'IN_PROGRESS', 'RESOLVED']
        reports = []

        for _ in range(num_records):
            category = random.choice(list(context_data.keys()))
            title_template = random.choice(context_data[category]['titles'])
            description_base = context_data[category]['desc']

            reports.append(
                Report(
                    title=f'{title_template} - {fake.street_name()}',
                    category=category,
                    description=(
                        f'{description_base} Lokasi detail: '
                        f'{fake.street_address()}.'
                    ),
                    location=f'Kecamatan {fake.city()}, {fake.address()}',
                    status=random.choice(status_choices),
                )
            )

        Report.objects.bulk_create(reports)

        self.stdout.write(
            self.style.SUCCESS(
                f'Berhasil membuat {num_records} laporan yang kontekstual!'
            )
        )
