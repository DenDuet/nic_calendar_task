# Развертывание на виртуальном хостинге (Reg.ru и аналоги)

## Особенности виртуального хостинга:
- Нет прав sudo
- Ограниченные версии Python
- Предустановленное ПО
- Ограниченные права доступа

## Пошаговая инструкция:

### 1. Подключение к серверу
```bash
ssh u2976163@server134.dhcwrk.online
```

### 2. Переход в директорию сайта
```bash
cd ~/www/dhcwrk.online
```

### 3. Клонирование проекта
```bash
git clone https://github.com/DenDuet/nic_calendar_task.git .
```

### 4. Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate
```

### 5. Обновление pip
```bash
pip install --upgrade pip
```

### 6. Установка зависимостей (совместимых с Python 3.10)
```bash
pip install -r requirements_python310.txt
```

### 7. Настройка базы данных
Создайте файл `.env` в корне проекта:
```bash
nano .env
```

Содержимое `.env`:
```env
DEBUG=False
SECRET_KEY=your-very-secret-key-here
ALLOWED_HOSTS=dhcwrk.online,www.dhcwrk.online
DATABASE_URL=sqlite:///db.sqlite3
```

### 8. Настройка Django settings
Создайте файл `workcalendar/settings_production.py`:
```bash
nano workcalendar/settings_production.py
```

Содержимое:
```python
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
```

### 9. Применение миграций
```bash
python manage.py migrate --settings=workcalendar.settings_production
```

### 10. Создание суперпользователя
```bash
python manage.py createsuperuser --settings=workcalendar.settings_production
```

### 11. Сбор статических файлов
```bash
python manage.py collectstatic --noinput --settings=workcalendar.settings_production
```

### 12. Настройка WSGI
Создайте файл `wsgi.py` в корне проекта:
```bash
nano wsgi.py
```

Содержимое:
```python
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
```

### 13. Настройка .htaccess (если Apache)
Создайте файл `.htaccess`:
```bash
nano .htaccess
```

Содержимое:
```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ wsgi.py/$1 [QSA,L]

# Static files
RewriteRule ^static/(.*)$ staticfiles/$1 [L]
RewriteRule ^media/(.*)$ media/$1 [L]
```

### 14. Проверка работы
```bash
python manage.py runserver 0.0.0.0:8000 --settings=workcalendar.settings_production
```

## Альтернативный способ (если WSGI не работает):

### Использование FastCGI
Создайте файл `fcgi.py`:
```python
#!/home/u2976163/www/dhcwrk.online/venv/bin/python
import os
import sys

sys.path.insert(0, '/home/u2976163/www/dhcwrk.online')
os.environ['DJANGO_SETTINGS_MODULE'] = 'workcalendar.settings_production'

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
```

## Полезные команды:

```bash
# Активация виртуального окружения
source venv/bin/activate

# Деактивация
deactivate

# Проверка версии Python
python --version

# Проверка установленных пакетов
pip list

# Просмотр логов (если доступно)
tail -f /var/log/apache2/error.log
```

## Troubleshooting:

### Если не работает WSGI:
1. Проверьте права доступа к файлам
2. Убедитесь, что виртуальное окружение активировано
3. Проверьте пути в wsgi.py

### Если ошибки с базой данных:
1. Убедитесь, что файл db.sqlite3 создан
2. Проверьте права доступа к директории

### Если не загружаются статические файлы:
1. Проверьте настройки STATIC_ROOT
2. Убедитесь, что collectstatic выполнен
3. Проверьте .htaccess правила

## Контакты поддержки:
- Reg.ru Support: https://www.reg.ru/support/
- Документация хостинга: https://www.reg.ru/support/hosting/
