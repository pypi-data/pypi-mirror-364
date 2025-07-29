# 📖 Руководство по использованию

## 🚀 Быстрый старт

### 1. Подготовка данных

Убедитесь, что у вас есть:
- Файлы конфигурации 1С в папке `conf_files/`
- Текстовый отчет конфигурации в `conf_reports/FullReport.txt`

### 2. Запуск генерации

#### Интерактивный режим (рекомендуется для начала)

```bash
python scripts/generate.py
```

Следуйте пошаговому мастеру:
1. Выберите директорию конфигурации
2. Выберите файл отчета
3. Выберите выходную директорию
4. Выберите компоненты для генерации
5. Подтвердите настройки

#### Командный режим

```bash
python scripts/generate.py --auto \
  --conf-dir conf_files \
  --report-path conf_reports/FullReport.txt
```

### 3. Анализ результатов

```bash
# Статистика
python scripts/analyze.py --action stats

# Поиск по контрактам
python scripts/analyze.py --action search --query "ДокументыПредприятия"

# Валидация
python scripts/analyze.py --action validate
```

## 🔧 Параметры командной строки

### Основные параметры

- `--auto` - Автоматический режим (без интерактивных вопросов)
- `--conf-dir` - Директория с файлами конфигурации
- `--report-path` - Путь к файлу отчета по конфигурации
- `--output-dir` - Выходная директория для контрактов (по умолчанию: metadata_contracts)

### Параметры выборочной генерации

- `--skip-metadata` - Пропустить генерацию контрактов метаданных
- `--skip-forms` - Пропустить генерацию контрактов форм
- `--skip-modules` - Пропустить генерацию контрактов модулей

## 📊 Структура выходных данных

После генерации в выходной директории создается структура:

```
metadata_contracts/
├── Справочники/                    # Контракты метаданных справочников
│   ├── ДокументыПредприятия.json
│   └── Номенклатура.json
├── Документы/                      # Контракты метаданных документов
│   ├── ЗаказНаряды.json
│   └── ПоступлениеТоваров.json
├── Формы/                          # Контракты форм
│   ├── Справочник.ДокументыПредприятия.ФормаОбъекта.json
│   └── Справочник.ДокументыПредприятия.ФормаСписка.json
└── Модули/                         # Контракты модулей
    ├── ДокументыПредприятия_ModuleContract.json
    └── Номенклатура_ModuleContract.json
```

## 🎯 Примеры использования

### Пример 1: Генерация всех контрактов

```bash
python scripts/generate.py --auto \
  --conf-dir /path/to/conf_files \
  --report-path /path/to/conf_reports/FullReport.txt
```

### Пример 2: Только контракты метаданных

```bash
python scripts/generate.py --auto \
  --conf-dir conf_files \
  --report-path conf_reports/FullReport.txt \
  --skip-forms --skip-modules
```

### Пример 3: Только контракты форм

```bash
python scripts/generate.py --auto \
  --conf-dir conf_files \
  --report-path conf_reports/FullReport.txt \
  --skip-metadata --skip-modules
```

### Пример 4: Анализ сгенерированных контрактов

```bash
# Получить статистику
python scripts/analyze.py --action stats

# Найти все справочники
python scripts/analyze.py --action search --query "Справочник"

# Проверить качество контрактов
python scripts/analyze.py --action validate

# Создать отчет
python scripts/analyze.py --action report --output analysis.md
```

## 🔍 Анализ контрактов

### Действия анализа

- `stats` - Статистика по контрактам
- `search` - Поиск по контрактам
- `validate` - Валидация качества контрактов
- `report` - Генерация отчета

### Примеры поиска

```bash
# Поиск по имени объекта
python scripts/analyze.py --action search --query "ДокументыПредприятия"

# Поиск по типу данных
python scripts/analyze.py --action search --query "СправочникСсылка"

# Поиск по типу объекта
python scripts/analyze.py --action search --query "Документ"
```

## 🧪 Тестирование

### Запуск всех тестов

```bash
python scripts/test.py
```

### Запуск конкретных тестов

```bash
# Тесты запускатора
python -m pytest tests/test_launcher.py -v

# Тесты генераторов
python -m pytest tests/test_generators.py -v

# Тесты утилит
python -m pytest tests/test_utils.py -v
```

### Тестирование с покрытием

```bash
python -m pytest tests/ --cov=src --cov-report=html
```

## 🚨 Устранение проблем

### Проблема: "Файл отчета не найден"

```bash
# Проверьте путь к файлу
ls -la conf_reports/

# Используйте абсолютный путь
python scripts/generate.py --auto \
  --conf-dir /absolute/path/to/conf_files \
  --report-path /absolute/path/to/conf_reports/FullReport.txt
```

### Проблема: "Директория конфигурации не найдена"

```bash
# Проверьте структуру папок
ls -la conf_files/

# Создайте необходимые папки
mkdir -p conf_files/Catalogs conf_files/Documents conf_files/Forms
```

### Проблема: Кодировка в Windows

```bash
# Установите переменную окружения
set PYTHONIOENCODING=utf-8

# Или запустите в PowerShell
$env:PYTHONIOENCODING="utf-8"
python scripts/generate.py
```

### Проблема: Ошибки импорта

```bash
# Проверьте структуру проекта
ls -la src/core/

# Убедитесь, что вы в корне проекта
pwd
ls -la scripts/
```

## 📋 Чек-лист перед использованием

- [ ] Python 3.7+ установлен
- [ ] Файлы конфигурации подготовлены
- [ ] Текстовый отчет сгенерирован
- [ ] Структура папок создана
- [ ] Переменные окружения настроены (для Windows)

## 🎯 Лучшие практики

1. **Всегда используйте интерактивный режим для первого запуска**
2. **Проверяйте пути к файлам перед запуском**
3. **Анализируйте результаты после генерации**
4. **Сохраняйте резервные копии исходных данных**
5. **Используйте версионирование для контрактов** 