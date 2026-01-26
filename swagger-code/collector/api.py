from fastapi import FastAPI, HTTPException, Query
from datetime import datetime

# Импортируем ваш класс из collector.py
from collector import SensorDataCollector

# Конфигурация
NODE_URL = "http://127.0.0.1:6862"
CONTRACT_ID = "test_contract_123"

# Создаем экземпляр вашего коллектора
collector = SensorDataCollector(NODE_URL, CONTRACT_ID)

# Создаем FastAPI приложение
app = FastAPI(
    title="Sensor Data Collector API",
    description="API для получения конфигураций датчиков из блокчейна",
    version="1.0.0"
)

@app.get("/", 
         summary="Информация о API",
         description="Корневой эндпоинт с основной информацией")
async def root():
    return {
        "service": "Sensor Data Collector API",
        "version": "1.0.0",
        "description": "Сервис для извлечения конфигураций датчиков из блокчейн-контракта",
        "endpoints": {
            "/sensors": "GET - получить все датчики",
            "/sensors/{sensor_id}": "GET - получить конкретный датчик",
            "/refresh": "POST - обновить данные из блокчейна",
            "/export": "GET - экспортировать данные в файл",
            "/health": "GET - проверка здоровья сервиса"
        }
    }

@app.get("/sensors",
         summary="Получить все датчики",
         description="Возвращает список всех конфигураций датчиков")
async def get_all_sensors(
    refresh: bool = Query(False, description="Принудительно обновить данные"),
    limit: int = Query(100, ge=1, le=1000, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации")
):
    try:
        sensors = collector.get_sensors(force_refresh=refresh)
        
        # Пагинация
        items = list(sensors.items())[offset:offset + limit]
        
        return {
            "success": True,
            "count": len(items),
            "total": len(sensors),
            "sensors": dict(items),
            "timestamp": datetime.now().isoformat(),
            "last_update": collector._last_update.isoformat() if collector._last_update else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sensors/{sensor_id}",
         summary="Получить конкретный датчик",
         description="Возвращает конфигурацию указанного датчика")
async def get_sensor(
    sensor_id: str,
    refresh: bool = Query(False, description="Принудительно обновить данные")
):
    if refresh:
        collector.get_sensors(force_refresh=True)
    
    sensor_data = collector.get_sensor(sensor_id)
    if sensor_data is None:
        raise HTTPException(status_code=404, detail=f"Датчик {sensor_id} не найден")
    
    return {
        "success": True,
        "sensor_id": sensor_id,
        "data": sensor_data,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/refresh",
          summary="Обновить данные",
          description="Принудительно обновляет данные из блокчейна")
async def refresh():
    try:
        sensors = collector.get_sensors(force_refresh=True)
        return {
            "success": True,
            "message": "Данные успешно обновлены",
            "count": len(sensors),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export",
         summary="Экспортировать данные",
         description="Сохраняет текущие данные датчиков в JSON файл")
async def export():
    if collector.save_and_export(collector._cache):
        return {
            "success": True,
            "message": f"Данные сохранены в '{collector.output_file}'",
            "file": collector.output_file,
            "count": len(collector._cache),
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=500, detail="Не удалось сохранить данные")

@app.get("/health",
         summary="Проверка здоровья",
         description="Проверяет доступность сервиса")
async def health():
    return {
        "status": "healthy",
        "api": "running",
        "cache_size": len(collector._cache),
        "last_update": collector._last_update.isoformat() if collector._last_update else None
    }
