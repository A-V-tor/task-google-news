## Тестовое задание:


Задача:
Создать проект на базе SQLite,Requests,Selenium,Multiprocessing.
Получаем свежие новости из google, создаем потоки на каждый профиль, создаем сессию используя уже имеющиеся Cookie, переходим и листаем новости после чего добавляем новые Cookie в базу данных.

Модуль SQLite
- Создаем базу данных Profile
- Создаем таблицу Cookie Profile:
* Уникальной id для каждой строки (Not NULL)
* Дата и время создания записи (Not NULL)
* Значения Cookie
* Дата и время последнего запуска
* Кол-во всего запусков
- Заполняем таблицу 15 значениями (id, текущая дата и время создания)

Модуль Requests
- GET запросом получаем содержимое страницы (https://news.google.com/home)
- Собираем в массив, ссылки на новости ( пример : https://news.google.com/articles/CBMi….)

Модуль Selenium
- Создаем сессию (если Cookie переданы, передаем их)
- Переходим по рандомной ссылке из массива модуля Requests
- Прокручиваем страницу с рандомной задержкой
- Сохраняем Cookie в SQLite (обновляем значения профиля)
- Закрываем сессию

Модуль Multiprocessing
- Собираем профиля из таблицы Cookie Profile (кол-во потоков)
- Используем Pool для создания потоков на каждый профиль
- Ограничение 5 одновременных потоков

<h1 align="center">Развертывание проекта</h1>

<h2>Скачать проект</h2>

```
  git clone git@github.com:A-V-tor/task-google-news.git
```

```
  cd task-google-news
```

<h2> Создать виртуальное окружение и установить зависимости</h2>

```
    python -m venv venv
    source venv/bin/activate
    
```
`python -m pip install -r requirements.txt` </br> </br>
<p> Скрипт работает через браузер Google Chrome</p>

```
    python -i task_google_news/main.py
    
```

<img src="https://github.com/A-V-tor/task-google-news/blob/main/image.png"></br>
<h3>Пример базы данных</h3>
<img src="https://github.com/A-V-tor/task-google-news/blob/main/db.png">
