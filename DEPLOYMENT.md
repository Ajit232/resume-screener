# ResumeAI Screener — Deployment Guide

---

## LOCAL DEVELOPMENT (Windows / macOS / Linux)

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Git

### Setup steps

```bash
# 1. Clone or extract the project
cd C:\Users\chinu\projects\resume_screener_project\resume_screener

# 2. Activate virtual environment
# Windows:
resumeai_env\Scripts\Activate.ps1
# macOS/Linux:
source resumeai_env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 4. Create .env file
copy .env.example .env
# Edit .env with your DB credentials and SECRET_KEY

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Load sample data (optional)
python manage.py shell < sample_data.py

# 8. Collect static files
python manage.py collectstatic --noinput

# 9. Start server
python manage.py runserver
```

Open http://127.0.0.1:8000/

---

## ENVIRONMENT VARIABLES (.env)

```
SECRET_KEY=your-50-char-random-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=resume_screener_db
DB_USER=resume_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

Generate SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## POSTGRESQL SETUP

```sql
-- Run in psql as postgres superuser
CREATE DATABASE resume_screener_db;
CREATE USER resume_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE resume_screener_db TO resume_user;

-- PostgreSQL 15+ also needs this:
\c resume_screener_db
GRANT ALL ON SCHEMA public TO resume_user;
\q
```

---

## PRODUCTION DEPLOYMENT (Ubuntu Server)

### 1. Server setup

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.11 python3.11-venv python3-pip postgresql nginx git -y
```

### 2. Create database

```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE resume_screener_db;
CREATE USER resume_user WITH PASSWORD 'StrongProdPassword';
GRANT ALL PRIVILEGES ON DATABASE resume_screener_db TO resume_user;
\c resume_screener_db
GRANT ALL ON SCHEMA public TO resume_user;
\q
```

### 3. Clone and set up project

```bash
cd /var/www
sudo git clone <your-repo-url> resumeai
sudo chown -R $USER:$USER /var/www/resumeai
cd /var/www/resumeai/resume_screener

python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Production .env

```bash
nano .env
```

```
SECRET_KEY=your-production-secret-key-50-chars
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

DB_NAME=resume_screener_db
DB_USER=resume_user
DB_PASSWORD=StrongProdPassword
DB_HOST=localhost
DB_PORT=5432
```

### 5. Run migrations and collect static

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 6. Gunicorn setup

```bash
nano /etc/systemd/system/resumeai.service
```

```ini
[Unit]
Description=ResumeAI Gunicorn Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/resumeai/resume_screener
ExecStart=/var/www/resumeai/resume_screener/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/resumeai.sock \
    config.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start resumeai
sudo systemctl enable resumeai
sudo systemctl status resumeai
```

### 7. Nginx configuration

```bash
sudo nano /etc/nginx/sites-available/resumeai
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /var/www/resumeai/resume_screener/staticfiles;
    }

    location /media/ {
        root /var/www/resumeai/resume_screener/media;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/resumeai.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/resumeai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. SSL with Let's Encrypt (optional but recommended)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## MEDIA FILES PERMISSIONS (Production)

```bash
sudo chown -R www-data:www-data /var/www/resumeai/resume_screener/media
sudo chmod -R 755 /var/www/resumeai/resume_screener/media
```

---

## USEFUL COMMANDS

```bash
# Check Django status
python manage.py check

# Run server (development)
python manage.py runserver

# Make and apply migrations
python manage.py makemigrations
python manage.py migrate

# Load sample data
python manage.py shell < sample_data.py

# Create admin user
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# View logs (production)
sudo journalctl -u resumeai -f

# Restart services (production)
sudo systemctl restart resumeai
sudo systemctl restart nginx
```

---

## UPGRADING spaCy MODEL

```bash
python -m spacy download en_core_web_sm
# Or for better accuracy (larger model, slower):
python -m spacy download en_core_web_md
```

If you switch to en_core_web_md update skill_extractor.py:
```python
_nlp = spacy.load("en_core_web_md")
```

---

## PROJECT STRUCTURE SUMMARY

```
resume_screener/
├── config/          Django project settings and URLs
├── accounts/        User registration, login, profile
├── jobs/            Job description upload and parsing
├── resumes/         Resume upload, editor, versioning
├── analysis/        Scoring engine and results
├── dashboard/       User dashboard
├── services/        NLP services (extractor, parser, scorer)
├── templates/       Global HTML templates
├── static/          CSS and JS files
├── media/           User uploaded files
└── manage.py        Django management entry point
```

---

## SCORING WEIGHTS (configurable in services/scorer.py)

```python
SKILL_WEIGHT       = 0.40   # 40% — skill overlap
KEYWORD_WEIGHT     = 0.25   # 25% — keyword presence
EXPERIENCE_WEIGHT  = 0.20   # 20% — years of experience
EDUCATION_WEIGHT   = 0.15   # 15% — education level
```

To adjust, edit these four constants in `services/scorer.py`.
All four must sum to 1.0.

---

## SCORE LABELS

| Score     | Label          | Badge colour |
|-----------|----------------|--------------|
| 80 - 100  | Strong Match   | Green        |
| 60 - 79   | Good Match     | Blue         |
| 40 - 59   | Partial Match  | Yellow       |
| 0  - 39   | Low Match      | Red          |
