# DualDoc Translator

Десктопное приложение для параллельной работы с двуязычными документами.

## Структура

- `packages/shared/` — общие модели, схемы API, формат `.dualtrans`
- `packages/backend/` — FastAPI-сервер (VPS)
- `packages/client/` — PySide6 десктоп-клиент
- `docs/` — документация, диаграммы, ТЗ
- `scripts/` — служебные скрипты
- `tests/` — интеграционные тесты

## Быстрый старт

```bash
git clone <repo-url>
cd DualDoc-Translator

# Бэкенд
cd packages/backend
pip install -e ../shared -e .
uvicorn dualdoc_backend.main:app --reload

# Клиент
cd packages/client
pip install -e ../shared -e .
python -m dualdoc_client.main
```

## Docker (бэкенд + БД + Redis)

```bash
docker compose up
```
