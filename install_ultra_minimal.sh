#!/bin/bash

# Скрипт ультра минимальной установки
echo "🔧 Ультра минимальная установка зависимостей..."

# Активация виртуального окружения
source venv/bin/activate

echo "📦 Установка ультра минимальных пакетов..."
pip install -r requirements_ultra_minimal.txt

echo "✅ Установка завершена!"

# Проверка установки Django
echo "🔍 Проверка установки Django..."
python -c "import django; print('Django версия:', django.get_version())"

echo "🎉 Готово! Теперь можете запустить:"
echo "python manage.py migrate --settings=workcalendar.settings_minimal"
echo "python manage.py createsuperuser --settings=workcalendar.settings_minimal"
echo "python manage.py collectstatic --noinput --settings=workcalendar.settings_minimal"
echo "python manage.py runserver 0.0.0.0:8000 --settings=workcalendar.settings_minimal"
