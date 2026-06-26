import requests
from django.conf import settings

HEADERS_AUTH = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}


def get_token():
    """Ambil token autentikasi dari API SISTER."""
    url = f"{settings.SISTER_BASE_URL}/authorize"
    data = {
        'username': settings.SISTER_USERNAME,
        'password': settings.SISTER_PASSWORD,
        'id_pengguna': settings.SISTER_ID_PENGGUNA,
    }
    files = {k: (None, v) for k, v in data.items()}

    resp = requests.post(url, files=files, headers=HEADERS_AUTH, timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    if 'token' not in payload:
        raise ValueError(f"Respons tidak mengandung token: {payload}")
    return payload['token']


def fetch_referensi_sdm(token):
    """Ambil daftar referensi SDM (dosen/tendik) dari API SISTER."""
    url = f"{settings.SISTER_BASE_URL}/referensi/sdm"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'User-Agent': HEADERS_AUTH['User-Agent'],   # <-- tambahan ini
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()

def fetch_jabatan_fungsional(token, id_sdm):
    """Ambil riwayat jabatan fungsional seorang dosen berdasarkan id_sdm."""
    url = f"{settings.SISTER_BASE_URL}/jabatan_fungsional"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'User-Agent': HEADERS_AUTH['User-Agent'],
    }
    params = {'id_sdm': id_sdm}
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()