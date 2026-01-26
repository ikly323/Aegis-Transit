#!/usr/bin/env python3
"""
run_api.py - Запуск REST API сервера для обработчика
"""

import uvicorn
from api import app

if __name__ == "__main__":
    print(f"""
    ⚙️  Sensor Processor API с Swagger
    🚀 Запускаю сервер на http://localhost:8001
    📚 Swagger документация: http://localhost:8001/docs
    📖 ReDoc документация: http://localhost:8001/redoc
    
    API Endpoints:
    - Обработать показание: POST /process
    - Получить результаты: GET /results
    - Статистика: GET /status
    - Проверка конфигурации: GET /config-check
    - Очередь на экспорт: GET /export-queue
    
    Пример запроса:
    curl -X POST http://localhost:8001/process \\
      -H "Content-Type: application/json" \\
      -d '{{"sensor_id": "001", "value": 30.0}}'
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)