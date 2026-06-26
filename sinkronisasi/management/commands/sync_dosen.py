from datetime import datetime
from django.utils import timezone as django_timezone
from django.core.management.base import BaseCommand
from sinkronisasi.sister_client import get_token, fetch_referensi_sdm
from sinkronisasi.models import Dosen


def parse_waktu(value):
    if not value:
        return None
    try:
        naive_dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return django_timezone.make_aware(naive_dt)
    except (ValueError, TypeError):
        return None


class Command(BaseCommand):
    help = "Sinkronisasi data dosen dari API SISTER (referensi/sdm) ke database MariaDB"

    def handle(self, *args, **kwargs):
        try:
            token = get_token()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Gagal mendapatkan token: {e}"))
            return

        try:
            data = fetch_referensi_sdm(token)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Gagal mengambil data referensi SDM: {e}"))
            return

        if not isinstance(data, list):
            self.stderr.write(self.style.ERROR(f"Format respons tidak sesuai: {data}"))
            return

        created, updated, skipped = 0, 0, 0

        for item in data:
            id_sdm = str(item.get('id_sdm', '')).strip()
            nama = item.get('nama_sdm', '').strip().title()

            # Validasi: id_sdm wajib ada sebagai unique key
            if not id_sdm or not nama:
                skipped += 1
                continue

            obj, is_new = Dosen.objects.update_or_create(
                id_sdm=id_sdm,
                defaults={
                    'nama': nama,
                    'nidn': item.get('nidn') or None,
                    'nuptk': item.get('nuptk') or None,
                    'nip': item.get('nip') or None,
                    'status_aktif': item.get('nama_status_aktif'),
                    'status_pegawai': item.get('nama_status_pegawai'),
                    'jenis_sdm': item.get('jenis_sdm'),
                    'waktu_data_update': parse_waktu(item.get('waktu_data_update')),
                    'sumber_data': 'SISTER',
                }
            )
            created += int(is_new)
            updated += int(not is_new)

        self.stdout.write(self.style.SUCCESS(
            f"Selesai. Baru: {created}, Update: {updated}, Dilewati: {skipped}, "
            f"Total sumber: {len(data)}, Total di DB: {Dosen.objects.count()}"
        ))