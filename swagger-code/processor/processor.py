"""
processor.py - Обработчик показаний датчиков
Читает настройки, проверяет лимиты, формирует результаты для блокчейна
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class SensorProcessor:
    def __init__(self, config_file: str = "sensor_configs.json", 
                 export_file: str = "to_blockchain.json"):
        """
        Инициализация обработчика
        
        Args:
            config_file: Файл с настройками датчиков от collector
            export_file: Файл для сохранения результатов
        """
        self.config_file = config_file
        self.export_file = export_file
        self._results_cache = []  # Кэш последних результатов
        
    def load_sensor_configs(self) -> Dict:
        """Загружает конфигурации датчиков из файла"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"Файл {self.config_file} не найден. "
                f"Сначала запустите Sensor Collector!"
            )
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def process_reading(self, sensor_id: str, current_value: float) -> Dict:
        """
        Обрабатывает одно показание датчика
        
        Args:
            sensor_id: Идентификатор датчика
            current_value: Текущее показание
            
        Returns:
            Словарь с результатом обработки
        """
        try:
            configs = self.load_sensor_configs()
        except FileNotFoundError as e:
            return {
                "sensor_id": sensor_id,
                "value": current_value,
                "timestamp": datetime.now().isoformat(),
                "status": "ERROR_NO_CONFIG",
                "applied_limits": "NONE",
                "error": str(e)
            }
        
        # Получаем лимиты для датчика
        limits = configs.get(sensor_id)
        
        # Определяем статус и диапазон
        status = "NORMAL"
        applied_range = "NONE"
        
        if limits is None:
            status = "NOT_CONFIGURED_IGNORED"
            applied_range = "NONE"
        else:
            min_val = limits.get("min")
            max_val = limits.get("max")
            applied_range = f"{min_val}-{max_val}"
            
            if min_val is None or max_val is None:
                status = "SENSOR_DISABLED"
            elif current_value < min_val:
                status = "LOW_ALARM"
            elif current_value > max_val:
                status = "HIGH_ALARM"
        
        # Формируем результат
        result = {
            "sensor_id": sensor_id,
            "value": current_value,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "applied_limits": applied_range
        }
        
        # Сохраняем в кэш
        self._results_cache.append(result)
        if len(self._results_cache) > 100:  # Ограничиваем размер кэша
            self._results_cache = self._results_cache[-50:]
        
        return result
    
    def process_batch(self, readings: List[Dict]) -> List[Dict]:
        """
        Обрабатывает пакет показаний
        
        Args:
            readings: Список словарей [{"sensor_id": "id", "value": 25.5}, ...]
            
        Returns:
            Список результатов обработки
        """
        results = []
        for reading in readings:
            result = self.process_reading(
                reading["sensor_id"], 
                reading["value"]
            )
            results.append(result)
        return results
    
    def save_to_export_file(self, result: Dict) -> bool:
        """
        Сохраняет результат в файл для отправки в блокчейн
        
        Args:
            result: Результат обработки
            
        Returns:
            True если успешно сохранено
        """
        try:
            history = []
            if os.path.exists(self.export_file):
                with open(self.export_file, 'r', encoding='utf-8') as f:
                    try: 
                        history = json.load(f)
                        if not isinstance(history, list):
                            history = []
                    except: 
                        history = []
            
            history.append(result)
            
            with open(self.export_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Ошибка при сохранении в файл: {e}")
            return False
    
    def get_recent_results(self, limit: int = 20) -> List[Dict]:
        """Возвращает последние результаты обработки"""
        return self._results_cache[-limit:] if self._results_cache else []
    
    def get_status_summary(self) -> Dict:
        """Статистика по статусам"""
        status_counts = {}
        for result in self._results_cache:
            status = result.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_processed": len(self._results_cache),
            "status_counts": status_counts,
            "last_processed": self._results_cache[-1] if self._results_cache else None
        }
    
    def run_cli_example(self):
        """Пример работы в CLI режиме (как у вас было)"""
        print("=== Обработчик показаний датчиков ===\n")
        
        # Примеры показаний
        test_readings = [
            {"sensor_id": "999", "value": 50.0},  # Не настроен
            {"sensor_id": "001", "value": 30.0},  # Авария
            {"sensor_id": "002", "value": 22.0},  # Норма
        ]
        
        for reading in test_readings:
            print(f"\nОбработка: {reading['sensor_id']} = {reading['value']}")
            result = self.process_reading(reading["sensor_id"], reading["value"])
            
            # Сохраняем для отправки
            if self.save_to_export_file(result):
                print(f"  Статус: {result['status']}")
                print(f"  Лимиты: {result['applied_limits']}")
                
                if result["status"] not in ["NORMAL", "NOT_CONFIGURED_IGNORED"]:
                    print(f"  🚨 ALERT: {result['sensor_id']} статус {result['status']}!")
        
        print(f"\n✅ Результаты сохранены в {self.export_file}")

# Для обратной совместимости
def process_new_reading(sensor_id: str, current_value: float):
    """Старая функция для обратной совместимости"""
    processor = SensorProcessor()
    result = processor.process_reading(sensor_id, current_value)
    processor.save_to_export_file(result)
    
    if result["status"] not in ["NORMAL", "NOT_CONFIGURED_IGNORED"]:
        print(f"🚨 ALERT: {sensor_id} статус {result['status']}!")
    
    return result

if __name__ == "__main__":
    # Старый режим CLI
    processor = SensorProcessor()
    processor.run_cli_example()