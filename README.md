# 🎵 HX Music Bot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python" alt="Python 3.9+"/>
  <img src="https://img.shields.io/badge/aiogram-3.0%2B-blue?style=for-the-badge" alt="aiogram 3.0+"/>
  <img src="https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker" alt="Docker Ready"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License MIT"/>
</p>

## 🚀 Установка

### Локальная установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/hxvisual/hx-music-bot.git
cd hx-music-bot
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` со следующими параметрами:

```
BOT_TOKEN=ваш_токен_бота
ADMIN_IDS=id_администратора1,id_администратора2
```

4. Запустите бота:

```bash
python bot.py
```

### Установка на сервере

Для упрощения установки бота на сервере, используйте скрипт автоматической настройки:

1. Загрузите скрипт на сервер:

```bash
curl -O https://raw.githubusercontent.com/hxvisual/hx-music-bot/main/server_setup.sh
chmod +x server_setup.sh
```

2. Запустите скрипт:

```bash
./server_setup.sh
```

Скрипт выполнит все необходимые шаги:
- Обновит системные пакеты
- Установит Docker и Docker Compose
- Создаст директорию проекта
- Запросит необходимые данные (токен бота, ID администраторов)
- Настроит и запустит контейнеры Docker

### Настройка автообновления

Настройте следующие секреты в вашем GitHub репозитории:
   - `SSH_HOST`: IP-адрес вашего сервера
   - `SSH_USERNAME`: имя пользователя SSH
   - `SSH_PRIVATE_KEY`: приватный SSH ключ
   - `SSH_PORT`: порт SSH (обычно 22)
   - `PROJECT_PATH`: путь к директории проекта на сервере

При каждом push в ветку `main` будет выполняться автоматическое обновление бота на сервере.

## 🐳 Работа с Docker

### Основные команды Docker

```bash
# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Перезапуск бота
docker-compose restart

# Остановка бота
docker-compose down

# Обновление и перезапуск
git pull && docker-compose up -d --build
```


---

<p align="center">
  Сделано с ❤️ by <a href="https://github.com/hxvisual">hxvisual</a>
</p> 