# 🔧 API Документация

## 📋 Обзор API

Система OneC Contract Generator предоставляет API для генерации контрактов метаданных из конфигураций 1С.

## 🚀 Launcher API

### Класс `Launcher`

Основной класс для запуска системы генерации контрактов.

```python
from src.core.launcher import Launcher

# Создание экземпляра
launcher = Launcher()

# Запуск интерактивного режима
launcher.run_interactive_mode()

# Запуск автоматического режима
launcher.run_auto_mode()
```

#### Методы

##### `run_interactive_mode()`
Запускает интерактивный мастер для пошаговой настройки генерации.

**Возвращает**: `None`

##### `run_auto_mode()`
Запускает автоматический режим с параметрами командной строки.

**Возвращает**: `None`

##### `generate_contracts()`
Координирует процесс генерации всех типов контрактов.

**Возвращает**: `bool` - успешность выполнения

## 📋 Metadata Generator API

### Класс `MetadataGenerator`

Генератор контрактов метаданных объектов.

```python
from src.core.metadata_generator import MetadataGenerator

# Создание экземпляра
generator = MetadataGenerator(
    report_path="path/to/report.txt",
    output_dir="path/to/output"
)

# Генерация контрактов
success = generator.generate()
```

#### Конструктор

```python
__init__(self, report_path: str, output_dir: str)
```

**Параметры**:
- `report_path` (str): Путь к текстовому отчету конфигурации
- `output_dir` (str): Директория для сохранения контрактов

#### Методы

##### `generate() -> bool`
Основной метод генерации контрактов метаданных.

**Возвращает**: `bool` - успешность выполнения

##### `parse_report() -> Dict[str, Any]`
Парсит текстовый отчет и извлекает структуру объектов.

**Возвращает**: `Dict[str, Any]` - структура объектов

##### `generate_contract(object_data: Dict[str, Any]) -> Dict[str, Any]`
Генерирует контракт для одного объекта.

**Параметры**:
- `object_data` (Dict[str, Any]): Данные объекта

**Возвращает**: `Dict[str, Any]` - контракт объекта

##### `save_contract(contract: Dict[str, Any], object_name: str)`
Сохраняет контракт в JSON файл.

**Параметры**:
- `contract` (Dict[str, Any]): Контракт для сохранения
- `object_name` (str): Имя объекта

##### `log(category: str, message: str)`
Добавляет сообщение в лог.

**Параметры**:
- `category` (str): Категория сообщения (info, success, warning, error, summary)
- `message` (str): Текст сообщения

##### `print_logs()`
Выводит сгруппированные логи.

## 📝 Form Generator API

### Класс `FormGenerator`

Генератор контрактов форм.

```python
from src.core.form_generator import FormGenerator

# Создание экземпляра
generator = FormGenerator(
    conf_dir="path/to/conf_files",
    output_dir="path/to/output"
)

# Генерация контрактов
success = generator.generate()
```

#### Конструктор

```python
__init__(self, conf_dir: str, output_dir: str)
```

**Параметры**:
- `conf_dir` (str): Директория с файлами конфигурации
- `output_dir` (str): Директория для сохранения контрактов

#### Методы

##### `generate() -> bool`
Основной метод генерации контрактов форм.

**Возвращает**: `bool` - успешность выполнения

##### `find_form_files() -> List[Path]`
Находит все XML файлы форм в конфигурации.

**Возвращает**: `List[Path]` - список путей к файлам форм

##### `parse_form_xml(xml_path: Path) -> Optional[Dict[str, Any]]`
Парсит XML файл формы.

**Параметры**:
- `xml_path` (Path): Путь к XML файлу

**Возвращает**: `Optional[Dict[str, Any]]` - данные формы или None

##### `generate_form_contract(form_data: Dict[str, Any], form_name: str) -> Dict[str, Any]`
Генерирует контракт формы.

**Параметры**:
- `form_data` (Dict[str, Any]): Данные формы
- `form_name` (str): Имя формы

**Возвращает**: `Dict[str, Any]` - контракт формы

##### `process_form_file(xml_path: Path) -> bool`
Обрабатывает один файл формы.

**Параметры**:
- `xml_path` (Path): Путь к XML файлу

**Возвращает**: `bool` - успешность обработки

## 🔧 Module Generator API

### Класс `ModuleGenerator`

Генератор контрактов модулей.

```python
from src.core.module_generator import ModuleGenerator

# Создание экземпляра
generator = ModuleGenerator(
    conf_dir="path/to/conf_files",
    output_dir="path/to/output"
)

# Генерация контрактов
success = generator.generate()
```

