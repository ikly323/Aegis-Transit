import json
import requests
from datetime import datetime

class SensorDataCollector:
    def __init__(self, node_url: str, contract_id: str):
        self.node_url = node_url.rstrip('/')
        self.contract_id = contract_id
        self.output_file = "sensor_configs.json"
        self._cache = {}  # Добавили кэш
        self._last_update = None  # Добавили время обновления

    def fetch_contract_state(self):
        """Получает текущее состояние контракта через REST API ноды"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Запрос данных контракта {self.contract_id}...")
        url = f"{self.node_url}/contracts/{self.contract_id}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка связи с нодой: {e}")
            return None

    def process_sensors(self, state_data):
        """Фильтрует и структурирует данные о датчиках"""
        sensors = {}
        if not isinstance(state_data, list):
            state_data = state_data.get('state', []) if isinstance(state_data, dict) else []
        for entry in state_data:
            key = entry.get('key', '')
            value = entry.get('value', '')
            if key.startswith("sensor:"):
                sensor_id = key.split(":", 1)[1]
                try:
                    if isinstance(value, str):
                        sensors[sensor_id] = json.loads(value)
                    else:
                        sensors[sensor_id] = value
                except json.JSONDecodeError:
                    sensors[sensor_id] = {"raw_value": value, "error": "invalid_json"}
        return sensors

    def save_and_export(self, data):
        """Сохраняет данные в JSON файл для другой программы"""
        if not data:
            print("Данные для сохранения отсутствуют.")
            return False
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Успешно сохранено {len(data)} датчиков в '{self.output_file}'")
            return True
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")
            return False
    
    # === ДОБАВИЛИ ДВЕ НОВЫЕ МЕТОДЫ ===
    def get_sensors(self, force_refresh=False):
        """Получение датчиков с кэшированием"""
        if force_refresh or not self._cache:
            state = self.fetch_contract_state()
            if state:
                self._cache = self.process_sensors(state)
                self._last_update = datetime.now()
                self.save_and_export(self._cache)
        return self._cache.copy()
    
    def get_sensor(self, sensor_id: str):
        """Получение конкретного датчика"""
        sensors = self.get_sensors()
        return sensors.get(sensor_id)
    
    # === СТАРАЯ ФУНКЦИЯ main() для обратной совместимости ===
    def run_cli(self):
        """Запуск в старом режиме (CLI)"""
        print("[Режим CLI] Запуск однократного сбора данных...")
        state = self.fetch_contract_state()
        if state:
            sensors = self.process_sensors(state)
            if self.save_and_export(sensors):
                print("Программа завершена успешно. Данные готовы к чтению другой программой.")
                return True
        else:
            print("Не удалось получить данные. Проверьте адрес ноды и ID контракта.")
        return False
