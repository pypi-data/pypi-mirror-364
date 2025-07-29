# 📖 Руководство по использованию

## 🚀 Быстрый старт

### 1. Установка

#### Установка с PyPI (рекомендуется)

```bash
pip install onec-contract-generator
```

#### Установка для разработки

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd onec-contract-generator

# Установка в режиме разработки
pip install -e ".[dev]"

# Или установка зависимостей вручную
pip install -r requirements-dev.txt
```

#### Ручной запуск без pip

Если вы хотите запустить генератор без установки через pip:

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd onec-contract-generator

# Установите зависимости (если нужно)
pip install -r requirements.txt

# Запуск через Python скрипты
python scripts/generate.py

# Или через модули напрямую
python -m src.core.launcher

# Или с параметрами
python scripts/generate.py --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts"
```

### 2. Подготовка данных

Убедитесь, что у вас есть:
- Файлы конфигурации 1С в папке `conf_files/`
- Текстовый отчет конфигурации в `conf_report/ОтчетПоКонфигурации.txt`

### 3. Запуск генерации

#### Интерактивный режим (рекомендуется для начала)

```bash
onec-contract-generate
```

Следуйте пошаговому мастеру:
1. Выберите директорию конфигурации
2. Выберите файл отчета
3. Выберите выходную директорию
4. Выберите компоненты для генерации
5. Подтвердите настройки

#### Командный режим

```bash
onec-contract-generate --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts"
```

### 4. Анализ результатов

```bash
# Статистика
onec-contract-analyze --action stats

# Поиск по контрактам
onec-contract-analyze --action search --query "ДокументыПредприятия"

# Валидация
onec-contract-analyze --action validate
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

После генерации в выходной директории создается плоская структура с префиксами типов:

```
metadata_contracts/
├── Справочник_Номенклатура.json
├── Справочник_ДокументыПредприятия.json
├── Документ_ЗаказНаряды.json
├── Документ_ПоступлениеТоваров.json
├── Обработка_Обработка1.json
├── Обработка_Обработка2.json
├── Форма_рлф_ФормаСпискаСПапками.json
├── Форма_ФормаОбъекта.json
├── Модуль_ДокументыПредприятия_ModuleContract.json
└── Модуль_Номенклатура_ModuleContract.json
```

### Структура контракта метаданных

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

## 🎯 Примеры использования

### Пример 1: Генерация всех контрактов

```bash
onec-contract-generate --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts"
```

### Пример 2: Только контракты метаданных

```bash
onec-contract-generate --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --report-path "C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts" \
  --skip-forms \
  --skip-modules
```

### Пример 3: Только контракты форм

```bash
onec-contract-generate --auto \
  --conf-dir "C:\YourProject\YourConfig\conf_files" \
  --output-dir "C:\YourProject\YourConfig\metadata_contracts" \
  --skip-metadata \
  --skip-modules
```

### Пример 4: Интерактивный режим

```bash
onec-contract-generate
```

Система задаст вопросы:
```
🚀 OneC Contract Generator
==================================================

📁 Директория конфигурации: C:\YourProject\YourConfig\conf_files
📄 Файл отчета: C:\YourProject\YourConfig\conf_report\ОтчетПоКонфигурации.txt
📂 Выходная директория: C:\YourProject\YourConfig\metadata_contracts

🔧 Выберите компоненты для генерации:
✅ Контракты метаданных
✅ Контракты форм
❌ Контракты модулей

🎯 Подтвердите настройки (y/N): y
```

## 📁 Поддерживаемые типы объектов 1С

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

## 🔍 Анализ и поиск

### Статистика контрактов

```bash
# Через pip установку
onec-contract-analyze --action stats

# Или ручной запуск
python scripts/analyze.py --action stats
```

Вывод:
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
  ...

📈 Общий размер: 45.6 MB
```

### Поиск по контрактам

```bash
# Через pip установку
onec-contract-analyze --action search --query "Номенклатура"

# Или ручной запуск
python scripts/analyze.py --action search --query "Номенклатура"
```

### Валидация контрактов

```bash
# Через pip установку
onec-contract-analyze --action validate

# Или ручной запуск
python scripts/analyze.py --action validate
```

## 🛠️ Конфигурация

### Переменные окружения

- `ONEC_DEBUG` - включить отладочный режим
- `ONEC_LOG_LEVEL` - уровень логирования (INFO, WARNING, ERROR)

### Структура входных данных

```
project/
├── conf_files/                    # Файлы конфигурации
│   ├── Catalogs/
│   ├── Documents/
│   └── Forms/
├── conf_report/                   # Отчеты конфигурации
│   └── ОтчетПоКонфигурации.txt
└── metadata_contracts/            # Выходные контракты
```

## 🚨 Устранение проблем

### Проблема: Кодировка в Windows
```bash
# Решение: Установить переменную окружения
set PYTHONIOENCODING=utf-8
onec-contract-generate
```

### Проблема: Пути к файлам
```bash
# Решение: Использовать абсолютные пути
onec-contract-generate --auto \
  --conf-dir "C:\absolute\path\to\conf_files" \
  --report-path "C:\absolute\path\to\report.txt"
```

### Проблема: Отсутствие файлов
```bash
# Решение: Проверить структуру проекта
ls -la
onec-contract-test
```

### Проблема: Ошибки парсинга форм
```bash
# Решение: Проверить XML файлы форм
# Система автоматически группирует ошибки в логах
```

## 📊 Результаты тестирования

### ✅ **Успешно протестировано на реальных данных:**
- **Конфигурация**: YourProject (33MB отчет)
- **Модули**: 3,451 объект обработан
- **Формы**: Множество форм создано
- **Метаданные**: Структурированные контракты

### 📋 **Группировка логов:**
- **info**: Информационные сообщения
- **success**: Успешно обработанные файлы
- **warning**: Предупреждения
- **error**: Ошибки обработки
- **summary**: Сводки по результатам

## 🔗 Связанные документы

- [📖 Полная документация](../README.md)
- [📋 Примеры использования](EXAMPLES.md)
- [🔧 API документация](API.md)
- [🛠️ Руководство разработчика](DEVELOPMENT.md) 