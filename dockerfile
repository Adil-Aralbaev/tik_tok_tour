# Используем минимальный образ Python
FROM python:3.11-slim

# Устанавливаем системные зависимости (для Pillow и сборки пакетов)
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта внутрь контейнера
COPY . .

RUN python manage.py collectstatic --noinput

# Переменные окружения (чтобы Python не кэшировал pyc и выводил stdout сразу)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Открываем порт для Django (8000)
EXPOSE 8000

# Команда запуска через gunicorn
CMD ["gunicorn", "my_project.wsgi:application", "--bind", "0.0.0.0:80"]

VOLUME /app/staticfiles