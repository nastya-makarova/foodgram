# Foodgram

## Описание проекта
### «Фудграм» — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Подготовка и запуск проекта на удаленном сервере

+ ### Установите на удаленный сервер docker и docker-compose.
```
sudo apt install docker.io
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
+ ### Создайте на удаленном сервере папку ~/foodgram. Находясь в домашней директории:
```
mkdir foodgram/
```
+ ### Скопируйте на удаленный серевер файл с переменными .env:
```
scp -i <path/to/ssh-key/ssh-file> <path/to/.env> <username>@<host>:/home/<username>/foodgram/
```
+ ### Файл .env содержит:
  * POSTGRES_USER=<имя пользователя>
  * POSTGRES_PASSWORD=<пароль пользователя>
  * POSTGRES_DB=<имя базы данных>
  * DB_HOST=<db>
  * DB_PORT=<5432>
  * ALLOWED_HOSTS=<список допустимых хостов или IP-адресов>
  * DEBUG=<определяет включен ли режим отладки в вашем Django-проекте>
  * SECRET_KEY=<секретный ключ проекта django>
  * HOST_NAME=<server name>

+ ### Для деплоя на удаленный сервер используется GitHub Actions. Workflow состоит из следующих шагов.
  * Проверка кода бэкенда с помощью flake8
  * Сборка и публикация образов бекенда и фронтенда на DockerHub.
  * Автоматический деплой на удаленный сервер.

+ ### Добавьте переменные окружения в Secrets GitHub:
  * DOCKER_PASSWORD=<пароль DockerHub>
  * DOCKER_USERNAME=<имя пользователя DockerHub>
  * USER=<username для подключения к серверу>
  * HOST=<IP сервера>
  * SSH_PASSPHRASE=<пароль для сервера, если он установлен>
  * SSH_KEY=<ваш приватный SSH ключ>

## Создать суперпользователя Django:
```
pyhton manage.py createsuperuser
```

## Загрузите ингредиенты в базу данных.
```
pyhton manage.py load_csv_data
```

### Проект доступен по [ссылке](https://yafoodgram.zapto.org)

## Технологии, которые применены в этом проекте:
* Python
* Django
* Django REST Framework
* Djoser

## Автор проекта: [Анастасия Макарова](https://github.com/nastya-makarova)