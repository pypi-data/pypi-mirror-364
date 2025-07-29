# 🚀 Руководство по публикации на PyPI

## 📋 Подготовка к публикации

### 1. Установка необходимых инструментов

```bash
# Основные инструменты
pip install build twine

# Для разработки
pip install -r requirements-dev.txt
```

### 2. Проверка конфигурации

Убедитесь, что все файлы настроены правильно:

- ✅ `setup.py` - основная конфигурация
- ✅ `pyproject.toml` - современная конфигурация
- ✅ `MANIFEST.in` - файлы для включения
- ✅ `requirements.txt` - продакшн зависимости
- ✅ `requirements-dev.txt` - dev зависимости

### 3. Тестирование

```bash
# Запуск тестов
python scripts/test.py

# Или с pytest
pytest tests/

# Проверка качества кода
black src/ tests/
flake8 src/ tests/
mypy src/
```

## 🏗️ Сборка пакета

### Автоматическая сборка

```bash
# Используйте готовый скрипт
python scripts/publish.py
```

### Ручная сборка

```bash
# Очистка старых сборок
rm -rf build/ dist/ *.egg-info/

# Сборка пакета
python -m build

# Проверка пакета
twine check dist/*
```

## 📦 Публикация

### 1. TestPyPI (рекомендуется для тестирования)

```bash
# Загрузка на TestPyPI
twine upload --repository testpypi dist/*

# Установка с TestPyPI для проверки
pip install --index-url https://test.pypi.org/simple/ onec-contract-generator
```

### 2. PyPI (продакшн)

```bash
# Загрузка на PyPI
twine upload dist/*
```

## 🔐 Настройка учетных данных

### Создание токенов

1. Зарегистрируйтесь на [PyPI](https://pypi.org/account/register/)
2. Создайте API токен в настройках аккаунта
3. Сохраните токен в `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token-here
```

## 📝 Чек-лист перед публикацией

### ✅ Конфигурация
- [ ] Версия обновлена в `setup.py` и `src/_version.py`
- [ ] Описание проекта актуально
- [ ] Классификаторы настроены правильно
- [ ] Зависимости указаны корректно

### ✅ Код
- [ ] Все тесты проходят
- [ ] Код отформатирован (black)
- [ ] Линтер не выдает ошибок (flake8)
- [ ] Типы проверены (mypy)

### ✅ Документация
- [ ] README.md актуален
- [ ] Примеры работают
- [ ] Документация обновлена

### ✅ Пакет
- [ ] Пакет собирается без ошибок
- [ ] Все файлы включены в MANIFEST.in
- [ ] Пакет проверен (twine check)

## 🎯 Команды для быстрой публикации

```bash
# Полный цикл публикации
python scripts/publish.py

# Или пошагово:
rm -rf build/ dist/ *.egg-info/
python -m build
twine check dist/*
twine upload --repository testpypi dist/*  # Тест
twine upload dist/*  # Продакшн
```

## 🆘 Решение проблем

### Ошибка "File already exists"
```bash
# Удалите старую версию или увеличьте номер версии
rm -rf build/ dist/ *.egg-info/
```

### Ошибка аутентификации
```bash
# Проверьте токен в ~/.pypirc
# Или используйте интерактивный ввод
twine upload --username your-username dist/*
```

### Ошибка "Invalid distribution"
```bash
# Проверьте пакет
twine check dist/*
# Исправьте ошибки и пересоберите
```

## 📊 Мониторинг

После публикации проверьте:

1. **PyPI**: https://pypi.org/project/onec-contract-generator/
2. **Установка**: `pip install onec-contract-generator`
3. **Импорт**: `python -c "import onec_contract_generator; print('OK')"`

## 🔄 Обновление версии

Для новой версии:

1. Обновите версию в `setup.py` и `src/_version.py`
2. Обновите `CHANGELOG.md`
3. Соберите и опубликуйте пакет

```bash
# Пример обновления версии
sed -i 's/version="2.1.0"/version="2.1.1"/' setup.py
sed -i 's/__version__ = "2.1.0"/__version__ = "2.1.1"/' src/_version.py
python scripts/publish.py
```

---

**Удачи с публикацией! 🚀** 