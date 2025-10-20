#!/bin/bash

# Скрипт установки для SQLite (без PostgreSQL)
echo "🔧 Установка зависимостей для SQLite..."

# Активация виртуального окружения
source venv/bin/activate

echo "📦 Установка пакетов без PostgreSQL..."
pip install -r requirements_sqlite.txt

echo "✅ Установка завершена!"

# Проверка установки Django
echo "🔍 Проверка установки Django..."
python -c "import django; print('Django версия:', django.get_version())"

echo "🎉 Готово! Теперь можете запустить:"
echo "python manage.py migrate --settings=workcalendar.settings_sqlite"
echo "python manage.py createsuperuser --settings=workcalendar.settings_sqlite"
echo "python manage.py collectstatic --noinput --settings=workcalendar.settings_sqlite"
echo "python manage.py runserver 0.0.0.0:8000 --settings=workcalendar.settings_sqlite"
