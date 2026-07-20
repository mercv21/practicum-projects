# Создать образ на основе базового слоя с Python 3.12
FROM python:3.12

# Переходим в образе в директорию /app
WORKDIR /app

# Устанавливаем gunicorn
RUN pip install gunicorn==25.3.0

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# Копируем весь код проекта
COPY . .

# Команда запуска (главное отличие!)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "kittygram_backend.wsgi"]
