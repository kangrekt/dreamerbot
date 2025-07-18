# 🌙 POD - Dreamer Quests Bot

**Dreamer Quests Bot** adalah bot otomatis berbasis Python untuk menyelesaikan task, spin harian, dan check-in otomatis di [Dreamer Quests](https://dreamerquests.partofdream.io/).

> **Belum punya akun?** Silakan daftar terlebih dahulu melalui tautan berikut: [**👉 LINK DAFTAR DREAMER QUESTS**](https://dreamerquests.partofdream.io/login?referralCodeForPOD=2650d60d)

---

## ✨ Fitur Utama

* 🔄 **Multi Akun** – Mendukung banyak akun melalui `cookies.txt`
* ✅ **Auto Task** – Selesaikan task otomatis dan klaim poin
* 🎡 **Auto Spin Harian** – Spin otomatis dan check-in setelah spin
* ⏳ **Auto Cooldown** – Auto loop 24jam sekali
* 🌐 **Dukungan Proxy** – Bisa menggunakan proxy dari `proxies.txt`

---

## 📂 Struktur File Pendukung

| File          | Fungsi                                             |
| ------------- | -------------------------------------------------- |
| `cookies.txt` | Daftar session token akun (setiap baris = 1 akun)  |
| `proxies.txt` | Daftar proxy yang digunakan secara acak (opsional) |
| `bot.py`      | Script utama untuk menjalankan bot Dreamer Quests  |

---

## 🔧 Instalasi

### 1. Wajib Mengaktifkan Screen

```bash
apt install screen
screen -S dreamerbot
```

### 2. Clone Repo

```bash
git clone https://github.com/kangrekt/dreamerbot.git
cd dreamerbot
```

### 3. Install Dependensi (Virtual Environment Disarankan)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Jika belum ada `requirements.txt`, install manual:

```bash
pip install requests rich beautifulsoup4
```

---

## 🚀 Cara Menjalankan

```bash
python bot.py
```

Pastikan file `cookies.txt` telah diisi dengan session token:
`klik F12, pada Tab Network klik session, dan pada baris cookie terdapat connect.sid=xxx`
```text
connect.sid=xxxx (token akun 1)
connect.sid=xxxx (token akun 2)
```

Jika ingin menggunakan proxy, isi `proxies.txt`:

```text
http://user:pass@ip:port
http://ip:port
```

### Alur Kerja Otomatis

1. Mengecek sesi akun dan status task
2. Menyelesaikan semua task otomatis
3. Spin harian otomatis
4. Check-in otomatis setelah spin
5. Auto countdown 24 jam untuk spin dan Check-in berikutnya

---

## 📝 Contoh Output Terminal

```
=== ✓ TUGAS SELESAI ===
• Task: Follow us on Twitter → ✅ Berhasil
• Poin Ditambahkan: 50

=== ✓ HASIL SPIN ===
🎁 Hadiah: 100 Points
⭐ Poin Spin: 50
💰 USDT: 0.1
```

---

## ⚠️ Catatan Penting

* Gunakan session token aktif dari akun Dreamer Quests
* Jangan gunakan akun secara berlebihan agar tidak terkena pembatasan

---

## 📜 Lisensi

MIT License © 2025 [@kangrekt](https://github.com/kangrekt)

---

## ☕ Dukungan

Jika bot ini membantumu, bantu dengan:

* ⭐ Memberi bintang di GitHub
* 🏱 Kontribusi pull request / ide baru
* 📣 Share ke komunitas lain

---

## 📢 Social

Join Telegram: [https://t.me/ingpokanjepe](https://t.me/ingpokanjepe)

---
