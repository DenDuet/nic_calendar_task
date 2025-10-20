# Инструкция по развертыванию Work Calendar на сервере

## Подготовка сервера

### 1. Обновление системы
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2. Установка Python 3.12
```bash
# Ubuntu/Debian
sudo apt install python3.12 python3.12-venv python3.12-dev python3-pip -y

# CentOS/RHEL
sudo yum install python3.12 python3.12-pip python3.12-devel -y
```

### 3. Установка дополнительных пакетов
```bash
# Ubuntu/Debian
sudo apt install git nginx supervisor postgresql postgresql-contrib -y

# CentOS/RHEL
sudo yum install git nginx supervisor postgresql postgresql-server postgresql-contrib -y
```

## Настройка базы данных PostgreSQL

### 1. Инициализация PostgreSQL
```bash
# CentOS/RHEL (если нужно)
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Создание базы данных и пользователя
```bash
sudo -u postgres psql
```

В PostgreSQL консоли:
```sql
CREATE DATABASE workcalendar_db;
CREATE USER workcalendar_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE workcalendar_db TO workcalendar_user;
ALTER USER workcalendar_user CREATEDB;
\q
```

## Развертывание приложения

### 1. Клонирование репозитория
```bash
cd /var/www/
sudo git clone https://github.com/DenDuet/nic_calendar_task.git workcalendar
sudo chown -R $USER:$USER /var/www/workcalendar
cd /var/www/workcalendar
```

### 2. Создание виртуального окружения
```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
```bash
cp .env.example .env  # если есть
nano .env
```

Содержимое `.env`:
```env
DEBUG=False
SECRET_KEY=your-very-secret-key-here
DATABASE_URL=postgresql://workcalendar_user:your_secure_password@localhost/workcalendar_db
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,server-ip
```

### 5. Настройка Django settings
```bash
nano workcalendar/settings.py
```

Обновите настройки:
```python
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'workcalendar_db',
        'USER': 'workcalendar_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### 6. Выполнение миграций
```bash
python manage.py migrate
```

### 7. Создание суперпользователя
```bash
python manage.py createsuperuser
```

### 8. Сбор статических файлов
```bash
python manage.py collectstatic --noinput
```

## Настройка Nginx

### 1. Создание конфигурации сайта
```bash
sudo nano /etc/nginx/sites-available/workcalendar
```

Содержимое конфигурации:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/workcalendar;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root /var/www/workcalendar;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/workcalendar/workcalendar.sock;
    }
}
```

### 2. Активация сайта
```bash
sudo ln -s /etc/nginx/sites-available/workcalendar /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## Настройка Gunicorn

### 1. Создание конфигурации Gunicorn
```bash
nano /var/www/workcalendar/gunicorn.conf.py
```

Содержимое:
```python
bind = "unix:/var/www/workcalendar/workcalendar.sock"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
user = "www-data"
group = "www-data"
daemon = False
pidfile = "/var/www/workcalendar/gunicorn.pid"
accesslog = "/var/www/workcalendar/logs/access.log"
errorlog = "/var/www/workcalendar/logs/error.log"
loglevel = "info"
```

### 2. Создание директории для логов
```bash
mkdir -p /var/www/workcalendar/logs
sudo chown -R www-data:www-data /var/www/workcalendar
```

## Настройка Supervisor

### 1. Создание конфигурации Supervisor
```bash
sudo nano /etc/supervisor/conf.d/workcalendar.conf
```

Содержимое:
```ini
[program:workcalendar]
command=/var/www/workcalendar/venv/bin/gunicorn --config /var/www/workcalendar/gunicorn.conf.py workcalendar.wsgi:application
directory=/var/www/workcalendar
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/workcalendar/logs/supervisor.log
```

### 2. Перезапуск Supervisor
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start workcalendar
```

## Настройка SSL (Let's Encrypt)

### 1. Установка Certbot
```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx -y

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx -y
```

### 2. Получение SSL сертификата
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Мониторинг и обслуживание

### 1. Проверка статуса сервисов
```bash
sudo systemctl status nginx
sudo supervisorctl status workcalendar
sudo systemctl status postgresql
```

### 2. Просмотр логов
```bash
# Логи приложения
tail -f /var/www/workcalendar/logs/error.log
tail -f /var/www/workcalendar/logs/access.log

# Логи Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Логи Supervisor
sudo tail -f /var/www/workcalendar/logs/supervisor.log
```

### 3. Обновление приложения
```bash
cd /var/www/workcalendar
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart workcalendar
```

## Бэкап и восстановление

### 1. Создание бэкапа базы данных
```bash
pg_dump -h localhost -U workcalendar_user workcalendar_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Восстановление из бэкапа
```bash
psql -h localhost -U workcalendar_user workcalendar_db < backup_file.sql
```

## Безопасность

### 1. Настройка файрвола
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Регулярные обновления
```bash
# Создание скрипта для автоматических обновлений
nano /var/www/workcalendar/update.sh
```

Содержимое скрипта:
```bash
#!/bin/bash
cd /var/www/workcalendar
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart workcalendar
echo "Update completed at $(date)"
```

```bash
chmod +x /var/www/workcalendar/update.sh
```

## Troubleshooting

### Частые проблемы:

1. **Ошибка 502 Bad Gateway**
   - Проверьте статус Gunicorn: `sudo supervisorctl status workcalendar`
   - Проверьте права доступа к сокету: `ls -la /var/www/workcalendar/workcalendar.sock`

2. **Ошибки статических файлов**
   - Убедитесь, что выполнили `python manage.py collectstatic`
   - Проверьте права доступа к директории staticfiles

3. **Ошибки базы данных**
   - Проверьте подключение к PostgreSQL
   - Убедитесь, что пользователь имеет права на базу данных

4. **Проблемы с правами доступа**
   ```bash
   sudo chown -R www-data:www-data /var/www/workcalendar
   sudo chmod -R 755 /var/www/workcalendar
   ```

## Полезные команды

```bash
# Перезапуск всех сервисов
sudo systemctl restart nginx postgresql
sudo supervisorctl restart workcalendar

# Проверка конфигурации Nginx
sudo nginx -t

# Просмотр активных соединений
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Мониторинг ресурсов
htop
df -h
free -h
```

Ваш проект Work Calendar теперь развернут на сервере и доступен по адресу `https://your-domain.com`!
