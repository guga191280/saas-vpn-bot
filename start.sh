#!/bin/bash
# Запускаем веб-сервер в фоновом режиме
python3 server.py &
# Запускаем бота
python3 bot.py
