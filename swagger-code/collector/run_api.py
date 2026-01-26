#!/usr/bin/env python3
"""
run_api.py - Запуск REST API сервера
"""

import uvicorn
from api import app

if __name__ == "__main__":
    print(f"""
    🌐 Sensor Data Collector API с Swagger
    🚀 Запускаю сервер на http://localhost:8000
    📚 Swagger документация: http://localhost:8000/docs
    📖 ReDoc документация: http://localhost:8000/redoc
    
    Доступные команды:
    - Получить все датчики: curl http://localhost:8000/sensors
    - Получить один датчик: curl http://localhost:8000/sensors/temp_sensor_1
    - Обновить данные: curl -X POST http://localhost:8000/refresh
    - Проверить здоровье: curl http://localhost:8000/health
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
