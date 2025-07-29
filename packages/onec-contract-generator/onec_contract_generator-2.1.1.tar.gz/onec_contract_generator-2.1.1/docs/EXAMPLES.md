# 💡 Примеры использования

## 🚀 Быстрый старт

### Пример 1: Первый запуск

```bash
# 1. Перейдите в директорию проекта
cd onec-contract-generator

# 2. Запустите интерактивный режим
python scripts/generate.py
```

**Результат**: Пошаговый мастер поможет настроить генерацию.

### Пример 2: Автоматический запуск

```bash
# Запуск с реальными данными
python scripts/generate.py --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts"
```

**Результат**: Автоматическая генерация всех контрактов.

## 📋 Примеры контрактов

### Контракт справочника

```json
{
  "metadata_type": "Object",
  "name": "Справочники.ДокументыПредприятия",
  "type": "Справочник",
  "comment": "Справочник документов предприятия",
  "structure": {
    "attributes_count": 3,
    "tabular_sections_count": 1,
    "attributes": [
      {
        "name": "Наименование",
        "type": "Строка",
        "path": "Справочники.ДокументыПредприятия.Реквизиты.Наименование"
      },
      {
        "name": "Код",
        "type": "Строка",
        "path": "Справочники.ДокументыПредприятия.Реквизиты.Код"
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
  "generated_at": "C:\\YourProject\\onec-contract-generator",
  "source": "Text Report"
}
```

### Контракт формы

```json
{
  "metadata_type": "Form",
  "name": "рлф_ФормаСпискаСПапками",
  "synonym": "Форма списка с папками (Рольф)",
  "comment": "Форвард; Мазалов Е.А.; 04.02.2025; 92558",
  "form_type": "Managed",
  "structure": {
    "elements_count": 0,
    "attributes_count": 0,
    "elements": [],
    "attributes": []
  },
  "generated_at": "C:\\YourProject\\onec-contract-generator",
  "source": "XML Form Description"
}
```

### Контракт модуля

```json
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
  "generated_at": "C:\\YourProject\\onec-contract-generator",
  "source": "XML Module Description"
}
```

## 🔧 Примеры команд

### Генерация только метаданных

```bash
python scripts/generate.py --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --skip-forms --skip-modules
```

### Генерация только форм

```bash
python scripts/generate.py --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --skip-metadata --skip-modules
```

### Генерация только модулей

```bash
python scripts/generate.py --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --skip-metadata --skip-forms
```

## 📊 Примеры анализа

### Получение статистики

```bash
python scripts/analyze.py --action stats
```

**Результат**:
```
📊 Статистика контрактов:
- Всего файлов: 1,247
- Справочники: 156
- Документы: 89
- Обработки: 234
- Формы: 567
- Модули: 201
```

### Поиск по контрактам

```bash
# Поиск по имени
python scripts/analyze.py --action search --query "ДокументыПредприятия"

# Поиск по типу
python scripts/analyze.py --action search --query "Справочник"

# Поиск по типу данных
python scripts/analyze.py --action search --query "Строка"
```

### Валидация контрактов

```bash
python scripts/analyze.py --action validate
```

**Результат**:
```
✅ Валидация контрактов:
- Проверено файлов: 1,247
- Успешно: 1,245
- Ошибок: 2
- Предупреждений: 15
```

## 🔍 Примеры логов

### Успешная генерация

```
🔄 Генерация контрактов метаданных...
  📖 Читаю отчет: C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt
  🧹 Очищаю целевую папку: C:\YourProject\YourConfig\metadata_contracts

📋 Сводка по генерации контрактов метаданных:
==================================================

🔍 info (3):
  • Прочитано строк: 125847
  • Найден объект: Справочники.ДокументыПредприятия
  • Найден объект: Справочники.Номенклатура

🔍 success (156):
  • Создан контракт: ДокументыПредприятия
  • Создан контракт: Номенклатура
  • ... и еще 154 сообщений

🔍 summary (1):
  • Обработано объектов: 156, успешно: 156
==================================================
```

### Генерация с ошибками

