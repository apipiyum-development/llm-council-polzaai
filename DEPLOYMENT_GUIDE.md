# Полное руководство по установке LLM Council на сервер

## Часть 1: Подготовка и публикация на GitHub

### 1.1. Подготовка проекта для публикации

1. Убедитесь, что все изменения внесены в проект:
   - docker-compose.yml с правильной конфигурацией
   - nginx.conf для внутренней маршрутизации
   - Dockerfiles для backend и frontend
   - Обновленные конфигурации CORS и API
   - README.md с инструкциями

2. Создайте файл `.gitignore`, если он не существует:
   ```
   .env
   .env.local
   .env.development
   .env.production
   node_modules/
   __pycache__/
   *.pyc
   *.pyo
   *.pyd
   .pytest_cache/
   .coverage
   htmlcov/
   .venv/
   venv/
   .env*
   !.env.example
   data/conversations/
   ```

3. Создайте пример файла конфигурации `.env.example`:
   ```
   POLZAAI_API_KEY=your-polzaai-api-key-here
   ```

4. Убедитесь, что в репозитории нет чувствительных данных:
   - Удалите все .env файлы из репозитория
   - Проверьте, что в git не попали API-ключи

5. Зафиксируйте изменения и залейте на GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: LLM Council with server deployment configuration"
   git remote add origin https://github.com/your-username/llm-council.git
   git branch -M main
   git push -u origin main
   ```

## Часть 2: Установка на сервер

### 2.1. Подготовка сервера

1. Подключитесь к серверу по SSH:
   ```bash
   ssh user@your-server-ip
   ```

2. Установите Docker и Docker Compose:
   ```bash
   # Обновление системы
   sudo apt update && sudo apt upgrade -y
   
   # Установка Docker
   sudo apt install ca-certificates curl gnupg lsb-release -y
   sudo mkdir -p /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt update
   sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin
   sudo usermod -aG docker $USER
   ```

3. Перезайдите в сессию SSH, чтобы изменения группы вступили в силу:
   ```bash
   exit
   ssh user@your-server-ip
   ```

4. Установите Git:
   ```bash
   sudo apt install git -y
   ```

### 2.2. Клонирование репозитория

1. Создайте директорию для приложения:
   ```bash
   mkdir -p ~/apps
   cd ~/apps
   ```

2. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-username/llm-council.git
   cd llm-council
   ```

## Часть 3: Настройка домена и SSL

### 3.1. Настройка DNS

1. Убедитесь, что домен `llm.clusterdev.ru` направлен на IP-адрес вашего сервера.
   Это делается в настройках DNS вашего доменного регистратора.

### 3.2. Установка и настройка Traefik (если его нет)

Если у вас уже есть n8n с Traefik, пропустите этот шаг и перейдите к разделу 3.3.

1. Создайте директорию для Traefik:
   ```bash
   mkdir -p ~/traefik
   cd ~/traefik
   ```

2. Создайте файл конфигурации Traefik `traefik.yml`:
   ```yaml
   api:
     dashboard: true
     insecure: true

   entryPoints:
     web:
       address: ":80"
       http:
         redirections:
           entryPoint:
             to: websecure
             scheme: https
     websecure:
       address: ":443"

   providers:
     docker:
       endpoint: "unix:///var/run/docker.sock"
       exposedByDefault: false
     file:
       directory: /etc/traefik/config
       watch: true

   certificatesResolvers:
     myresolver:
       acme:
         email: your-email@example.com
         storage: /etc/traefik/acme.json
         httpChallenge:
           entryPoint: web
   ```

3. Создайте пустой файл для хранения сертификатов:
   ```bash
   sudo touch ~/traefik/acme.json
   sudo chmod 600 ~/traefik/acme.json
   ```

4. Создайте docker-compose.yml для Traefik:
   ```yaml
   version: '3.8'

   services:
     traefik:
       image: traefik:v2.9
       restart: always
       command:
         - "--configfile=/etc/traefik/traefik.yml"
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - /var/run/docker.sock:/var/run/docker.sock
         - ./traefik.yml:/etc/traefik/traefik.yml
         - ./acme.json:/etc/traefik/acme.json

   networks:
     default:
       external:
         name: traefik_default  # или создайте новую сеть: traefik_public
   ```

