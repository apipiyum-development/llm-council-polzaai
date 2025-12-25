FROM node:18-alpine as build

WORKDIR /app

# Копирование файлов
COPY frontend/package*.json ./
COPY frontend/ .

# Установка зависимостей
RUN npm install

# Сборка приложения
RUN npm run build

# Production stage
FROM nginx:alpine

# Копирование собранного приложения
COPY --from=build /app/dist /usr/share/nginx/html

# Удаление стандартной конфигурации nginx
RUN rm -v /etc/nginx/conf.d/default.conf

# Создание простой конфигурации для обслуживания статических файлов
RUN echo $'\
server { \
    listen 80; \
    server_name _; \
\
    root /usr/share/nginx/html; \
    index index.html; \
\
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]