set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}${BOLD}$1${NC}"
    echo -e "${BLUE}${BOLD}$(printf '=%.0s' {1..50})${NC}\n"
}

print_step() {
    echo -e "${YELLOW}➤ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

clear
echo -e "${BOLD}${GREEN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║                                                        ║"
echo "║   Установка и настройка Telegram бота на сервере       ║"
echo "║                                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "Этот скрипт автоматически настроит все необходимое для работы бота.\n"

print_header "ОБНОВЛЕНИЕ СИСТЕМЫ"
print_step "Обновление списка пакетов..."
sudo apt-get update
print_step "Установка обновлений..."
sudo apt-get upgrade -y
print_success "Система успешно обновлена"

print_header "УСТАНОВКА DOCKER"
if ! command -v docker &> /dev/null; then
    print_step "Установка необходимых зависимостей..."
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    print_step "Добавление ключа Docker GPG..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    print_step "Добавление репозитория Docker..."
    sudo add-apt-repository "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    print_step "Обновление списка пакетов..."
    sudo apt-get update
    print_step "Установка Docker..."
    sudo apt-get install -y docker-ce
    print_step "Настройка автозапуска Docker..."
    sudo systemctl enable docker
    sudo systemctl start docker
    print_step "Добавление текущего пользователя в группу docker..."
    sudo usermod -aG docker $USER
    print_success "Docker успешно установлен!"
else
    print_success "Docker уже установлен"
fi

print_header "УСТАНОВКА DOCKER COMPOSE"
if ! command -v docker-compose &> /dev/null; then
    print_step "Получение последней версии Docker Compose..."
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    print_step "Загрузка Docker Compose ${COMPOSE_VERSION}..."
    sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    print_step "Настройка прав доступа..."
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose успешно установлен!"
else
    print_success "Docker Compose уже установлен"
fi

print_header "НАСТРОЙКА ДИРЕКТОРИИ ПРОЕКТА"
PROJECT_DIR="$HOME/hx-music-bot"
print_step "Создание директории проекта в ${PROJECT_DIR}..."

if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p "$PROJECT_DIR"
    print_success "Директория создана"
else
    print_success "Директория уже существует"
fi

cd "$PROJECT_DIR"

print_header "НАСТРОЙКА ФАЙЛОВ ПРОЕКТА"
if [ -d "$PROJECT_DIR/.git" ]; then
    print_step "Обновление кода из репозитория..."
    git pull
    print_success "Репозиторий обновлен"
else
    print_step "Клонирование репозитория..."
    git clone https://github.com/hxvisual/hx-music-bot.git .
    print_success "Репозиторий склонирован"
fi

print_header "НАСТРОЙКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ"
print_step "Создание файла .env..."
    
echo -e "${YELLOW}Введите токен вашего бота (получить можно у @BotFather):${NC}"
read -p "> " BOT_TOKEN
while [ -z "$BOT_TOKEN" ]; do
    echo -e "${RED}Токен не может быть пустым. Пожалуйста, введите токен:${NC}"
    read -p "> " BOT_TOKEN
done

echo -e "${YELLOW}Введите SOUNDCLOUD_CLIENT_ID (можно получить, зарегистрировавшись на developers.soundcloud.com и создав приложение):${NC}"
read -p "> " SOUNDCLOUD_CLIENT_ID
while [ -z "$SOUNDCLOUD_CLIENT_ID" ]; do
    echo -e "${RED}SOUNDCLOUD_CLIENT_ID не может быть пустым. Пожалуйста, введите ID:${NC}"
    read -p "> " SOUNDCLOUD_CLIENT_ID
done

echo "BOT_TOKEN=$BOT_TOKEN" > .env
echo "ADMIN_IDS=$SOUNDCLOUD_CLIENT_ID" >> .env

print_success "Файл .env создан с вашими данными"

print_header "ЗАПУСК БОТА"
print_step "Остановка предыдущих контейнеров (если есть)..."
docker-compose down || true
print_step "Сборка и запуск контейнеров..."
docker-compose up -d --build
print_success "Контейнеры запущены"

print_header "УСТАНОВКА ЗАВЕРШЕНА"
print_success "Бот успешно настроен и запущен!"
echo -e "\n${YELLOW}Проверить логи бота можно командой:${NC} docker-compose logs -f"

echo -e "\n${BLUE}${BOLD}ДАЛЬНЕЙШИЕ ДЕЙСТВИЯ:${NC}"
echo -e "  ${GREEN}1. Для перезапуска бота:${NC} docker-compose restart"
echo -e "  ${GREEN}2. Для остановки бота:${NC} docker-compose down"
echo -e "  ${GREEN}3. Для просмотра логов:${NC} docker-compose logs -f"
echo -e "  ${GREEN}4. Для обновления кода с GitHub:${NC} git pull && docker-compose up -d --build"

echo -e "\n${BOLD}${GREEN}Спасибо за использование! Желаем успешной работы с ботом!${NC}\n" 