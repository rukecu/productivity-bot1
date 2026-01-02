import os
import telebot
from telebot import types
import datetime
import psycopg2
from urllib.parse import urlparse
import json

# Конфигурация
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///bot.db')

bot = telebot.TeleBot(TOKEN)

# Подключение к базе данных
def get_db_connection():
    if DATABASE_URL.startswith('postgres://'):
        result = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
    else:
        # Fallback to SQLite
        import sqlite3
        conn = sqlite3.connect('bot.db')
    return conn

# Инициализация БД
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Для PostgreSQL
    if DATABASE_URL.startswith('postgres://'):
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
    cur.close()
    conn.close()

init_db()

# Сохранить данные дня
def save_day_data(user_id, date, data):
    conn = get_db_connection()
    cur = conn.cursor()
    
    total = (
        data.get('sleep_score', 0) +
        data.get('workout_score', 0) +
        data.get('wakeup_score', 0) +
        data.get('python_score', 0)
    )
    
    if DATABASE_URL.startswith('postgres://'):
        cur.execute('''
            INSERT INTO productivity 
            (user_id, date, sleep_hours, sleep_score, workout_type, workout_score,
             wakeup_time, wakeup_score, python_hours, python_score, total_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, date) DO UPDATE SET
            sleep_hours = EXCLUDED.sleep_hours,
            sleep_score = EXCLUDED.sleep_score,
            workout_type = EXCLUDED.workout_type,
            workout_score = EXCLUDED.workout_score,
            wakeup_time = EXCLUDED.wakeup_time,
            wakeup_score = EXCLUDED.wakeup_score,
            python_hours = EXCLUDED.python_hours,
            python_score = EXCLUDED.python_score,
            total_score = EXCLUDED.total_score
        ''', (
            user_id, date,
            data.get('sleep_hours', 0),
            data.get('sleep_score', 0),
            data.get('workout_type', ''),
            data.get('workout_score', 0),
            data.get('wakeup_time', ''),
            data.get('wakeup_score', 0),
            data.get('python_hours', 0),
            data.get('python_score', 0),
            total
        ))
    else:
        cur.execute('''
            INSERT OR REPLACE INTO productivity 
            (user_id, date, sleep_hours, sleep_score, workout_type, workout_score,
             wakeup_time, wakeup_score, python_hours, python_score, total_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, date,
            data.get('sleep_hours', 0),
            data.get('sleep_score', 0),
            data.get('workout_type', ''),
            data.get('workout_score', 0),
            data.get('wakeup_time', ''),
            data.get('wakeup_score', 0),
            data.get('python_hours', 0),
            data.get('python_score', 0),
            total
        ))
    
    conn.commit()
    cur.close()
    conn.close()

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    
    welcome = """
    🤖 *Productivity Tracker Bot*
    
    *Отслеживайте ежедневно:*
    🛌 Сон (7+ часов = 30%)
    🏃 Тренировка (25%)
    ☀️ Подъём до 10:00 (20%)
    🐍 Обучение Python (25%)
    
    *Максимальный КПД: 100%*
    
    Начните: /today
    """
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('📅 Сегодня', '📊 Статистика')
    markup.row('📈 Месяц', '⚙️ Настройки')
    
    bot.send_message(message.chat.id, welcome, 
                     parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['today'])
def today_command(message):
    user_id = message.from_user.id
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Создаём инлайн-клавиатуру
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Сон
    markup.add(
        types.InlineKeyboardButton("🛌 7+ ч (30%)", callback_data="sleep_30"),
        types.InlineKeyboardButton("🛌 6-7 ч (15%)", callback_data="sleep_15"),
        types.InlineKeyboardButton("🛌 <6 ч (0%)", callback_data="sleep_0")
    )
    
    # Тренировка
    markup.add(
        types.InlineKeyboardButton("🏃 Полная (25%)", callback_data="workout_25"),
        types.InlineKeyboardButton("🚶 Короткая (12.5%)", callback_data="workout_12"),
        types.InlineKeyboardButton("❌ Нет (0%)", callback_data="workout_0")
    )
    
    # Подъём
    markup.add(
        types.InlineKeyboardButton("☀️ До 10:00 (20%)", callback_data="wakeup_20"),
        types.InlineKeyboardButton("⏰ 10-11:00 (10%)", callback_data="wakeup_10"),
        types.InlineKeyboardButton("🌙 После 11:00 (0%)", callback_data="wakeup_0")
    )
    
    # Python
    markup.add(
        types.InlineKeyboardButton("🐍 1+ ч (25%)", callback_data="python_25"),
        types.InlineKeyboardButton("📚 30-60 мин (15%)", callback_data="python_15"),
        types.InlineKeyboardButton("📖 Теория (5%)", callback_data="python_5"),
        types.InlineKeyboardButton("❌ Нет (0%)", callback_data="python_0")
    )
    
    markup.add(types.InlineKeyboardButton("✅ Рассчитать КПД", callback_data="calculate"))
    
    bot.send_message(
        message.chat.id,
        f"📅 *{datetime.datetime.now().strftime('%d.%m.%Y')}*\n\n"
        "Выберите выполненные задачи:\n\n"
        "🛌 *Сон:* 7+ ч = 30% | 6-7 ч = 15% | <6 ч = 0%\n"
        "🏃 *Тренировка:* Полная = 25% | Короткая = 12.5% | Нет = 0%\n"
        "☀️ *Подъём:* До 10:00 = 20% | 10-11:00 = 10% | После 11:00 = 0%\n"
        "🐍 *Python:* 1+ ч = 25% | 30-60 мин = 15% | Теория = 5% | Нет = 0%",
        parse_mode='Markdown',
        reply_markup=markup
    )

# Временное хранилище для данных
user_temp_data = {}

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    
    if user_id not in user_temp_data:
        user_temp_data[user_id] = {
            'sleep_score': 0,
            'workout_score': 0,
            'wakeup_score': 0,
            'python_score': 0,
            'sleep_hours': 0,
            'workout_type': '',
            'wakeup_time': '',
            'python_hours': 0
        }
    
    if data.startswith('sleep_'):
        score = int(data.split('_')[1])
        user_temp_data[user_id]['sleep_score'] = score
        user_temp_data[user_id]['sleep_hours'] = 7.5 if score == 30 else 6.5 if score == 15 else 5.5
        bot.answer_callback_query(call.id, f"Сон: {score}%")
        
    elif data.startswith('workout_'):
        score = float(data.split('_')[1])
        user_temp_data[user_id]['workout_score'] = score
        user_temp_data[user_id]['workout_type'] = 'full' if score == 25 else 'short' if score == 12 else 'none'
        bot.answer_callback_query(call.id, f"Тренировка: {score}%")
        
    elif data.startswith('wakeup_'):
        score = int(data.split('_')[1])
        user_temp_data[user_id]['wakeup_score'] = score
        user_temp_data[user_id]['wakeup_time'] = 'early' if score == 20 else 'medium' if score == 10 else 'late'
        bot.answer_callback_query(call.id, f"Подъём: {score}%")
        
    elif data.startswith('python_'):
        score = int(data.split('_')[1])
        user_temp_data[user_id]['python_score'] = score
        user_temp_data[user_id]['python_hours'] = 1.5 if score == 25 else 0.75 if score == 15 else 0.25 if score == 5 else 0
        bot.answer_callback_query(call.id, f"Python: {score}%")
        
    elif data == 'calculate':
        user_data = user_temp_data.get(user_id, {})
        total = (
            user_data.get('sleep_score', 0) +
            user_data.get('workout_score', 0) +
            user_data.get('wakeup_score', 0) +
            user_data.get('python_score', 0)
        )
        
        # Сохраняем в БД
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        save_day_data(user_id, today, user_data)
        
        # Формируем результат
        result = f"""
📊 *КПД дня: {total}%*

🛌 Сон: {user_data.get('sleep_score', 0)}%
🏃 Тренировка: {user_data.get('workout_score', 0)}%
☀️ Подъём: {user_data.get('wakeup_score', 0)}%
🐍 Python: {user_data.get('python_score', 0)}%

{'🏆 *ИДЕАЛЬНЫЙ ДЕНЬ!*' if total == 100 else 
 '✅ *Отлично!*' if total >= 70 else 
 '👍 *Хорошо!*' if total >= 50 else 
 '💪 *Завтра лучше!*'}
        """
        
        bot.edit_message_text(
            result,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = message.from_user.id
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    if DATABASE_URL.startswith('postgres://'):
        cur.execute('''
            SELECT 
                COUNT(*) as days_count,
                AVG(total_score) as avg_score,
                COUNT(CASE WHEN total_score = 100 THEN 1 END) as perfect_days,
                COUNT(CASE WHEN total_score >= 70 THEN 1 END) as good_days
            FROM productivity 
            WHERE user_id = %s
        ''', (user_id,))
    else:
        cur.execute('''
            SELECT 
                COUNT(*) as days_count,
                AVG(total_score) as avg_score,
                COUNT(CASE WHEN total_score = 100 THEN 1 END) as perfect_days,
                COUNT(CASE WHEN total_score >= 70 THEN 1 END) as good_days
            FROM productivity 
            WHERE user_id = ?
        ''', (user_id,))
    
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if row and row[0] > 0:
        days_count = row[0]
        avg_score = round(row[1] or 0, 1)
        perfect_days = row[2] or 0
        good_days = row[3] or 0
        
        stats = f"""
📈 *Ваша статистика:*

📅 Отслежено дней: *{days_count}*
📊 Средний КПД: *{avg_score}%*
🏆 Идеальных дней: *{perfect_days}*
✅ Хороших дней (≥70%): *{good_days}*

*Советы для улучшения:*
1. Спите 7+ часов каждый день
2. Тренируйтесь через день
3. Вставайте до 10:00
4. Уделяйте Python минимум 1 час
        """
    else:
        stats = "📊 У вас пока нет данных. Начните с команды /today"
    
    bot.send_message(message.chat.id, stats, parse_mode='Markdown')

@bot.message_handler(commands=['month'])
def month_command(message):
    # Простая текстовая таблица
    table = """
📅 *Таблица продуктивности:*

День | 🛌 | 🏃 | ☀️ | 🐍 | КПД
-----|----|----|----|----|----
 1   | 🟢 | 🏃 | ☀️ | 🐍 | 85%
 2   | 🟡 | ❌ | ⏰ | 📚 | 40%
 3   | 🟢 | 🚶 | ☀️ | 🐍 | 72%
 4   | ⚫ | 🏃 | 🌙 | ❌ | 25%
 5   | 🟢 | ❌ | ☀️ | 📖 | 55%
 6   | 🟡 | 🏃 | ☀️ | 🐍 | 82%
 7   | 🟢 | 🚶 | ⏰ | 🐍 | 67%

📊 *Средний КПД: 60%*
🏆 *Идеальных дней: 1*
✅ *Хороших дней: 3*

*Легенда:*
🟢 = 7+ ч сна | 🟡 = 6-7 ч | ⚫ = <6 ч
🏃 = Полная | 🚶 = Короткая | ❌ = Нет
☀️ = До 10:00 | ⏰ = 10-11:00 | 🌙 = После 11:00
🐍 = 1+ ч | 📚 = 30-60 мин | 📖 = Теория
    """
    
    bot.send_message(message.chat.id, table, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == '📅 Сегодня')
def today_button(message):
    today_command(message)

@bot.message_handler(func=lambda m: m.text == '📊 Статистика')
def stats_button(message):
    stats_command(message)

@bot.message_handler(func=lambda m: m.text == '📈 Месяц')
def month_button(message):
    month_command(message)

@bot.message_handler(func=lambda m: m.text == '⚙️ Настройки')
def settings_button(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🔔 Напоминания", callback_data="settings_reminders"),
        types.InlineKeyboardButton("🌐 Часовой пояс", callback_data="settings_timezone"),
        types.InlineKeyboardButton("🗑️ Очистить данные", callback_data="settings_clear")
    )
    
    bot.send_message(
        message.chat.id,
        "⚙️ *Настройки бота:*\n\n"
        "Вы можете настроить:\n"
        "• Уведомления и напоминания\n"
        "• Часовой пояс\n"
        "• Очистку данных\n"
        "• Язык интерфейса",
        parse_mode='Markdown',
        reply_markup=markup
    )

if __name__ == '__main__':
    import sys
    # Если бота запускают отдельно (для тестов)
    if len(sys.argv) > 1 and sys.argv[1] == '--bot-only':
        print("🤖 Запускаю только бота...")
        bot.polling(none_stop=True)
    else:
        # Режим для совместного запуска с веб-сервером
        print("🤖 Бот запущен в фоновом режиме...")
        from threading import Thread
        bot_thread = Thread(target=bot.polling, kwargs={'none_stop': True})
        bot_thread.daemon = True  # Поток завершится с основным процессом
        bot_thread.start()