```
🔄 Генерация контрактов форм...
  🧹 Очищаю целевую папку: C:\YourProject\YourConfig\metadata_contracts\Формы

📋 Сводка по генерации контрактов форм:
==================================================

🔍 info (3):
  • Найдено 150 файлов форм по паттерну: **/Forms/*.xml
  • Найдено 45 файлов форм по паттерну: **/Forms/*/*.xml
  • Всего найдено уникальных файлов форм: 180

🔍 success (175):
  • Создан контракт: рлф_ФормаСпискаСПапками
  • Создан контракт: ФормаОбъекта
  • ... и еще 173 сообщений

🔍 warning (5):
  • Не найден элемент Form в файле: Template.xml
  • Ошибка при парсинге элементов формы: Invalid XML

🔍 summary (1):
  • Обработано файлов: 180, успешно: 175
==================================================
```

## 🧪 Примеры тестирования

### Запуск всех тестов

```bash
python scripts/test.py
```

**Результат**:
```
🧪 Запуск тестов...
✅ Тест launcher: PASSED
✅ Тест metadata_generator: PASSED
✅ Тест form_generator: PASSED
✅ Тест module_generator: PASSED
✅ Все тесты пройдены успешно
```

### Тестирование с покрытием

```bash
python -m pytest tests/ --cov=src --cov-report=html
```

**Результат**:
```
---------- coverage: platform win32, python 3.9.0-final-0 -----------
Name                           Stmts   Miss  Cover
--------------------------------------------------
src/core/launcher.py             45      2    96%
src/core/metadata_generator.py   89      5    94%
src/core/form_generator.py       67      3    96%
src/core/module_generator.py     34      1    97%
--------------------------------------------------
TOTAL                           235     11    95%
```

## 🔧 Примеры настройки

### Настройка кодировки (Windows)

```bash
# В командной строке
set PYTHONIOENCODING=utf-8
python scripts/generate.py

# В PowerShell
$env:PYTHONIOENCODING="utf-8"
python scripts/generate.py
```

### Настройка путей

```bash
# Абсолютные пути (рекомендуется)
python scripts/generate.py --auto \
  --conf-dir "C:\absolute\path\to\conf_files" \
  --report-path "C:\absolute\path\to\report.txt"

# Относительные пути
python scripts/generate.py --auto \
  --conf-dir "conf_files" \
  --report-path "conf_report\report.txt"
```

## 📈 Примеры интеграции

### Интеграция в CI/CD

```yaml
# .github/workflows/generate-contracts.yml
name: Generate 1C Contracts

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  generate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Generate contracts
      run: |
        python scripts/generate.py --auto \
          --conf-dir "conf_files" \
          --report-path "conf_report/report.txt" \
          --output-dir "generated_contracts"
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: contracts
        path: generated_contracts/
```

### Интеграция в скрипт сборки

```bash
#!/bin/bash
# build.sh

echo "🚀 Генерация контрактов 1С..."

# Генерация контрактов
python scripts/generate.py --auto \
  --conf-dir "conf_files" \
  --report-path "conf_report/report.txt" \
  --output-dir "generated_contracts"

# Проверка результатов
if [ $? -eq 0 ]; then
    echo "✅ Контракты сгенерированы успешно"
    
    # Анализ результатов
    python scripts/analyze.py --action stats
    
    # Валидация
    python scripts/analyze.py --action validate
else
    echo "❌ Ошибка генерации контрактов"
    exit 1
fi
```

## 🎯 Лучшие практики

### 1. Структура проекта

```
project/
├── conf_files/                    # Файлы конфигурации
│   ├── Catalogs/
│   ├── Documents/
│   └── Forms/
├── conf_report/                   # Отчеты
│   └── ОтчетПоКонфигурации.txt
├── generated_contracts/           # Сгенерированные контракты
│   ├── Справочники/
│   ├── Документы/
│   ├── Формы/
│   └── Модули/
└── onec-contract-generator/       # Система генерации
```

### 2. Версионирование

```bash
# Создание версии контрактов
cp -r generated_contracts/ contracts_v1.0.0/

# Сравнение версий
diff -r contracts_v1.0.0/ contracts_v1.1.0/
```

### 3. Автоматизация

```bash
# Скрипт для регулярной генерации
#!/bin/bash
# daily_generation.sh

DATE=$(date +%Y%m%d)
OUTPUT_DIR="contracts_${DATE}"

python scripts/generate.py --auto \
  --conf-dir "conf_files" \
  --report-path "conf_report/report.txt" \
  --output-dir "${OUTPUT_DIR}"

# Архивирование
tar -czf "${OUTPUT_DIR}.tar.gz" "${OUTPUT_DIR}"
```

---

**Для получения дополнительной информации см. [USAGE.md](USAGE.md) и [API.md](API.md)** 