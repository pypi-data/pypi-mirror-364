# Contributing to DmDSLab

Спасибо за интерес к проекту DmDSLab! Мы приветствуем вклад от сообщества.

## 🚀 Как начать

1. **Fork** репозитория
2. **Clone** ваш fork: `git clone https://github.com/YOUR_USERNAME/DmDSLab.git`
3. Создайте **feature branch**: `git checkout -b feature/amazing-feature`
4. Внесите изменения и протестируйте их
5. **Commit** изменения: `git commit -m 'Add amazing feature'`
6. **Push** в branch: `git push origin feature/amazing-feature`
7. Создайте **Pull Request**

## 📋 Типы вкладов

### 🐛 Багрепорты
- Используйте шаблон issue для багрепортов
- Предоставьте минимальный воспроизводимый пример
- Укажите версию Python и DmDSLab

### 💡 Новая функциональность
- Сначала создайте issue для обсуждения
- Убедитесь, что функция соответствует целям проекта
- Добавьте тесты и документацию

### 📚 Документация
- Исправления в README, docstrings, комментариях
- Примеры использования
- Переводы

### 🗃️ Новые датасеты UCI
- Добавление метаданных новых датасетов в `initialize_uci_database.py`
- Проверка качества и актуальности информации

## 🛠️ Настройка среды разработки

```bash
# Клонируйте репозиторий
git clone https://github.com/YOUR_USERNAME/DmDSLab.git
cd DmDSLab

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установите зависимости для разработки
pip install -e .
pip install pytest black flake8 mypy

# Инициализируйте базу данных UCI
python scripts/initialize_uci_database.py
```

## ✅ Стандарты кода

### Форматирование
```bash
# Форматирование кода
black dmdslab/ tests/

# Проверка стиля
flake8 dmdslab/ tests/

# Проверка типов
mypy dmdslab/
```

### Документация
- Все публичные функции и классы должны иметь docstrings
- Используйте Google-style docstrings
- Примеры в docstrings должны быть рабочими

Пример:
```python
def create_data_split(
    features: Union[np.ndarray, pd.DataFrame],
    y: Union[np.ndarray, pd.Series],
    test_size: Optional[float] = 0.2,
    random_state: Optional[int] = None,
) -> DataSplit:
    """
    Создание разбиения данных на train/validation/test.

    Args:
        features: Матрица признаков
        y: Целевая переменная
        test_size: Доля тестовой выборки
        random_state: Seed для воспроизводимости

    Returns:
        DataSplit: Объект с разбиением данных

    Example:
        >>> X = np.random.randn(100, 5)
        >>> y = np.random.randint(0, 2, 100)
        >>> split = create_data_split(X, y, test_size=0.2)
        >>> print(split.train.n_samples)
        80
    """
```

### Тестирование
- Все новые функции должны иметь тесты
- Используйте pytest
- Стремитесь к покрытию >80%

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=dmdslab tests/

# Запуск конкретного файла
pytest tests/test_ml_data_container.py -v
```

## 📦 Структура проекта

```
DmDSLab/
├── dmdslab/                 # Основной пакет
│   ├── __init__.py
│   └── datasets/           # Модуль работы с данными
│       ├── __init__.py
│       ├── ml_data_container.py
│       └── uci_dataset_manager.py
├── tests/                  # Тесты
│   ├── test_ml_data_container.py
│   └── test_uci_dataset_manager.py
├── scripts/               # Утилиты
│   └── initialize_uci_database.py
├── docs/                  # Документация (будет добавлена)
└── examples/              # Примеры использования (будет добавлено)
```

## 🏷️ Версионирование

Мы используем [Semantic Versioning](https://semver.org/):
- **MAJOR**: Обратно несовместимые изменения API
- **MINOR**: Новая функциональность (обратно совместимая)
- **PATCH**: Исправления багов

## 🎯 Приоритеты развития

### Высокий приоритет
- Расширение базы UCI датасетов
- Улучшение производительности загрузки
- Дополнительные методы разбиения данных

### Средний приоритет
- Интеграция с OpenML
- Визуализация характеристик датасетов
- Экспорт в различные форматы

### Низкий приоритет
- GUI интерфейс
- Интеграция с облачными хранилищами

## 🤝 Взаимодействие с сообществом

- **Обсуждения**: Используйте GitHub Discussions для вопросов
- **Issues**: Только для багов и feature requests
- **Pull Requests**: Для предложения изменений кода

## 📝 Шаблоны

### Issue Template
```markdown
## Описание проблемы/функции

## Шаги для воспроизведения (для багов)
1. 
2. 
3. 

## Ожидаемое поведение

## Текущее поведение

## Окружение
- Python версия:
- DmDSLab версия:
- ОС:

## Дополнительная информация
```

### Pull Request Template
```markdown
## Описание изменений

## Тип изменений
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Тестирование
- [ ] Тесты пройдены
- [ ] Добавлены новые тесты
- [ ] Документация обновлена

## Чек-лист
- [ ] Код соответствует стандартам проекта
- [ ] Self-review выполнен
- [ ] Комментарии добавлены в сложные места
- [ ] Документация обновлена
```

---

**Помните**: качество важнее количества. Лучше сделать одну хорошо продуманную функцию, чем десять неотполированных.