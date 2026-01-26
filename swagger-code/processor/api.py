"""
api.py - REST API для обработчика показаний датчиков
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException, Query, Body

# Импортируем ваш класс процессора
from processor import SensorProcessor

# Создаем экземпляр процессора
processor = SensorProcessor()

# Создаем FastAPI приложение
app = FastAPI(
    title="Sensor Processor API",
    description="API для обработки показаний датчиков и проверки лимитов",
    version="1.0.0"
)

@app.get("/",
         summary="Информация о API",
         description="Корневой эндпоинт с основной информацией о процессоре")
async def root():
    return {
        "service": "Sensor Processor API",
        "version": "1.0.0",
        "description": "Обработчик показаний датчиков: проверяет лимиты, формирует результаты для блокчейна",
        "config_file": processor.config_file,
        "export_file": processor.export_file,
        "endpoints": {
            "/process": "POST - обработать одно показание или пакет",
            "/results": "GET - получить последние результаты",
            "/status": "GET - статистика обработки",
            "/config-check": "GET - проверка конфигурации"
        }
    }

@app.post("/process",
          summary="Обработать показания",
          description="Обрабатывает одно или несколько показаний датчиков")
async def process_reading(
    sensor_id: Optional[str] = Body(None, description="ID датчика (для одиночного запроса)"),
    value: Optional[float] = Body(None, description="Значение (для одиночного запроса)"),
    batch: Optional[List[Dict]] = Body(None, description="Пакет показаний для обработки")
):
    """
    Обрабатывает показания датчиков.
    
    Можно отправить:
    1. Одно показание: {"sensor_id": "001", "value": 25.5}
    2. Пакет показаний: {"batch": [{"sensor_id": "001", "value": 25.5}, ...]}
    """
    try:
        results = []
        
        if batch:
            # Обработка пакета
            results = processor.process_batch(batch)
            for result in results:
                processor.save_to_export_file(result)
        elif sensor_id is not None and value is not None:
            # Одно показание
            result = processor.process_reading(sensor_id, value)
            processor.save_to_export_file(result)
            results = [result]
        else:
            raise HTTPException(
                status_code=400,
                detail="Укажите либо sensor_id и value, либо batch"
            )
        
        return {
            "success": True,
            "count": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "export_file": processor.export_file
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results",
         summary="Получить результаты",
         description="Возвращает последние обработанные результаты")
async def get_results(
    limit: int = Query(20, ge=1, le=100, description="Количество последних результатов"),
    status_filter: Optional[str] = Query(None, description="Фильтр по статусу (например, HIGH_ALARM)")
):
    try:
        results = processor.get_recent_results(limit)
        
        if status_filter:
            results = [r for r in results if r.get("status") == status_filter]
        
        return {
            "success": True,
            "count": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status",
         summary="Статистика обработки",
         description="Статистика по обработанным показаниям")
async def get_status():
    try:
        summary = processor.get_status_summary()
        return {
            "success": True,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config-check",
         summary="Проверка конфигурации",
         description="Проверяет наличие и корректность файла конфигурации")
async def config_check():
    try:
        configs = processor.load_sensor_configs()
        return {
            "success": True,
            "config_file": processor.config_file,
            "sensors_count": len(configs),
            "timestamp": datetime.now().isoformat(),
            "note": f"Файл конфигурации загружен успешно. Датчиков: {len(configs)}"
        }
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Файл конфигурации не найден: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export-queue",
         summary="Очередь на экспорт",
         description="Показывает данные в файле для отправки в блокчейн")
async def get_export_queue(
    limit: int = Query(50, ge=1, le=1000, description="Лимит записей")
):
    try:
        if not os.path.exists(processor.export_file):
            return {
                "success": True,
                "message": "Файл экспорта не существует",
                "queue": [],
                "count": 0
            }
        
        with open(processor.export_file, 'r', encoding='utf-8') as f:
            queue = json.load(f)
        
        if not isinstance(queue, list):
            queue = []
        
        return {
            "success": True,
            "export_file": processor.export_file,
            "count": len(queue),
            "queue": queue[-limit:],  # Последние записи
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))