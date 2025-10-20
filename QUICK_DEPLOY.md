# Быстрое развертывание Work Calendar

## Минимальная установка (5 минут)

### 1. Подготовка сервера
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y python3.12 python3.12-venv python3-pip git nginx postgresql postgresql-contrib supervisor

# CentOS/RHEL
sudo yum update -y && sudo yum install -y python3.12 python3-pip git nginx postgresql postgresql-server postgresql-contrib supervisor
```

### 2. Настройка базы данных
```bash
sudo -u postgres psql -c "CREATE DATABASE workcalendar_db;"
sudo -u postgres psql -c "CREATE USER workcalendar_user WITH PASSWORD 'secure123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE workcalendar_db TO workcalendar_user;"
```

### 3. Развертывание приложения
```bash
cd /var/www/
sudo git clone https://github.com/DenDuet/nic_calendar_task.git workcalendar
sudo chown -R $USER:$USER workcalendar
cd workcalendar

# Создание виртуального окружения
python3.12 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Настройка базы данных
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 4. Настройка Nginx
```bash
sudo tee /etc/nginx/sites-available/workcalendar > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    location /static/ {
        root /var/www/workcalendar;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/workcalendar/workcalendar.sock;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/workcalendar /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
```

### 5. Настройка Gunicorn
```bash
sudo tee /etc/supervisor/conf.d/workcalendar.conf > /dev/null <<EOF
[program:workcalendar]
command=/var/www/workcalendar/venv/bin/gunicorn --bind unix:/var/www/workcalendar/workcalendar.sock workcalendar.wsgi:application
directory=/var/www/workcalendar
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/workcalendar.log
EOF

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start workcalendar
```

### 6. Проверка
```bash
curl http://localhost
```

## Автоматическое развертывание

Используйте готовый скрипт:
```bash
cd /var/www/workcalendar
chmod +x deploy.sh
./deploy.sh production
```

## Обновление приложения

```bash
cd /var/www/workcalendar
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart workcalendar
```

## Полезные команды

```bash
# Статус сервисов
sudo supervisorctl status workcalendar
sudo systemctl status nginx

# Логи
sudo tail -f /var/log/workcalendar.log
sudo tail -f /var/log/nginx/error.log

# Перезапуск
sudo supervisorctl restart workcalendar
sudo systemctl restart nginx
```

## SSL сертификат (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

Готово! Ваш календарь задач доступен по адресу сервера.
