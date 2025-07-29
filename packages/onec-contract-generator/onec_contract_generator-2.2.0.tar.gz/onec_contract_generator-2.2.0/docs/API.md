# 🔧 API Документация

## 📋 Обзор API

Система OneC Contract Generator предоставляет API для генерации контрактов метаданных из конфигураций 1С.

## 🚀 Установка и импорт

### Установка

```bash
# Через pip
pip install onec-contract-generator

# Или ручная установка
git clone <repository-url>
cd onec-contract-generator
pip install -r requirements.txt
```

### Импорт

```python
# Основные компоненты
from core.launcher import ContractGeneratorLauncher
from core.metadata_generator import MetadataGenerator
from core.form_generator import FormGenerator
from core.module_generator import ModuleGenerator

# Или импорт всего пакета
import onec_contract_generator

# При ручной установке используйте относительные импорты
from src.core.launcher import ContractGeneratorLauncher
from src.core.metadata_generator import MetadataGenerator
from src.core.form_generator import FormGenerator
from src.core.module_generator import ModuleGenerator
```

## 🚀 Launcher API

### Класс `ContractGeneratorLauncher`

Основной класс для запуска системы генерации контрактов.

```python
from core.launcher import ContractGeneratorLauncher

# Создание экземпляра
launcher = ContractGeneratorLauncher()

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
from core.metadata_generator import MetadataGenerator

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
- `category` (str): Категория лога (info, success, warning, error, summary)
- `message` (str): Сообщение

##### `_get_category_for_type(object_type: str) -> str`
Определяет категорию для типа объекта.

**Параметры**:
- `object_type` (str): Тип объекта

**Возвращает**: `str` - категория объекта

#### Поддерживаемые типы объектов

```python
ALLOWED_ROOT_TYPES = [
    "Конфигурации", "Языки", "Подсистемы", "Роли", "ПланыСчетов",
    "РегистрыБухгалтерии", "РегистрыРасчета", "ПланыВидовРасчета",
    "ПланыВидовСчетов", "ПланыВидовНоменклатуры", "ПланыВидовСвойств",
    "ПланыВидовСчетовБухгалтерии", "ПланыВидовСчетовНалоговогоУчета",
    "Перечисления", "ОбщиеМодули", "HTTPСервисы", "WebСервисы",
    "XDTOПакеты", "Стили", "ЭлементыСтиля", "ХранилищаНастроек",
    "ПараметрыСеанса", "РегламентныеЗадания", "ЖурналыДокументов",
    "ОпределяемыеТипы", "ОбщиеКартинки", "ОбщиеКоманды", "ОбщиеРеквизиты",
    "ГруппыКоманд", "Боты", "ПодпискиНаСобытия", "ФункциональныеОпции",
    "ПараметрыФункциональныхОпций", "КритерииОтбора", "ОбщиеШаблоны",
    "Расширения", "Справочники", "Документы", "Отчеты", "Обработки",
    "РегистрыСведений", "РегистрыНакопления", "ПланыВидовХарактерик",
    "ПланыОбмена"
]
```

## 📝 Form Generator API

### Класс `FormGenerator`

Генератор контрактов форм.

```python
from core.form_generator import FormGenerator

# Создание экземпляра
generator = FormGenerator(
    conf_dir="path/to/conf_files",
    output_dir="path/to/output"
)

# Генерация контрактов форм
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

##### `find_form_files() -> List[str]`
Находит все XML файлы форм.

**Возвращает**: `List[str]` - список путей к файлам форм

##### `parse_form_file(file_path: str) -> Dict[str, Any]`
Парсит XML файл формы.

**Параметры**:
- `file_path` (str): Путь к XML файлу формы

**Возвращает**: `Dict[str, Any]` - структура формы

##### `generate_form_contract(form_data: Dict[str, Any]) -> Dict[str, Any]`
Генерирует контракт формы.

**Параметры**:
- `form_data` (Dict[str, Any]): Данные формы

**Возвращает**: `Dict[str, Any]` - контракт формы

## 🔧 Module Generator API

### Класс `ModuleGenerator`

Генератор контрактов модулей (заглушка).

