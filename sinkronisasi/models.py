from django.db import models

class Dosen(models.Model):
    id_sdm = models.CharField(max_length=64, unique=True)
    nidn = models.CharField(max_length=20, blank=True, null=True)
    nuptk = models.CharField(max_length=20, blank=True, null=True)
    nip = models.CharField(max_length=30, blank=True, null=True)
    nama = models.CharField(max_length=255)
    status_aktif = models.CharField(max_length=50, blank=True, null=True)
    status_pegawai = models.CharField(max_length=50, blank=True, null=True)
    jenis_sdm = models.CharField(max_length=50, blank=True, null=True)
    waktu_data_update = models.DateTimeField(blank=True, null=True)
    sumber_data = models.CharField(max_length=50, default='SISTER')
    synced_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nidn or self.nip or self.id_sdm} - {self.nama}"
    
class JabatanFungsional(models.Model):
    dosen = models.ForeignKey(Dosen, on_delete=models.CASCADE, related_name='riwayat_jabatan')
    id_jabfung = models.CharField(max_length=64, unique=True)  # field 'id' dari API
    jabatan_fungsional = models.CharField(max_length=255)
    sk = models.CharField(max_length=100, blank=True, null=True)
    tanggal_mulai = models.DateField(blank=True, null=True)
    id_stat_pegawai = models.IntegerField(blank=True, null=True)
    nm_stat_pegawai = models.CharField(max_length=50, blank=True, null=True)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-tanggal_mulai']

    def __str__(self):
        return f"{self.dosen.nama} - {self.jabatan_fungsional} ({self.tanggal_mulai})"