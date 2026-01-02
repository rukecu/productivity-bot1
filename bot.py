import os
import telebot
from telebot import types
import datetime
from urllib.parse import urlparse
import sys
import sqlite3
import time  # <-- ДОБАВИТЬ

# Пытаемся импортировать psycopg2 для PostgreSQL
try:
    import psycopg2
except ImportError:
    psycopg2 = None

# Конфигурация
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///bot.db')

if not TOKEN:
    print("❌ ОШИБКА: TELEGRAM_BOT_TOKEN не установлен!")
    sys.exit(1)

print(f"🤖 Токен получен, длина: {len(TOKEN)} символов")
print(f"📦 DATABASE_URL: {DATABASE_URL[:20]}...")

bot = telebot.TeleBot(TOKEN)

# Подключение к базе данных
def get_db_connection():
    try:
        if DATABASE_URL.startswith('postgres://') and psycopg2:
            result = urlparse(DATABASE_URL)
            conn = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port
            )
            print("✅ Подключено к PostgreSQL")
        else:
            # Fallback to SQLite
            conn = sqlite3.connect('bot.db', check_same_thread=False)
            print("✅ Подключено к SQLite")
        return conn
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return None

# Инициализация БД
def init_db():
    conn = get_db_connection()
    if conn is None:
        print("⚠️ Не удалось подключиться к БД, пропускаем инициализацию")
        return
    
    cur = conn.cursor()
    
    try:
        # Для PostgreSQL
        if DATABASE_URL.startswith('postgres://') and psycopg2:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS productivity (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    date DATE,
                    sleep_hours FLOAT DEFAULT 0,
                    sleep_score INTEGER DEFAULT 0,
                    workout_type TEXT,
                    workout_score INTEGER DEFAULT 0,
                    wakeup_time TEXT,
                    wakeup_score INTEGER DEFAULT 0,
                    python_hours FLOAT DEFAULT 0,
                    python_score INTEGER DEFAULT 0,
                    total_score INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            # Для SQLite
            cur.execute('''
                CREATE TABLE IF NOT EXISTS productivity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date TEXT,
                    sleep_hours REAL DEFAULT 0,
                    sleep_score INTEGER DEFAULT 0,
                    workout_type TEXT,
                    workout_score INTEGER DEFAULT 0,
                    wakeup_time TEXT,
                    wakeup_score INTEGER DEFAULT 0,
                    python_hours REAL DEFAULT 0,
                    python_score INTEGER DEFAULT 0,
                    total_score INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        conn.commit()
        print("✅ Таблица создана/проверена")
    except Exception as e:
        print(f"❌ Ошибка при создании таблицы: {e}")
    finally:
        cur.close()
        conn.close()

# ... ВСТАВЬТЕ СЮДА ВСЕ ВАШИ ОБРАБОТЧИКИ КОМАНД (@bot.message_handler) ...

if __name__ == '__main__':
    print("🚀 Инициализирую БД...")
    init_db()
    print("🚀 Запускаю бота...")
    
    try:
        # Пробуем polling, если ошибка 409 — ждём и пробуем ещё
        for attempt in range(3):
            try:
                bot.polling(none_stop=True, interval=1, timeout=30, skip_pending=True)
                break
            except Exception as e:
                if "409" in str(e):
                    print(f"⚠️ Конфликт (попытка {attempt+1}/3), жду 10 секунд...")
                    time.sleep(10)
                else:
                    raise
    except Exception as e:
        print(f"❌ Ошибка в боте: {e}")
        import traceback
        traceback.print_exc()
    
    # Держим процесс активным
    print("🔄 Бот работает...")
    while True:
        time.sleep(3600)  # Спим 1 час

from flask import Flask
from threading import Thread

# Веб-сервер для проверки здоровья
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is alive!"

def run_web():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Запускаем веб-сервер в отдельном потоке
    web_thread = Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()
    
    print("🚀 Инициализирую БД...")
    init_db()
    print("🚀 Запускаю бота...")
    bot.polling(none_stop=True, skip_pending=True)
