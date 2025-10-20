#!/bin/bash

# Скрипт установки для MySQL
echo "🔧 Установка зависимостей для MySQL..."

# Активация виртуального окружения
source venv/bin/activate

echo "📦 Установка пакетов для MySQL..."

# Сначала попробуем установить mysqlclient
echo "Устанавливаем mysqlclient..."
pip install mysqlclient==2.1.1

# Если не получилось, попробуем PyMySQL
if [ $? -ne 0 ]; then
    echo "mysqlclient не установился, пробуем PyMySQL..."
    pip install PyMySQL==1.0.2
    # Добавляем PyMySQL в настройки
    echo "import pymysql" >> workcalendar/__init__.py
    echo "pymysql.install_as_MySQLdb()" >> workcalendar/__init__.py
fi

# Устанавливаем остальные пакеты
pip install -r requirements_mysql.txt

echo "✅ Установка завершена!"

# Проверка установки Django
echo "🔍 Проверка установки Django..."
python -c "import django; print('Django версия:', django.get_version())"

echo "🎉 Готово! Теперь можете запустить:"
echo "python manage.py migrate --settings=workcalendar.settings_mysql"
echo "python manage.py createsuperuser --settings=workcalendar.settings_mysql"
echo "python manage.py collectstatic --noinput --settings=workcalendar.settings_mysql"
echo "python manage.py runserver 0.0.0.0:8000 --settings=workcalendar.settings_mysql"