5. Запустите Traefik:
   ```bash
   # Создаем сеть для Traefik
   docker network create traefik_default
   
   # Запускаем Traefik
   docker-compose up -d
   ```

### 3.3. Если Traefik уже установлен для n8n

Если у вас уже установлен Traefik для n8n, то он уже слушает на портах 80 и 443, и LLM Council будет использовать тот же экземпляр Traefik для маршрутизации.

## Часть 4: Настройка LLM Council

### 4.1. Подготовка конфигурационных файлов

1. Создайте файл `.env` в корне проекта:
   ```bash
   cd ~/apps/llm-council
   nano .env
   ```
   
   Добавьте ваш API-ключ:
   ```
   POLZAAI_API_KEY=ваш-ключ-от-polzaai
   ```

2. Убедитесь, что в `docker-compose.yml` присутствуют правильные метки для Traefik:
   ```yaml
   services:
     llm-council-nginx:
       # ... остальные настройки ...
       labels:
         - "traefik.enable=true"
         - "traefik.http.routers.llm-council.entrypoints=web,websecure"
         - "traefik.http.routers.llm-council.rule=Host(`llm.clusterdev.ru`)"
         - "traefik.http.routers.llm-council.tls=true"
         - "traefik.http.routers.llm-council.tls.certresolver=myresolver"
         - "traefik.http.services.llm-council.loadbalancer.server.port=8080"
   ```

### 4.2. Запуск приложения

1. Убедитесь, что вы находитесь в директории проекта:
   ```bash
   cd ~/apps/llm-council
   ```

2. Запустите приложение:
   ```bash
   docker-compose up -d
   ```

3. Проверьте статус контейнеров:
   ```bash
   docker-compose ps
   ```

4. Проверьте логи, если что-то пошло не так:
   ```bash
   docker-compose logs -f
   ```

## Часть 5: Проверка установки

### 5.1. Проверка доступности

1. Дождитесь получения SSL-сертификата (это может занять несколько минут)
2. Откройте в браузере: `https://llm.clusterdev.ru`
3. Убедитесь, что приложение загружается и кнопки работают

### 5.2. Проверка функциональности

1. Отправьте тестовый запрос
2. Убедитесь, что все 3 стадии (Stage 1, Stage 2, Stage 3) работают
3. Проверьте, что кнопки и интерфейс корректно реагируют

## Часть 6: Мониторинг и обслуживание

### 6.1. Проверка состояния сервиса

```bash
# Проверить статус контейнеров
docker-compose ps

# Посмотреть логи
docker-compose logs

# Посмотреть логи конкретного сервиса
docker-compose logs llm-council-nginx
```

### 6.2. Обновление приложения

1. Остановите текущее приложение:
   ```bash
   docker-compose down
   ```

2. Обновите код из репозитория:
   ```bash
   git pull origin main
   ```

3. Пересоберите и запустите:
   ```bash
   docker-compose up -d --build
   ```

### 6.3. Резервное копирование

Для резервного копирования переписок:
```bash
# Создайте архив с переписками
tar -czf llm-conversations-backup-$(date +%Y%m%d).tar.gz data/conversations/
```

## Возможные проблемы и решения

### Проблема: SSL-сертификат не создается
Решение: Проверьте, что домен правильно направлен на сервер и что порты 80 и 443 не блокируются фаерволом.

### Проблема: Приложение не отвечает
Решение: Проверьте логи контейнеров и убедитесь, что все сервисы запущены:
```bash
docker-compose logs --tail=50
```

### Проблема: Ошибка CORS
Решение: Убедитесь, что в `backend/main.py` разрешены правильные домены.

## Безопасность

1. Убедитесь, что API-ключи не хранятся в открытом виде
2. Регулярно обновляйте Docker-образы
3. Используйте HTTPS для всех соединений
4. Проверьте настройки фаервола