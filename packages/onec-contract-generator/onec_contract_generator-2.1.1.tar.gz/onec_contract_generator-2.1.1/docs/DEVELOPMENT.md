# 🔧 Документация для разработчиков

## 🏗️ Архитектура системы

### 📁 Структура проекта

```
onec-contract-generator/
├── src/                            # Основные компоненты
│   ├── core/                       # Основные компоненты
│   │   ├── launcher.py             # 🚀 Единый запускатор системы
│   │   ├── metadata_generator.py   # 📋 Генератор контрактов метаданных
│   │   ├── form_generator.py       # 📝 Генератор контрактов форм
│   │   └── module_generator.py     # 🔧 Генератор контрактов модулей
│   ├── utils/                      # Утилиты (пока не реализованы)
│   └── parsers/                    # Парсеры (пока не реализованы)
```

### 🔄 Поток данных

```
Входные данные → Парсеры → Генераторы → Контракты → Анализ
     ↓              ↓          ↓          ↓         ↓
  XML файлы    → XML Parser → Form Gen → JSON → Validator
  Текстовые    → Text Parser → Metadata Gen → JSON → Analyzer
  отчеты       → BSL Parser → Module Gen → JSON → Reporter
```

## 🎯 Основные компоненты

### 🚀 Launcher (`src/core/launcher.py`)

**Назначение**: Единая точка входа в систему

**Основные функции**:
- Парсинг аргументов командной строки
- Координация работы генераторов
- Интерактивный режим
- Обработка ошибок

**Ключевые методы**:
```python
def run_interactive_mode()      # Интерактивный мастер
def run_auto_mode()            # Автоматический режим
def validate_paths()           # Валидация путей
def generate_contracts()       # Координация генерации
```

### 📋 Metadata Generator (`src/core/metadata_generator.py`)

**Назначение**: Генерация контрактов метаданных из текстовых отчетов

**Основные функции**:
- Парсинг текстовых отчетов конфигурации
- Извлечение структуры объектов
- Генерация JSON контрактов
- Группированное логирование

**Ключевые методы**:
```python
def parse_report()             # Парсинг отчета
def generate_contract()        # Генерация контракта
def save_contract()            # Сохранение контракта
def log()                      # Логирование
def print_logs()               # Вывод логов
```

### 📝 Form Generator (`src/core/form_generator.py`)

**Назначение**: Генерация контрактов форм из XML файлов

**Основные функции**:
- Парсинг XML файлов форм
- Извлечение свойств форм
- Генерация структурированных контрактов
- Обработка ошибок парсинга

**Ключевые методы**:
```python
def find_form_files()          # Поиск файлов форм
def parse_form_xml()           # Парсинг XML
def generate_form_contract()   # Генерация контракта
def process_form_file()        # Обработка файла
```

### 🔧 Module Generator (`src/core/module_generator.py`)

**Назначение**: Генерация контрактов модулей из XML файлов

**Основные функции**:
- Парсинг XML файлов модулей
- Извлечение функций и процедур
- Генерация контрактов модулей
- Обработка различных типов модулей

## 📊 Система логирования

### 🏷️ Категории логов

```python
# Категории для группировки логов
LOGS_CATEGORIES = {
    'info': 'Информационные сообщения',
    'success': 'Успешно обработанные файлы',
    'warning': 'Предупреждения',
    'error': 'Критические ошибки',
    'summary': 'Сводки по результатам'
}
```

### 📋 Пример использования

```python
class Generator:
    def __init__(self):
        self.logs = defaultdict(list)
    
    def log(self, category: str, message: str):
        """Добавляет сообщение в лог с группировкой"""
        self.logs[category].append(message)
    
    def print_logs(self):
        """Выводит сгруппированные логи"""
        for category, messages in self.logs.items():
            if messages:
                print(f"\n🔍 {category} ({len(messages)}):")
                for msg in messages[:5]:
                    print(f"  • {msg}")
```

## 🔄 Процесс разработки

### 1. Добавление нового генератора

```python
# 1. Создайте новый файл в src/core/
class NewGenerator:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.logs = defaultdict(list)
    
    def generate(self) -> bool:
        """Основной метод генерации"""
        # Реализация генерации
        pass
    
    def log(self, category: str, message: str):
        """Логирование"""
        self.logs[category].append(message)
```

