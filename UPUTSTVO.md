# Daily Digest — Uputstvo za postavljanje

Automatizovana Python aplikacija koja svako jutro u **07:30** šalje
dnevni izvještaj sa vremenskom prognozom i vijestima iz 6 kategorija.

---

## Struktura projekta

```
daily_digest/
├── main.py          # Entrypoint + scheduler
├── weather.py       # OpenWeatherMap API
├── news.py          # NewsAPI + RSS feeds
├── report.py        # HTML/TXT/Telegram builder
├── delivery.py      # Email (SMTP) + Telegram
├── requirements.txt
├── .env.example     # ← kopirati u .env i popuniti
└── .env             # NIKAD ne commitati u git!
```

---

## 1. Preduslovi

- Python 3.11+ 
- Linux/macOS (preporučeno) ili Windows

```bash
python --version   # Treba biti >= 3.11
```

---

## 2. Instalacija

```bash
# Klonirati / preuzeti fajlove, ući u direktorij
cd daily_digest

# Virtualno okruženje (preporučeno)
python -m venv venv
source venv/bin/activate          # Linux/macOS
# venv\Scripts\activate           # Windows

# Instalacija zavisnosti
pip install -r requirements.txt
```

---

## 3. API ključevi (besplatni)

### 3.1 OpenWeatherMap (prognoza)
1. Registracija: https://openweathermap.org/api
2. Meni: *API Keys* → kopirajte ključ
3. Besplatni tier: 1.000 poziva/dan ✅

### 3.2 NewsAPI (vijesti)
1. Registracija: https://newsapi.org/register
2. Kopirajte API key s dashboarda
3. Besplatni tier: 100 poziva/dan ✅ (dovoljno za 6 kategorija)

### 3.3 Gmail App Password (email)
> Gmail ne dozvoljava direktnu lozinku — treba **App Password**.

1. https://myaccount.google.com/security
2. Uključiti **2-faktorsku autentifikaciju** (ako nije)
3. Pretražiti *"App Passwords"* → odabrati *Mail* → *Other* → dati naziv (npr. `DailyDigest`)
4. Gmail generiše 16-znakovna lozinku → kopirajte je

### 3.4 Telegram Bot (alternativa/backup)
> Telegram je bolji za mobilne notifikacije od emaila.

```
1. Otvorite Telegram, potražite @BotFather
2. Pošaljite: /newbot
3. Dajte naziv i username botu → dobijete TOKEN
4. Pošaljite botu bilo koji tekst (da postoji chat)
5. Otvorite: https://api.telegram.org/bot<TOKEN>/getUpdates
6. Pronađite "id" unutar "chat" objekta → to je CHAT_ID
```

---

## 4. Konfiguracija .env

```bash
cp .env.example .env
nano .env   # ili bilo koji editor
```

Popunite sva polja:

```env
OPENWEATHER_API_KEY=abc123...
NEWS_API_KEY=xyz456...

GMAIL_USER=acatovic@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop

TELEGRAM_BOT_TOKEN=123456789:ABCdef...
TELEGRAM_CHAT_ID=987654321

RECIPIENT_EMAIL=acatovic@gmail.com
DELIVERY_METHOD=both   # "email", "telegram" ili "both"
```

---

## 5. Testiranje

```bash
# Test jednog slanja odmah (bez čekanja 07:30)
python main.py --now

# Trebate vidjeti u konzoli:
# ✅ Email uspješno poslan na acatovic@gmail.com
# ✅ Telegram poruka uspješno poslana.
```

---

## 6. Pokretanje

### Opcija A — Daemon (direktno)

Pokreće scheduler koji čeka 07:30 svaki dan.

```bash
python main.py
# Ctrl+C za zaustavljanje
```

### Opcija B — systemd servis (Linux, preporučeno za server)

Kreira systemd servis koji se automatski pokreće pri restartu sistema.

```bash
# Kreirati servis fajl
sudo nano /etc/systemd/system/daily-digest.service
```

Sadržaj (prilagodite putanje!):

```ini
[Unit]
Description=Daily Digest — Jutarnji sažetak vijesti
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/daily_digest
ExecStart=/home/YOUR_USERNAME/daily_digest/venv/bin/python main.py
Restart=on-failure
RestartSec=60
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable daily-digest
sudo systemctl start  daily-digest
sudo systemctl status daily-digest   # Provjera statusa
journalctl -u daily-digest -f        # Live logovi
```

### Opcija C — cron (jednostavno, Linux/macOS)

```bash
crontab -e
```

Dodati red:
```
30 7 * * * /home/YOUR_USERNAME/daily_digest/venv/bin/python /home/YOUR_USERNAME/daily_digest/main.py --cron >> /home/YOUR_USERNAME/daily_logs/digest.log 2>&1
```

### Opcija D — Windows Task Scheduler

1. *Taskschd.msc* → Create Basic Task
2. Trigger: Daily, 07:30
3. Action: Start program
   - Program: `C:\Users\You\daily_digest\venv\Scripts\python.exe`
   - Arguments: `main.py --cron`
   - Start in: `C:\Users\You\daily_digest`

---

## 7. Sadržaj izvještaja

| Kategorija | Izvor |
|---|---|
| 🌤 Prognoza Sarajevo | OpenWeatherMap |
| 🤖 AI vijesti | NewsAPI (EN) |
| 🏙️ Sarajevo lokalne | Klix.ba, Oslobođenje, Radio Sarajevo (RSS) |
| 🇧🇦 Vijesti BiH | Klix.ba, Oslobođenje, N1 (RSS) |
| 🌍 Geopolitika | NewsAPI (EN) |
| 🔭 Astronomija | NewsAPI (EN) |
| 📷 Astrofotografija | NewsAPI (EN) |

---

## 8. Prilagođavanje

### Dodavanje RSS feedova (npr. Al Jazeera Balkans)
U `news.py`, dodajte URL u `RSS_FEEDS`:
```python
RSS_FEEDS = {
    "bih": [
        "https://www.klix.ba/rss/vijesti/bih",
        "https://balkans.aljazeera.net/feed",   # ← novo
    ],
```

### Promjena vremena slanja
U `main.py`, promijenite `CronTrigger`:
```python
CronTrigger(hour=6, minute=0, timezone=TIMEZONE)  # 06:00
```

### Broj vijesti po kategoriji
U `news.py`, promijenite `MAX_ARTICLES`:
```python
MAX_ARTICLES = 7  # Defaultno je 5
```

---

## 9. Troubleshooting

| Problem | Rješenje |
|---|---|
| Gmail auth greška | Provjerite App Password, ne koristite originalnu lozinku |
| NewsAPI 429 error | Previše poziva — besplatni tier je 100/dan; smanjite `MAX_ARTICLES` |
| Telegram ne šalje | Uvjerite se da ste poslali neku poruku botu prije; provjerite CHAT_ID |
| RSS nema vijesti | Provjerite URL feeda u browseru; feedovi se ponekad mijenjaju |
| Scheduler ne pali u 07:30 | Provjerite vremensku zonu sistema: `timedatectl` (Linux) |

---

## 10. Logovi

```bash
tail -f daily_digest.log   # Praćenje logova u realnom vremenu
```

---

*Aplikacija je modularna — svaki modul (weather.py, news.py, delivery.py)
može se koristiti i testirati samostalno.*
