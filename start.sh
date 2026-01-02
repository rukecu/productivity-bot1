#!/bin/bash
# Запускаем бота в фоне и веб-сервер на переднем плане
python bot.py & gunicorn web_app:app --bind 0.0.0.0:$PORT