#### Конструктор

```python
__init__(self, conf_dir: str, output_dir: str)
```

**Параметры**:
- `conf_dir` (str): Директория с файлами конфигурации
- `output_dir` (str): Директория для сохранения контрактов

#### Методы

##### `generate() -> bool`
Основной метод генерации контрактов модулей.

**Возвращает**: `bool` - успешность выполнения

##### `find_module_files() -> List[Path]`
Находит все XML файлы модулей.

**Возвращает**: `List[Path]` - список путей к файлам модулей

##### `parse_module_xml(xml_path: Path) -> Optional[Dict[str, Any]]`
Парсит XML файл модуля.

**Параметры**:
- `xml_path` (Path): Путь к XML файлу

**Возвращает**: `Optional[Dict[str, Any]]` - данные модуля или None

## 📊 Структуры данных

### Контракт метаданных

```python
{
    "metadata_type": "Object",
    "name": "Справочники.ДокументыПредприятия",
    "type": "Справочник",
    "comment": "Описание объекта",
    "structure": {
        "attributes_count": 3,
        "tabular_sections_count": 1,
        "attributes": [
            {
                "name": "Наименование",
                "type": "Строка",
                "path": "Справочники.ДокументыПредприятия.Реквизиты.Наименование"
            }
        ],
        "tabular_sections": [
            {
                "name": "Состав",
                "type": "ТабличнаяЧасть",
                "attributes": []
            }
        ]
    },
    "generated_at": "path/to/generator",
    "source": "Text Report"
}
```

### Контракт формы

```python
{
    "metadata_type": "Form",
    "name": "рлф_ФормаСпискаСПапками",
    "synonym": "Форма списка с папками (Рольф)",
    "comment": "Комментарий к форме",
    "form_type": "Managed",
    "structure": {
        "elements_count": 0,
        "attributes_count": 0,
        "elements": [],
        "attributes": []
    },
    "generated_at": "path/to/generator",
    "source": "XML Form Description"
}
```

### Контракт модуля

```python
{
    "metadata_type": "Module",
    "name": "ДокументыПредприятия_ModuleContract",
    "module_type": "ObjectModule",
    "functions": [
        {
            "name": "ПриСозданииНаСервере",
            "parameters": [],
            "return_type": "void"
        }
    ],
    "procedures": [
        {
            "name": "ОбработкаЗаполнения",
            "parameters": [
                {
                    "name": "Источник",
                    "type": "СправочникСсылка.ДокументыПредприятия"
                }
            ]
        }
    ],
    "generated_at": "path/to/generator",
    "source": "XML Module Description"
}
```

## 🔍 Обработка ошибок

### Исключения

Все генераторы могут выбрасывать следующие исключения:

- `FileNotFoundError`: Файл не найден
- `ET.ParseError`: Ошибка парсинга XML
- `UnicodeDecodeError`: Ошибка кодировки
- `Exception`: Общие ошибки

### Логирование

Все генераторы поддерживают группированное логирование:

```python
# Добавление сообщения в лог
generator.log("info", "Информационное сообщение")
generator.log("success", "Успешно обработан файл")
generator.log("warning", "Предупреждение")
generator.log("error", "Ошибка обработки")
generator.log("summary", "Сводка результатов")

# Вывод логов
generator.print_logs()
```

## 📋 Примеры использования

### Базовый пример

```python
from src.core.launcher import Launcher

# Создание и запуск
launcher = Launcher()
launcher.run_auto_mode()
```

### Прямое использование генераторов

```python
from src.core.metadata_generator import MetadataGenerator
from src.core.form_generator import FormGenerator

# Генерация метаданных
metadata_gen = MetadataGenerator("report.txt", "output")
metadata_gen.generate()

# Генерация форм
form_gen = FormGenerator("conf_files", "output")
form_gen.generate()
```

### Обработка ошибок

```python
from src.core.metadata_generator import MetadataGenerator

try:
    generator = MetadataGenerator("report.txt", "output")
    success = generator.generate()
    
    if success:
        print("Генерация завершена успешно")
    else:
        print("Генерация завершена с ошибками")
        
    # Вывод логов
    generator.print_logs()
    
except FileNotFoundError:
    print("Файл отчета не найден")
except Exception as e:
    print(f"Неожиданная ошибка: {e}")
```

---

**Для получения дополнительной информации см. [DEVELOPMENT.md](DEVELOPMENT.md)** 