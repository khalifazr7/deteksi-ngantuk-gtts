# Deteksi Ngantuk dengan Kamera dan Peringatan Suara (gTTS)

Project ini menggunakan **Python**, **OpenCV**, **Mediapipe**, dan **gTTS** untuk mendeteksi tanda-tanda ngantuk melalui mata. Saat terdeteksi ngantuk, sistem akan **mengeluarkan peringatan suara** dan menampilkan teks di layar.

## Fitur

- Deteksi ngantuk berbasis **Eye Aspect Ratio (EAR)** menggunakan Mediapipe Face Mesh.
- Peringatan suara menggunakan **Google Text-to-Speech (gTTS)**.
- Teks peringatan tampil di layar kamera.
- Tidak perlu menyimpan file MP3, suara diputar langsung melalui `pygame`.

## Instalasi

1. Clone repository:

```
git clone https://github.com/khalifazr7/deteksi-ngantuk-gtts.git
cd deteksi-ngantuk-gtts
```

2. Install dependencies:

```
pip install -r requirements.txt
```

## Penggunaan

Jalankan script utama:

```
python ngantuk_detector.py
```

- Tekan q untuk keluar dari aplikasi.
- Pastikan webcam terpasang dan aktif.

## Requirements

- Python 3.8+
- OpenCV
- Mediapipe
- SciPy
- gTTS
- pygame

## Catatan

- Landmark mata di Mediapipe bisa disesuaikan jika deteksi tidak akurat.
- Alarm dan teks akan muncul ketika mata tertutup selama beberapa frame berturut-turut.
