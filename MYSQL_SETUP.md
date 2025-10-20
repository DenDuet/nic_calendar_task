# Настройка MySQL для проекта

## 🔧 **Настройка базы данных MySQL**

### **1. Создание базы данных**

Войдите в панель управления хостингом (cPanel) и создайте базу данных:

```sql
-- Создайте базу данных
CREATE DATABASE u2976163_dhcwrk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Создайте пользователя (если нужно)
CREATE USER 'u2976163_dhcwrk'@'localhost' IDENTIFIED BY 'your_strong_password';

-- Дайте права пользователю
GRANT ALL PRIVILEGES ON u2976163_dhcwrk.* TO 'u2976163_dhcwrk'@'localhost';
FLUSH PRIVILEGES;
```

### **2. Настройка файла settings_mysql.py**

Отредактируйте файл `workcalendar/settings_mysql.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'u2976163_dhcwrk',  # Ваше имя базы данных
        'USER': 'u2976163_dhcwrk',  # Ваш пользователь
        'PASSWORD': 'your_actual_password',  # Ваш пароль
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

### **3. Установка зависимостей**

```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Установите пакеты
pip install -r requirements_mysql.txt

# Если mysqlclient не установился, используйте PyMySQL
pip install PyMySQL==1.0.2
```

### **4. Настройка PyMySQL (если mysqlclient не работает)**

Добавьте в файл `workcalendar/__init__.py`:

```python
import pymysql
pymysql.install_as_MySQLdb()
```

### **5. Применение миграций**

```bash
# Примените миграции
python manage.py migrate --settings=workcalendar.settings_mysql

# Создайте суперпользователя
python manage.py createsuperuser --settings=workcalendar.settings_mysql

# Соберите статические файлы
python manage.py collectstatic --noinput --settings=workcalendar.settings_mysql
```

### **6. Запуск сервера**

```bash
# Запустите сервер
python manage.py runserver 0.0.0.0:8000 --settings=workcalendar.settings_mysql
```

## 🔍 **Проверка подключения к MySQL**

```bash
# Проверьте подключение
python manage.py dbshell --settings=workcalendar.settings_mysql
```

## 📋 **Альтернативные варианты**

### **Вариант 1: Использование SQLite (проще)**

Если MySQL не работает, используйте SQLite:

```bash
pip install -r requirements_sqlite.txt
python manage.py migrate --settings=workcalendar.settings_sqlite
```

### **Вариант 2: Использование PyMySQL**

```bash
pip install PyMySQL==1.0.2
# Добавьте в workcalendar/__init__.py:
# import pymysql
# pymysql.install_as_MySQLdb()
```

## 🚨 **Возможные проблемы**

1. **Ошибка "mysqlclient not found"** - используйте PyMySQL
2. **Ошибка подключения** - проверьте данные в settings_mysql.py
3. **Ошибка прав доступа** - проверьте права пользователя в MySQL

## 📞 **Поддержка**

Если возникнут проблемы, обратитесь в поддержку хостинга для настройки MySQL.
