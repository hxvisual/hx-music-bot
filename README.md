# 🎵 HX Music Bot

<div align="center">

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![aiogram 3.0+](https://img.shields.io/badge/aiogram-3.0%2B-blue?style=for-the-badge)
![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)
![License MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

<hr>

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

<hr>

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

<hr>

### Настройка автообновления

1. Перейдите в настройки вашего GitHub репозитория (вкладка Settings)
2. В боковом меню выберите "Secrets and variables" → "Actions"
3. Нажмите кнопку "New repository secret"
4. Добавьте следующие секреты:
   - `SSH_HOST`: IP-адрес вашего сервера (например, 123.45.67.89)
   - `SSH_USERNAME`: имя пользователя SSH для подключения к серверу
   - `SSH_PRIVATE_KEY`: содержимое приватного SSH ключа (весь файл ~/.ssh/id_rsa)
   - `SSH_PORT`: порт SSH (обычно 22, но может быть изменен в настройках сервера)
   - `PROJECT_PATH`: полный путь к директории проекта на сервере (например, /home/username/hx-music-bot)

Эти секреты будут использоваться в GitHub Actions workflow для безопасного подключения к вашему серверу и обновления бота.

При каждом push в ветку `main` будет выполняться автоматическое обновление бота на сервере.

<hr>

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

<hr>

<div align="center">
  Сделано с ❤️ by <a href="https://github.com/hxvisual">hxvisual</a>
</div> 