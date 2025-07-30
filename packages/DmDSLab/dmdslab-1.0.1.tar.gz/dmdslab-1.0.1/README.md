# DmDSLab: Data Science Laboratory Toolkit

[![PyPI version](https://badge.fury.io/py/DmDSLab.svg)](https://badge.fury.io/py/DmDSLab)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**DmDSLab** — это библиотека инструментов для автоматизации рутинных задач в Data Science проектах, с фокусом на удобную работу с датасетами и структурированное управление данными.

## 🚀 Основные возможности

- **Контейнеры данных**: Типизированные структуры для хранения ML данных (`ModelData`, `DataSplit`)
- **UCI Dataset Manager**: Удобный доступ к датасетам UCI ML Repository с кэшированием
- **Автоматические разбиения**: Создание train/validation/test разбиений и k-fold CV
- **Метаданные**: Встроенная поддержка информации о датасетах и экспериментах

## 📦 Установка

```bash
pip install DmDSLab
```

Для работы с UCI датасетами:
```bash
pip install DmDSLab[uci]
```

## 🔥 Быстрый старт

### Работа с контейнерами данных

```python
from dmdslab.datasets import ModelData, create_data_split
import numpy as np

# Создание структуры данных
X = np.random.randn(1000, 10)
y = np.random.randint(0, 2, 1000)

data = ModelData(features=X, target=y)
print(f"Dataset shape: {data.shape}")
print(f"Feature names: {data.feature_names}")

# Автоматическое разбиение данных
split = create_data_split(X, y, test_size=0.2, validation_size=0.1)
print(f"Train: {split.train.n_samples}, Val: {split.validation.n_samples}, Test: {split.test.n_samples}")
```

### Работа с UCI датасетами

```python
from dmdslab.datasets.uci_dataset_manager import UCIDatasetManager, TaskType

# Инициализация менеджера
manager = UCIDatasetManager()

# Поиск датасетов
datasets = manager.filter_datasets(
    task_type=TaskType.BINARY_CLASSIFICATION,
    min_instances=1000,
    max_instances=10000
)

# Загрузка датасета
model_data = manager.load_dataset(73)  # Mushroom dataset
print(f"Loaded: {model_data.info.name}")
print(f"Shape: {model_data.shape}")

# Создание разбиений
split = manager.load_dataset_split(73, test_size=0.2, random_state=42)
kfold_splits = manager.load_dataset_kfold(73, n_splits=5, random_state=42)
```

## 📚 Документация

### Архитектура

```
dmdslab/
├── datasets/           # Работа с датасетами
│   ├── ml_data_container.py    # Контейнеры данных
│   └── uci_dataset_manager.py  # UCI Repository integration
└── scripts/           # Утилиты и скрипты инициализации
```

### Основные компоненты

#### ModelData
Контейнер для хранения признаков и целевой переменной с метаданными:
- Автоматическое преобразование pandas → numpy
- Встроенная валидация размерностей
- Поддержка выборки и копирования
- Интеграция с DataInfo для метаданных

#### DataSplit
Структура для организации train/validation/test разбиений:
- Гибкие конфигурации разбиений
- Автоматический расчет пропорций
- Поддержка стратификации
- Метаинформация о разбиении

#### UCIDatasetManager
Менеджер для работы с UCI ML Repository:
- Локальная база метаданных (30+ датасетов)
- Фильтрация по типу задач, размеру, домену
- Кэширование загруженных данных
- Автоматическое создание разбиений

## 🗄️ База данных UCI датасетов

Проект включает предварительно настроенную базу данных с метаданными популярных UCI датасетов:

```python
# Инициализация базы данных
python scripts/initialize_uci_database.py

# Статистика
manager = UCIDatasetManager()
stats = manager.get_statistics()
print(f"Доступно датасетов: {stats['total_datasets']}")
```

Включает датасеты из различных доменов:
- **Финансы**: Credit scoring, банковский маркетинг
- **Медицина**: Диагностика, предсказание осложнений  
- **Кибербезопасность**: Детекция спама, фишинговых сайтов
- **Физика**: Детекция частиц, астрономия
- **И многое другое**: 15+ доменов, разные размеры и сложность

## 🔬 Для исследователей

DmDSLab создан для исследователей, которые хотят:
- Быстро получать доступ к стандартным датасетам
- Воспроизводимо создавать разбиения данных
- Структурированно хранить метаданные экспериментов
- Фокусироваться на алгоритмах, а не на подготовке данных

## 🛠️ Разработка

```bash
# Клонирование репозитория
git clone https://github.com/Dmatryus/DmDSLab.git
cd DmDSLab

# Установка в режиме разработки
pip install -e .

# Запуск тестов
pytest tests/
```

## 📄 Лицензия

Apache License 2.0. См. [LICENSE](LICENSE) для деталей.

## 👨‍💻 Автор

**Dmatryus Detry** - [GitHub](https://github.com/Dmatryus)

---

*DmDSLab - инструменты для эффективных исследований в Data Science*