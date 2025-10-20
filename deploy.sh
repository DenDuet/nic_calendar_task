#!/bin/bash

# Скрипт автоматического развертывания Work Calendar
# Использование: ./deploy.sh [production|staging]

set -e

ENVIRONMENT=${1:-production}
PROJECT_DIR="/var/www/workcalendar"
BACKUP_DIR="/var/backups/workcalendar"
DATE=$(date +%Y%m%d_%H%M%S)

echo "🚀 Начинаем развертывание Work Calendar в окружении: $ENVIRONMENT"

# Создание бэкапа
echo "📦 Создание бэкапа..."
mkdir -p $BACKUP_DIR
if [ -d "$PROJECT_DIR" ]; then
    cp -r $PROJECT_DIR $BACKUP_DIR/backup_$DATE
    echo "✅ Бэкап создан: $BACKUP_DIR/backup_$DATE"
fi

# Переход в директорию проекта
cd $PROJECT_DIR

# Обновление кода из Git
echo "📥 Обновление кода из репозитория..."
git fetch origin
git reset --hard origin/main
echo "✅ Код обновлен"

# Активация виртуального окружения
echo "🐍 Активация виртуального окружения..."
source venv/bin/activate

# Обновление зависимостей
echo "📦 Обновление зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Зависимости обновлены"

# Применение миграций
echo "🗄️ Применение миграций базы данных..."
python manage.py migrate
echo "✅ Миграции применены"

# Сбор статических файлов
echo "📁 Сбор статических файлов..."
python manage.py collectstatic --noinput
echo "✅ Статические файлы собраны"

# Создание суперпользователя (если не существует)
echo "👤 Проверка суперпользователя..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print("Создание суперпользователя...")
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Суперпользователь создан: admin/admin123")
else:
    print("Суперпользователь уже существует")
EOF

# Перезапуск сервисов
echo "🔄 Перезапуск сервисов..."
sudo supervisorctl restart workcalendar
sudo systemctl reload nginx
echo "✅ Сервисы перезапущены"

# Проверка статуса
echo "🔍 Проверка статуса сервисов..."
sudo supervisorctl status workcalendar
sudo systemctl status nginx --no-pager -l

# Очистка старых бэкапов (оставляем только последние 5)
echo "🧹 Очистка старых бэкапов..."
cd $BACKUP_DIR
ls -t | tail -n +6 | xargs -r rm -rf
echo "✅ Старые бэкапы удалены"

echo "🎉 Развертывание завершено успешно!"
echo "📊 Статус сервисов:"
echo "   - Work Calendar: $(sudo supervisorctl status workcalendar | awk '{print $2}')"
echo "   - Nginx: $(sudo systemctl is-active nginx)"
echo "   - PostgreSQL: $(sudo systemctl is-active postgresql)"

# Отправка уведомления (опционально)
if command -v curl &> /dev/null; then
    echo "📧 Отправка уведомления о развертывании..."
    # Здесь можно добавить отправку уведомления в Slack, Telegram и т.д.
fi

echo "✨ Work Calendar успешно развернут в $ENVIRONMENT окружении!"
