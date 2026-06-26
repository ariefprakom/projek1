from django.core.management.base import BaseCommand
from django.db.models import Count
from sinkronisasi.models import Dosen


class Command(BaseCommand):
    help = "Quality check data dosen hasil sinkronisasi SISTER"

    def handle(self, *args, **kwargs):
        total = Dosen.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Total data dosen di database: {total}"))

        self.stdout.write("\n-- Distribusi Status Aktif --")
        for row in Dosen.objects.values('status_aktif').annotate(jumlah=Count('id')).order_by('-jumlah'):
            self.stdout.write(f"  {row['status_aktif'] or '(kosong)'}: {row['jumlah']}")

        self.stdout.write("\n-- Distribusi Status Pegawai --")
        for row in Dosen.objects.values('status_pegawai').annotate(jumlah=Count('id')).order_by('-jumlah'):
            self.stdout.write(f"  {row['status_pegawai'] or '(kosong)'}: {row['jumlah']}")

        self.stdout.write("\n-- Distribusi Jenis SDM --")
        for row in Dosen.objects.values('jenis_sdm').annotate(jumlah=Count('id')).order_by('-jumlah'):
            self.stdout.write(f"  {row['jenis_sdm'] or '(kosong)'}: {row['jumlah']}")

        # Cek anomali data
        kosong_nidn = Dosen.objects.filter(nidn__isnull=True).count()
        kosong_nip = Dosen.objects.filter(nip__isnull=True).count()
        self.stdout.write("\n-- Cek Anomali --")
        self.stdout.write(f"  Data tanpa NIDN: {kosong_nidn}")
        self.stdout.write(f"  Data tanpa NIP : {kosong_nip}")