import time
from datetime import datetime
from django.core.management.base import BaseCommand
from sinkronisasi.sister_client import get_token, fetch_jabatan_fungsional
from sinkronisasi.models import Dosen, JabatanFungsional


def parse_tanggal(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


class Command(BaseCommand):
    help = "Sinkronisasi riwayat jabatan fungsional seluruh dosen dari API SISTER"

    def handle(self, *args, **kwargs):
        try:
            token = get_token()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Gagal mendapatkan token: {e}"))
            return

        dosen_list = Dosen.objects.all()
        total_dosen = dosen_list.count()
        created, updated, skipped, gagal = 0, 0, 0, 0

        for i, dosen in enumerate(dosen_list, start=1):
            try:
                data = fetch_jabatan_fungsional(token, dosen.id_sdm)
            except Exception as e:
                self.stderr.write(self.style.WARNING(
                    f"[{i}/{total_dosen}] Gagal ambil jabfung {dosen.id_sdm}: {e}"
                ))
                gagal += 1
                continue

            if not isinstance(data, list):
                skipped += 1
                continue

            for item in data:
                id_jabfung = str(item.get('id', '')).strip()
                jabatan = item.get('jabatan_fungsional', '').strip()

                if not id_jabfung or not jabatan:
                    skipped += 1
                    continue

                obj, is_new = JabatanFungsional.objects.update_or_create(
                    id_jabfung=id_jabfung,
                    defaults={
                        'dosen': dosen,
                        'jabatan_fungsional': jabatan,
                        'sk': item.get('sk'),
                        'tanggal_mulai': parse_tanggal(item.get('tanggal_mulai')),
                        'id_stat_pegawai': item.get('id_stat_pegawai'),
                        'nm_stat_pegawai': item.get('nm_stat_pegawai'),
                    }
                )
                created += int(is_new)
                updated += int(not is_new)

            # beri jeda kecil agar tidak membebani API SISTER (rate limiting sederhana)
            time.sleep(0.3)

            if i % 50 == 0:
                self.stdout.write(f"Progres: {i}/{total_dosen} dosen diproses...")

        self.stdout.write(self.style.SUCCESS(
            f"Selesai. Dosen diproses: {total_dosen}, Gagal: {gagal}, "
            f"Riwayat baru: {created}, Riwayat update: {updated}, Dilewati: {skipped}, "
            f"Total riwayat di DB: {JabatanFungsional.objects.count()}"
        ))