# API приема показаний с датчиков и их обработки

Описание - система для сбора данных показаний датчиков и обработки этих данных.

├── processor/ # Модуль сбора данных
│ ├── processor.py # Основной скрипт сбора с логикой
│ ├── api.py # REST API
│ ├── run_api.py # Поднятие скрипта и REST API
│ ├── requirements.txt # Зависимости collector
│ └── README.md # Документация модуля

Быстрый старт: 
	### 1. Установка общих зависимостей
	pip install -r requirements.txt

	### 2. Запуск программы
	./processor/run_api.py

Зависимости: 
	fastapi>=0.100.0
	uvicorn[standard]>=0.23.0