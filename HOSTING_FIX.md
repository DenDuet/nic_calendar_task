# Исправление проблем с хостингом

## Проблема: Очень старая версия pip (9.0.3)

### Решение 1: Обновление pip вручную

```bash
# 1. Скачайте get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# 2. Установите новую версию pip
python get-pip.py

# 3. Проверьте версию
pip --version
```

### Решение 2: Если curl недоступен

```bash
# 1. Создайте файл get-pip.py вручную
nano get-pip.py
```

Вставьте содержимое из: https://bootstrap.pypa.io/get-pip.py

```bash
# 2. Запустите установку
python get-pip.py
```

### Решение 3: Установка совместимых версий

Если обновление pip не работает, используйте старые версии:

```bash
# Установите Django 3.2 (последняя стабильная для старых систем)
pip install Django==3.2.25

# Установите остальные пакеты по одному
pip install asgiref==3.4.1
pip install sqlparse==0.4.4
pip install tzdata==2023.3
pip install pillow==10.0.1
pip install django-crispy-forms==2.1
pip install crispy-bootstrap5==2023.10
pip install djangorestframework==3.14.0
pip install python-dotenv==1.0.0
pip install gunicorn==21.2.0
```

## Пошаговая инструкция для вашего случая:

### Шаг 1: Обновите pip
```bash
cd ~/www/dhcwrk.online
source venv/bin/activate

# Попробуйте обновить pip
pip install --upgrade pip

# Если не работает, скачайте get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

### Шаг 2: Установите Django 3.2
```bash
pip install Django==3.2.25
```

### Шаг 3: Установите остальные пакеты
```bash
pip install -r requirements_old.txt
```

### Шаг 4: Создайте настройки для Django 3.2
```bash
nano workcalendar/settings_production.py
```

Содержимое для Django 3.2:
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

### Шаг 5: Примените миграции
```bash
python manage.py migrate --settings=workcalendar.settings_production
```

### Шаг 6: Создайте суперпользователя
```bash
python manage.py createsuperuser --settings=workcalendar.settings_production
```

### Шаг 7: Соберите статические файлы
```bash
python manage.py collectstatic --noinput --settings=workcalendar.settings_production
```

## Альтернативное решение: Минимальная установка

Если ничего не работает, установите только самое необходимое:

```bash
# Только Django и базовые пакеты
pip install Django==3.2.25
pip install pillow
pip install python-dotenv

# Проверьте, что Django работает
python manage.py --version
```

## Проверка работы

```bash
# Запустите тестовый сервер
python manage.py runserver 0.0.0.0:8000 --settings=workcalendar.settings_production
```

## Если все еще не работает

Попробуйте использовать системный Python без виртуального окружения:

```bash
# Деактивируйте venv
deactivate

# Установите пакеты глобально (если разрешено)
pip install Django==3.2.25
pip install pillow
pip install python-dotenv

# Запустите проект
python manage.py runserver --settings=workcalendar.settings_production
```

## Контакты поддержки хостинга

Если ничего не помогает, обратитесь в поддержку Reg.ru:
- https://www.reg.ru/support/
- Укажите, что нужна более новая версия pip или Python
