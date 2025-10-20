#!/bin/bash

# Скрипт развертывания для виртуального хостинга
# Использование: ./deploy_hosting.sh

set -e

echo "🚀 Развертывание Work Calendar на виртуальном хостинге..."

# Проверка, что мы в правильной директории
if [ ! -f "manage.py" ]; then
    echo "❌ Ошибка: manage.py не найден. Убедитесь, что вы в корне проекта."
    exit 1
fi

# Создание виртуального окружения (если не существует)
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python -m venv venv
fi

# Активация виртуального окружения
echo "🐍 Активация виртуального окружения..."
source venv/bin/activate

# Обновление pip
echo "⬆️ Обновление pip..."
pip install --upgrade pip

# Установка зависимостей
echo "📦 Установка зависимостей..."
if [ -f "requirements_python310.txt" ]; then
    pip install -r requirements_python310.txt
else
    echo "⚠️ requirements_python310.txt не найден, используем requirements.txt"
    pip install -r requirements.txt
fi

# Создание .env файла (если не существует)
if [ ! -f ".env" ]; then
    echo "⚙️ Создание .env файла..."
    cat > .env << EOF
DEBUG=False
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=dhcwrk.online,www.dhcwrk.online
DATABASE_URL=sqlite:///db.sqlite3
EOF
    echo "✅ .env файл создан"
fi

# Создание production settings (если не существует)
if [ ! -f "workcalendar/settings_production.py" ]; then
    echo "⚙️ Создание production settings..."
    cat > workcalendar/settings_production.py << 'EOF'
import os
from .settings import *

# Production settings
DEBUG = False
ALLOWED_HOSTS = ['dhcwrk.online', 'www.dhcwrk.online']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
EOF
    echo "✅ Production settings созданы"
fi

# Применение миграций
echo "🗄️ Применение миграций..."
python manage.py migrate --settings=workcalendar.settings_production

# Создание суперпользователя (если не существует)
echo "👤 Проверка суперпользователя..."
python manage.py shell --settings=workcalendar.settings_production << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print("Создание суперпользователя...")
    User.objects.create_superuser('admin', 'admin@dhcwrk.online', 'admin123')
    print("Суперпользователь создан: admin/admin123")
else:
    print("Суперпользователь уже существует")
EOF

# Сбор статических файлов
echo "📁 Сбор статических файлов..."
python manage.py collectstatic --noinput --settings=workcalendar.settings_production

# Создание wsgi.py (если не существует)
if [ ! -f "wsgi.py" ]; then
    echo "⚙️ Создание wsgi.py..."
    cat > wsgi.py << 'EOF'
import os
import sys
import site

# Add the project directory to the Python path
sys.path.insert(0, '/home/u2976163/www/dhcwrk.online')

# Add the virtual environment's site-packages directory
site.addsitedir('/home/u2976163/www/dhcwrk.online/venv/lib/python3.10/site-packages')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workcalendar.settings_production')

# Import Django's WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
EOF
    echo "✅ wsgi.py создан"
fi

# Создание .htaccess (если не существует)
if [ ! -f ".htaccess" ]; then
    echo "⚙️ Создание .htaccess..."
    cat > .htaccess << 'EOF'
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ wsgi.py/$1 [QSA,L]

# Static files
RewriteRule ^static/(.*)$ staticfiles/$1 [L]
RewriteRule ^media/(.*)$ media/$1 [L]
EOF
    echo "✅ .htaccess создан"
fi

echo "🎉 Развертывание завершено!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Проверьте работу сайта: https://dhcwrk.online"
echo "2. Войдите в админку: https://dhcwrk.online/admin (admin/admin123)"
echo "3. Перейдите к календарю: https://dhcwrk.online/calendar/"
echo ""
echo "🔧 Полезные команды:"
echo "- Активация venv: source venv/bin/activate"
echo "- Запуск сервера: python manage.py runserver --settings=workcalendar.settings_production"
echo "- Создание миграций: python manage.py makemigrations --settings=workcalendar.settings_production"
echo "- Применение миграций: python manage.py migrate --settings=workcalendar.settings_production"
