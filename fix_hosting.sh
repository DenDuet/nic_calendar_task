#!/bin/bash

# Скрипт исправления проблем с хостингом
echo "🔧 Исправление проблем с хостингом..."

# Активация виртуального окружения
source venv/bin/activate

echo "📦 Попытка обновления pip..."
pip install --upgrade pip

# Проверка версии pip
PIP_VERSION=$(pip --version | grep -o '[0-9]\+\.[0-9]\+')
echo "Версия pip: $PIP_VERSION"

# Если pip все еще старая версия, попробуем обновить вручную
if [[ "$PIP_VERSION" < "20.0" ]]; then
    echo "⚠️ Pip слишком старая версия, пытаемся обновить вручную..."
    
    # Скачиваем get-pip.py
    if command -v curl &> /dev/null; then
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    else
        echo "❌ curl недоступен, создайте get-pip.py вручную"
        echo "Скачайте содержимое с: https://bootstrap.pypa.io/get-pip.py"
        exit 1
    fi
    
    # Устанавливаем новую версию pip
    python get-pip.py
    rm get-pip.py
fi

echo "📦 Установка Django 3.2.25..."
pip install Django==3.2.25

echo "📦 Установка остальных пакетов..."
pip install asgiref==3.4.1
pip install sqlparse==0.4.4
pip install tzdata==2023.3
pip install pillow==10.0.1
pip install django-crispy-forms==2.1
pip install crispy-bootstrap5==2023.10
pip install djangorestframework==3.14.0
pip install python-dotenv==1.0.0
pip install gunicorn==21.2.0

echo "✅ Установка завершена!"

# Проверка установки Django
echo "🔍 Проверка установки Django..."
python -c "import django; print('Django версия:', django.get_version())"

echo "🎉 Готово! Теперь можете запустить:"
echo "python manage.py migrate --settings=workcalendar.settings_production"
echo "python manage.py createsuperuser --settings=workcalendar.settings_production"
echo "python manage.py collectstatic --noinput --settings=workcalendar.settings_production"