```python
from core.module_generator import ModuleGenerator

# Создание экземпляра
generator = ModuleGenerator(
    conf_dir="path/to/conf_files",
    output_dir="path/to/output"
)

# Генерация контрактов модулей
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
Основной метод генерации контрактов модулей (заглушка).

**Возвращает**: `bool` - всегда True (заглушка)

## 📊 Структуры данных

### Контракт метаданных

```python
{
    "type": "Справочник",
    "name": "Номенклатура",
    "comment": "Номенклатура товаров и услуг",
    "properties": [
        {
            "name": "Код",
            "type": "Строка",
            "length": 9,
            "comment": "Код номенклатуры"
        }
    ],
    "search_info": {
        "type": "Справочник",
        "category": "ОсновныеОбъекты",
        "full_name": "Справочник_Номенклатура",
        "search_keywords": ["Справочник", "Номенклатура", "товары", "услуги"],
        "object_short_name": "Номенклатура"
    },
    "generated_at": "C:\\YourProject\\onec-contract-generator",
    "source": "Text Report"
}
```

### Контракт формы

```python
{
    "form_type": "ФормаЭлемента",
    "object_name": "Справочник.Номенклатура",
    "form_name": "ФормаЭлементаФорма",
    "synonym": "Форма элемента (Номенклатура)",
    "comment": "Форма элемента справочника Номенклатура",
    "controls": [
        {
            "name": "Код",
            "type": "Поле",
            "data_path": "Объект.Код",
            "title": "Код"
        }
    ],
    "generated_at": "C:\\YourProject\\onec-contract-generator",
    "source": "XML Form Description"
}
```

### Контракт модуля

```python
{
    "module_type": "ObjectModule",
    "object_name": "Справочник.Номенклатура",
    "module_name": "Номенклатура_ModuleContract",
    "functions": [
        {
            "name": "ПриСозданииНаСервере",
            "parameters": [],
            "return_type": "void",
            "comment": "Обработчик события создания объекта"
        }
    ],
    "procedures": [
        {
            "name": "ЗаполнитьИзДругогоОбъекта",
            "parameters": [
                {
                    "name": "Источник",
                    "type": "СправочникСсылка.Номенклатура",
                    "comment": "Источник данных"
                }
            ],
            "comment": "Заполнение из другого объекта"
        }
    ],
    "generated_at": "C:\\YourProject\\onec-contract-generator",
    "source": "XML Module Description"
}
```

## 🔍 Категории объектов

### Основные объекты
- **Справочники** - справочные данные
- **Документы** - документооборот
- **Отчеты** - отчетные формы
- **Обработки** - обработки данных

### Регистры
- **РегистрыСведений** - регистры сведений
- **РегистрыНакопления** - регистры накопления
- **РегистрыБухгалтерии** - регистры бухгалтерии
- **РегистрыРасчета** - регистры расчета

### Планы
- **ПланыВидовХарактеристик** - планы видов характеристик
- **ПланыОбмена** - планы обмена
- **ПланыСчетов** - планы счетов
- **ПланыВидовРасчета** - планы видов расчета

### Общие объекты
- **Перечисления** - перечисления
- **ОбщиеМодули** - общие модули
- **ОбщиеКартинки** - общие картинки
- **ОбщиеКоманды** - общие команды

### Сервисы
- **HTTPСервисы** - HTTP сервисы
- **WebСервисы** - Web сервисы
- **XDTOПакеты** - XDTO пакеты

## 📝 Примеры использования

### Базовый пример

```python
from core.launcher import ContractGeneratorLauncher

# Создание и запуск
launcher = ContractGeneratorLauncher()
success = launcher.generate_contracts()

if success:
    print("✅ Контракты сгенерированы успешно")
else:
    print("❌ Ошибка генерации контрактов")
```

### Прямое использование генераторов

```python
from core.metadata_generator import MetadataGenerator
from core.form_generator import FormGenerator

# Генерация метаданных
metadata_gen = MetadataGenerator(
    report_path="conf_report/ОтчетПоКонфигурации.txt",
    output_dir="metadata_contracts"
)
metadata_success = metadata_gen.generate()

# Генерация форм
form_gen = FormGenerator(
    conf_dir="conf_files",
    output_dir="metadata_contracts"
)
form_success = form_gen.generate()

print(f"Метаданные: {'✅' if metadata_success else '❌'}")
print(f"Формы: {'✅' if form_success else '❌'}")
```

### Кастомная обработка

```python
from core.metadata_generator import MetadataGenerator
import json

# Создание генератора
generator = MetadataGenerator(
    report_path="conf_report/ОтчетПоКонфигурации.txt",
    output_dir="metadata_contracts"
)

# Парсинг отчета
objects_data = generator.parse_report()

# Кастомная обработка
for object_name, object_data in objects_data.items():
    # Генерация контракта
    contract = generator.generate_contract(object_data)
    
    # Кастомная модификация
    contract["custom_field"] = "custom_value"
    
    # Сохранение
    generator.save_contract(contract, object_name)
```

## 🛠️ Конфигурация

### Переменные окружения

```python
import os

# Отладочный режим
os.environ["ONEC_DEBUG"] = "1"

# Уровень логирования
os.environ["ONEC_LOG_LEVEL"] = "INFO"
```

### Логирование

```python
from core.metadata_generator import MetadataGenerator

generator = MetadataGenerator("report.txt", "output")

# Добавление логов
generator.log("info", "Начало обработки")
generator.log("success", "Объект обработан успешно")
generator.log("warning", "Предупреждение")
generator.log("error", "Ошибка обработки")
generator.log("summary", "Обработано 100 объектов")
```

## 🚀 Примеры использования

### Ручной запуск без pip

```python
# При ручной установке используйте относительные импорты
import sys
sys.path.append('src')

from core.launcher import ContractGeneratorLauncher
from core.metadata_generator import MetadataGenerator
from core.form_generator import FormGenerator

# Создание и запуск
launcher = ContractGeneratorLauncher()
success = launcher.generate_contracts()
```

### Запуск через скрипты

```bash
# Основной генератор
python scripts/generate.py

# С параметрами
python scripts/generate.py --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts"

# Анализ
python scripts/analyze.py --action stats

# Тестирование
python scripts/test.py
```

### Отладка отдельных компонентов

```python
# Только генератор метаданных
from src.core.metadata_generator import MetadataGenerator

generator = MetadataGenerator('output_dir')
generator.generate('path/to/report.txt')

# Только генератор форм
from src.core.form_generator import FormGenerator

generator = FormGenerator('output_dir')
generator.generate('path/to/conf_files')
```

## 🔗 Связанные документы

- [📖 Руководство по использованию](USAGE.md)
- [📋 Примеры использования](EXAMPLES.md)
- [🛠️ Руководство разработчика](DEVELOPMENT.md) 