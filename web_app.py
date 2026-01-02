from flask import Flask, render_template_string, jsonify
import os
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Productivity Bot Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: white;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            color: #333;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 20px;
            font-size: 2.5em;
        }
        .status {
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
            font-size: 1.2em;
        }
        .card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            border: 2px solid #e9ecef;
        }
        .btn {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border-radius: 10px;
            text-decoration: none;
            font-weight: bold;
            margin: 10px 5px;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #764ba2;
            transform: translateY(-2px);
        }
        .emoji-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 20px 0;
        }
        .emoji-item {
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 10px;
            border: 2px solid #ddd;
        }
        .emoji { font-size: 2em; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 20px 0;
        }
        .stat-item {
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 10px;
            border: 2px solid #ddd;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        @media (max-width: 600px) {
            .emoji-grid, .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            h1 { font-size: 2em; }
            .container { padding: 15px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Productivity Bot</h1>
        
        <div class="status">
            🟢 Бот работает | Пользователей: {{ users_count }}
        </div>
        
        <div class="card">
            <h2>🚀 Быстрый старт</h2>
            <p>1. Найдите бота в Telegram: <strong>@{{ bot_username }}</strong></p>
            <p>2. Отправьте команду: <code>/start</code></p>
            <p>3. Нажмите "📅 Сегодня"</p>
            <p>4. Отмечайте выполненные задачи</p>
        </div>
        
        <div class="emoji-grid">
            <div class="emoji-item">
                <div class="emoji">🛌</div>
                <div>Сон 7+ часов</div>
                <small>30%</small>
            </div>
            <div class="emoji-item">
                <div class="emoji">🏃</div>
                <div>Тренировка</div>
                <small>25%</small>
            </div>
            <div class="emoji-item">
                <div class="emoji">☀️</div>
                <div>Подъём до 10:00</div>
                <small>20%</small>
            </div>
            <div class="emoji-item">
                <div class="emoji">🐍</div>
                <div>Python 1+ час</div>
                <small>25%</small>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-item">
                <div>📊 Максимальный КПД</div>
                <div class="stat-value">100%</div>
            </div>
            <div class="stat-item">
                <div>📅 Дней отслежено</div>
                <div class="stat-value">{{ days_count }}</div>
            </div>
            <div class="stat-item">
                <div>🏆 Идеальных дней</div>
                <div class="stat-value">{{ perfect_days }}</div>
            </div>
            <div class="stat-item">
                <div>✅ Средний КПД</div>
                <div class="stat-value">{{ avg_score }}%</div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://t.me/{{ bot_username }}" class="btn" target="_blank">
                🤖 Открыть в Telegram
            </a>
            <a href="/api/stats" class="btn" style="background: #4CAF50;">
                📊 API Статистика
            </a>
            <a href="/health" class="btn" style="background: #FF9800;">
                🏥 Health Check
            </a>
        </div>
        
        <div class="card">
            <h3>📞 Поддержка</h3>
            <p>Проблемы с ботом? Проверьте:</p>
            <ol>
                <li>Токен бота в переменных окружения</li>
                <li>Подключение к базе данных</li>
                <li>Логи в Render Dashboard</li>
            </ol>
        </div>
        
        <footer style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666;">
            <p>🚀 Развернуто на Render | Python + Flask + PostgreSQL</p>
            <p>Обновлено: {{ updated_at }}</p>
        </footer>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, 
        bot_username=os.environ.get('BOT_USERNAME', 'ProductivityTrackerBot'),
        users_count=100,
        days_count=50,
        perfect_days=10,
        avg_score=65,
        updated_at='Сегодня'
    )

@app.route('/api/stats')
def api_stats():
    return jsonify({
        'status': 'running',
        'service': 'productivity-bot',
        'version': '1.0.0',
        'database': 'connected',
        'uptime': '24h'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