### 2. Интеграция в launcher

```python
# В src/core/launcher.py
def generate_contracts(self):
    # Добавьте вызов нового генератора
    if not self.skip_new:
        new_generator = NewGenerator(
            self.conf_dir, 
            self.output_dir / "new_contracts"
        )
        success = new_generator.generate()
        if not success:
            self.log("error", "Ошибка генерации новых контрактов")
```

### 3. Добавление тестов

```python
# В tests/test_new_generator.py
def test_new_generator():
    generator = NewGenerator("test_input", "test_output")
    result = generator.generate()
    assert result == True
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
python scripts/test.py

# Конкретные тесты
python -m pytest tests/test_metadata_generator.py -v

# С покрытием
python -m pytest tests/ --cov=src --cov-report=html
```

### Структура тестов

```
tests/
├── test_launcher.py              # Тесты запускатора
├── test_metadata_generator.py    # Тесты генератора метаданных
├── test_form_generator.py        # Тесты генератора форм
├── test_module_generator.py      # Тесты генератора модулей
└── test_utils.py                 # Тесты утилит
```

## 🔧 Конфигурация

### Переменные окружения

```bash
# Кодировка для Windows
PYTHONIOENCODING=utf-8

# Путь к Python
PYTHONPATH=src/
```

### Настройки проекта

```python
# В setup.py
setup(
    name="onec-contract-generator",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pathlib",
        "json",
        "xml.etree.ElementTree"
    ]
)
```

## 🚨 Обработка ошибок

### Типы ошибок

1. **Ошибки файловой системы**
   - Файлы не найдены
   - Нет прав доступа
   - Неверные пути

2. **Ошибки парсинга**
   - Неверный формат XML
   - Поврежденные файлы
   - Неподдерживаемые структуры

3. **Ошибки генерации**
   - Недостаточно данных
   - Конфликты имен
   - Ошибки сериализации

### Стратегия обработки

```python
try:
    # Основная логика
    result = process_file(file_path)
except FileNotFoundError:
    self.log("error", f"Файл не найден: {file_path}")
    return False
except ET.ParseError as e:
    self.log("warning", f"Ошибка парсинга XML: {e}")
    return False
except Exception as e:
    self.log("error", f"Неожиданная ошибка: {e}")
    return False
```

## 📈 Планы развития

### 🔄 Краткосрочные задачи

1. **Улучшение парсинга форм**
   - Извлечение элементов управления
   - Парсинг команд и реквизитов
   - Обработка табличных частей

2. **Расширение валидации**
   - Проверка структуры контрактов
   - Валидация типов данных
   - Проверка целостности

3. **Добавление утилит**
   - Анализатор контрактов
   - Генератор отчетов
   - Инструменты сравнения

### 🎯 Долгосрочные задачи

1. **Поддержка новых форматов**
   - Экспорт в YAML
   - Экспорт в XML
   - Интеграция с IDE

2. **Расширенный анализ**
   - Статистика использования
   - Анализ зависимостей
   - Рекомендации по оптимизации

3. **Интеграция с экосистемой**
   - Плагины для IDE
   - CI/CD интеграция
   - API для внешних систем

## 🤝 Рекомендации по разработке

### 📝 Код-стайл

1. **Используйте типизацию**
   ```python
   def process_file(file_path: Path) -> Dict[str, Any]:
   ```

2. **Добавляйте документацию**
   ```python
   def generate_contract(self) -> Dict[str, Any]:
       """Генерирует контракт для объекта."""
   ```

3. **Логируйте действия**
   ```python
   self.log("info", f"Обрабатываю файл: {file_path}")
   ```

### 🔍 Отладка

1. **Используйте группированные логи**
2. **Проверяйте промежуточные результаты**
3. **Тестируйте на реальных данных**
4. **Добавляйте unit-тесты**

### 🚀 Производительность

1. **Обрабатывайте файлы потоково**
2. **Используйте генераторы для больших файлов**
3. **Кэшируйте результаты парсинга**
4. **Оптимизируйте поиск файлов**

---

**Удачной разработки! 🚀** 