# API импорта контракта блокчейна

Описание - система для сбора данных из блокчейна и обработки данных из контракта.

├── collector/ # Модуль сбора данных
│ ├── collector.py # Основной скрипт сбора с логикой
│ ├── api.py # REST API
│ ├── run_api.py # Поднятие скрипта и REST API
│ ├── requirements.txt # Зависимости collector
│ └── README.md # Документация модуля

Быстрый старт: 
	### 1. Установка общих зависимостей
	pip install -r requirements.txt

	### 2. Запуск программы
	./collector/run_api.py

Зависимости: 
	fastapi>=0.100.0
	uvicorn[standard]>=0.23.0
	requests>=2.31.0