# 💡 Примеры использования

## 🚀 Быстрый старт

### Пример 1: Установка и первый запуск

```bash
# 1. Установка с PyPI
pip install onec-contract-generator

# 2. Запуск интерактивного режима
onec-contract-generate
```

**Результат**: Пошаговый мастер поможет настроить генерацию.

### Пример 2: Автоматический запуск

```bash
# Запуск с реальными данными
onec-contract-generate --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts"
```

**Результат**: Автоматическая генерация всех контрактов.

### Пример 3: Установка для разработки

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd onec-contract-generator

# 2. Установка в режиме разработки
pip install -e ".[dev]"

# 3. Запуск
onec-contract-generate
```

### Пример 4: Ручной запуск без pip

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd onec-contract-generator

# 2. Установите зависимости (если нужно)
pip install -r requirements.txt

# 3. Запуск через Python скрипты
python scripts/generate.py

# Или через модули напрямую
python -m src.core.launcher

# Или с параметрами
python scripts/generate.py --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts"
```

## 📋 Примеры контрактов

### Контракт справочника (новая структура)

```json
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
    },
    {
      "name": "Наименование",
      "type": "Строка",
      "length": 150,
      "comment": "Наименование номенклатуры"
    },
    {
      "name": "ВидНоменклатуры",
      "type": "ПеречислениеСсылка.ВидыНоменклатуры",
      "comment": "Вид номенклатуры"
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

### Контракт документа

```json
{
  "type": "Документ",
  "name": "ПоступлениеТоваров",
  "comment": "Документ поступления товаров",
  "properties": [
    {
      "name": "Номер",
      "type": "Строка",
      "length": 9,
      "comment": "Номер документа"
    },
    {
      "name": "Дата",
      "type": "Дата",
      "comment": "Дата документа"
    },
    {
      "name": "Контрагент",
      "type": "СправочникСсылка.Контрагенты",
      "comment": "Контрагент"
    }
  ],
  "tabular_sections": [
    {
      "name": "Товары",
      "type": "ТабличнаяЧасть",
      "properties": [
        {
          "name": "Номенклатура",
          "type": "СправочникСсылка.Номенклатура",
          "comment": "Номенклатура"
        },
        {
          "name": "Количество",
          "type": "Число",
          "comment": "Количество"
        }
      ]
    }
  ],
  "search_info": {
    "type": "Документ",
    "category": "ОсновныеОбъекты",
    "full_name": "Документ_ПоступлениеТоваров",
    "search_keywords": ["Документ", "ПоступлениеТоваров", "товары", "поступление"],
    "object_short_name": "ПоступлениеТоваров"
  },
  "generated_at": "C:\\YourProject\\onec-contract-generator",
  "source": "Text Report"
}
```

### Контракт формы

```json
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
    },
    {
      "name": "Наименование",
      "type": "Поле",
      "data_path": "Объект.Наименование",
      "title": "Наименование"
    },
    {
      "name": "ВидНоменклатуры",
      "type": "Поле",
      "data_path": "Объект.ВидНоменклатуры",
      "title": "Вид номенклатуры"
    }
  ],
  "generated_at": "C:\\YourProject\\onec-contract-generator",
  "source": "XML Form Description"
}
```

### Контракт модуля

```json
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
    },
    {
      "name": "ПриЗаписиНаСервере",
      "parameters": [
        {
          "name": "Отказ",
          "type": "Булево",
          "comment": "Признак отказа в записи"
        }
      ],
      "return_type": "void",
      "comment": "Обработчик события записи объекта"
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

## 🎯 Примеры команд

### Генерация контрактов

```bash
# Генерация всех контрактов (через pip)
onec-contract-generate --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts"

# Или ручной запуск
python scripts/generate.py --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts"

# Только контракты метаданных (через pip)
onec-contract-generate --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts" \
  --skip-forms \
  --skip-modules

# Или ручной запуск
python scripts/generate.py --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts" \
  --skip-forms \
  --skip-modules

# Только контракты форм (через pip)
onec-contract-generate --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts" \
  --skip-metadata \
  --skip-modules

# Или ручной запуск
python scripts/generate.py --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts" \
  --skip-metadata \
  --skip-modules
```

### Анализ контрактов

```bash
# Статистика (через pip)
onec-contract-analyze --action stats

# Или ручной запуск
python scripts/analyze.py --action stats

# Поиск по контрактам (через pip)
onec-contract-analyze --action search --query "Номенклатура"

# Или ручной запуск
python scripts/analyze.py --action search --query "Номенклатура"

# Валидация (через pip)
onec-contract-analyze --action validate

# Или ручной запуск
python scripts/analyze.py --action validate

# Экспорт отчета (через pip)
onec-contract-analyze --action report --output analysis.md

# Или ручной запуск
python scripts/analyze.py --action report --output analysis.md
```

### Тестирование

```bash
# Запуск тестов (через pip)
onec-contract-test

# Или ручной запуск
python scripts/test.py

# Или с pytest
pytest tests/

# С покрытием
pytest --cov=src
```

## 📊 Примеры логов

### Успешная генерация

```
🚀 OneC Contract Generator
==================================================

📋 ГЕНЕРАЦИЯ КОНТРАКТОВ МЕТАДАННЫХ
==================================================

🔍 info (5):
  • Обработка файла: C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt
  • Найдено корневых объектов: 1,234
  • Обработано строк: 45,678
  • Найдено типов объектов: 15
  • Найдено неизвестных типов: 2

✅ success (1,232):
  • Создан контракт: Справочник_Номенклатура
  • Создан контракт: Документ_ПоступлениеТоваров
  • Создан контракт: Перечисление_ВидыНоменклатуры
  • ... и еще 1,229 сообщений

⚠️ warning (2):
  • Неизвестный тип объекта: ЭлементыСтиля в строке 12,345
  • Неизвестный тип объекта: ХранилищаНастроек в строке 23,456

📋 summary (1):
  • Обработано объектов: 1,234, успешно: 1,232

📝 ГЕНЕРАЦИЯ КОНТРАКТОВ ФОРМ
==================================================

🔍 info (3):
  • Найдено 180 файлов форм по паттерну: **/Forms/*.xml
  • Найдено 45 файлов форм по паттерну: **/Forms/*/*.xml
  • Всего найдено уникальных файлов форм: 200

✅ success (195):
  • Создан контракт: Форма_рлф_ФормаСпискаСПапками
  • Создан контракт: Форма_ФормаЭлементаФорма
  • ... и еще 193 сообщения

⚠️ warning (5):
  • Не найден элемент Form в файле: Template.xml
  • Ошибка при парсинге элементов формы: Invalid XML

📋 summary (1):
  • Обработано файлов: 200, успешно: 195

🎉 ГЕНЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!
==================================================

📊 ИТОГОВАЯ СТАТИСТИКА:
  • Контракты метаданных: 1,232
  • Контракты форм: 195
  • Контракты модулей: 0 (пропущены)
  • Общее время: 45.6 секунд
  • Размер выходных файлов: 12.3 MB
```

### Ошибки и предупреждения

```
⚠️ ПРЕДУПРЕЖДЕНИЯ:
  • Неизвестный тип объекта: ЭлементыСтиля
  • Неизвестный тип объекта: ХранилищаНастроек
  • Файл не найден: C:\YourProject\YourConfig\conf_files\Forms\Template.xml
  • Ошибка парсинга XML: Invalid XML structure

💡 РЕКОМЕНДАЦИИ:
  • Добавьте неизвестные типы в ALLOWED_ROOT_TYPES
  • Проверьте структуру XML файлов форм
  • Убедитесь в корректности путей к файлам
```

## 🔍 Примеры поиска

### Поиск по типу объекта

```bash
onec-contract-analyze --action search --query "Справочник"
```

**Результат:**
```
🔍 РЕЗУЛЬТАТЫ ПОИСКА: "Справочник"
==================================================

📋 Найдено контрактов: 123

📁 Справочники:
  • Справочник_Номенклатура
  • Справочник_Контрагенты
  • Справочник_Организации
  • ... и еще 120 объектов
```

### Поиск по имени объекта

```bash
onec-contract-analyze --action search --query "Номенклатура"
```

**Результат:**
```
🔍 РЕЗУЛЬТАТЫ ПОИСКА: "Номенклатура"
==================================================

📋 Найдено контрактов: 5

📁 Объекты:
  • Справочник_Номенклатура
  • Документ_ПоступлениеТоваров (содержит ссылку на Номенклатуру)
  • Форма_ФормаЭлементаФорма (форма элемента Номенклатуры)
  • Модуль_Номенклатура_ModuleContract
  • Перечисление_ВидыНоменклатуры
```

## 📈 Примеры статистики

### Полная статистика

```bash
onec-contract-analyze --action stats
```

**Результат:**
```
📊 СТАТИСТИКА КОНТРАКТОВ
==================================================

📋 Контракты метаданных: 1,234
📝 Контракты форм: 567
🔧 Контракты модулей: 890

📁 По типам объектов:
  Справочники: 123
  Документы: 456
  Отчеты: 78
  Обработки: 90
  Перечисления: 45
  ОбщиеМодули: 67
  РегистрыСведений: 89
  РегистрыНакопления: 56
  РегистрыБухгалтерии: 34
  ПланыВидовХарактерик: 23
  HTTPСервисы: 12
  WebСервисы: 8
  XDTOПакеты: 5
  Другие: 148

📁 По категориям:
  ОсновныеОбъекты: 747
  Регистры: 179
  Планы: 23
  ОбщиеОбъекты: 112
  Сервисы: 25
  СистемныеОбъекты: 148

📈 Общий размер: 45.6 MB
📊 Средний размер контракта: 12.3 KB
```

## 🛠️ Примеры конфигурации

### Переменные окружения

```bash
# Windows
set ONEC_DEBUG=1
set ONEC_LOG_LEVEL=INFO
onec-contract-generate

# Linux/macOS
export ONEC_DEBUG=1
export ONEC_LOG_LEVEL=INFO
onec-contract-generate
```

### Структура проекта

```
YourProject/
├── conf_files/                    # Файлы конфигурации
│   ├── Catalogs/
│   │   ├── Номенклатура/
│   │   └── Контрагенты/
│   ├── Documents/
│   │   ├── ПоступлениеТоваров/
│   │   └── РеализацияТоваров/
│   └── Forms/
│       ├── Номенклатура/
│       └── ПоступлениеТоваров/
├── conf_report/                   # Отчеты конфигурации
│   └── ОтчетПоКонфигурации.txt
└── metadata_contracts/            # Выходные контракты
    ├── Справочник_Номенклатура.json
    ├── Документ_ПоступлениеТоваров.json
    ├── Форма_ФормаЭлементаФорма.json
    └── ...
```

## 🔗 Связанные документы

- [📖 Руководство по использованию](USAGE.md)
- [🔧 API документация](API.md)
- [🛠️ Руководство разработчика](DEVELOPMENT.md)
- [📦 Руководство по публикации](../PUBLISH_GUIDE.md) 