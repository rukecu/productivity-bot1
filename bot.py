import os
import telebot
from telebot import types
import datetime
from urllib.parse import urlparse
import json
import signal
import sys
import sqlite3

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
print(f"Токен получен: {'ЕСТЬ' if TOKEN else 'НЕТ'}")
if TOKEN:
    print(f"Длина токена: {len(TOKEN)}")

# Пытаемся импортировать psycopg2 для PostgreSQL
try:
    import psycopg2
except ImportError:
    psycopg2 = None

print("🤖 Токен получен...")
print("🚀 Запускаю бота...")

sys.stdout.flush()  



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

sys.stdout.flush()  
        return None

# Инициализация БД
def init_db():
    conn = get_db_connection()
    if conn is None:
        print("⚠️ Не удалось подключиться к БД, пропускаем инициализацию")
        
sys.stdout.flush()  
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

# ... остальной код без изменений ...

if __name__ == '__main__':
    print("🚀 Инициализирую БД...")
    
 
    init_db()
    print("🚀 Запускаю бота...")

    
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"❌ Ошибка в боте: {e}")
        
        import traceback
        traceback.print_exc()
