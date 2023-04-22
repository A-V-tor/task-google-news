import random
import sqlite3
import time
from datetime import datetime
from multiprocessing import Pool, Lock

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = 'https://news.google.com/home'
ROOT_URL = 'https://news.google.com'


def get_list_links(url, root_url):
    """Получение списка новостных ссылок.

    Args:
        url: страница с набором ссылок на новости,
        root_url: часть адреса для построения ссылки

    Returns:
        list_links (list): список ссылок

    """
    session = requests.Session()
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    list_data_for_links = soup.find_all('a')
    list_links = []

    for i in list_data_for_links:
        try:
            chunk_links = i.get('href')[1:]
            if 'articles' in chunk_links:
                list_links.append(root_url + chunk_links)
        except Exception as error:
            print(error)

    return list_links


def fill_database():
    """Создание бд, таблицы и последующее

    наполнение данными.

    """
    conn = sqlite3.connect('profile.db')
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS Cookie_Profile (
    id INTEGER PRIMARY KEY NOT NULL,
    created_at DATETIME NOT NULL,
    cookie_value TEXT,
    last_run_at DATETIME,
    number_of_runs INTEGER DEFAULT 0
    )
    """
    )
    conn.commit()

    # если записи уже есть, функция возвращвет управление
    records = cursor.execute("""SELECT * FROM Cookie_Profile""").fetchall()
    if records:
        return None

    # елси записи отсутствуют, добавляем
    date = datetime.now()
    data = [(date, date) for i in range(15)]
    cursor.executemany(
        'INSERT INTO Cookie_Profile (created_at, last_run_at) VALUES (?, ?)',
        data,
    )
    conn.commit()
    conn.close()


def get_driver_browser():
    """Настройка драйвера для браузера

    Returns:
        driver (str): driver  для запросов
    """

    options = Options()

    # задаем работу браузера без gui
    options.add_argument('--headless')

    return webdriver.Chrome(options=options)


def get_cookie(row):
    """Получение cookies.

    Args:
        row (tuple): кортеж данных записи из бд

    Returns:
        str: cookie
    """
    driver = get_driver_browser()

    # Если есть cookie, передаем их в сессию
    if row[2]:
        driver.get(ROOT_URL)
        for cookie in row[2].split('; '):
            name, value = cookie.split('=', 1)
            driver.add_cookie({'name': name, 'value': value})

    random_link = random.choice(get_list_links(URL, ROOT_URL))
    driver.get(random_link)

    # скролл страницы
    for i in range(2):
        driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);'
        )
        time.sleep(random.uniform(0.5, 2.0))

    # сборка cookies
    cookie_dict = {}

    for cookie in driver.get_cookies():
        cookie_dict[cookie['name']] = cookie['value']

    driver.quit()

    return '; '.join(
        [f'{name}={value}' for name, value in cookie_dict.items()]
    )


def update_entries(id):
    """Обновление записи бд (cookie, last_run_at, number_of_runs).

    Args:
        id (int): id записи (профиля)

    """
    t1 = time.time()
    lock = Lock()

    # блокируем подключение к бд
    with lock:
        conn = sqlite3.connect('profile.db')
        cursor = conn.cursor()
        row = cursor.execute(
            f"""SELECT * FROM Cookie_Profile WHERE id = {id}"""
        ).fetchone()
        cookie = get_cookie(row)
        date = datetime.now()
        cursor.execute(
            f"""UPDATE Cookie_Profile SET cookie_value = "{cookie}", last_run_at = "{date}", number_of_runs = number_of_runs + 1  WHERE id = {id}"""
        )
        conn.commit()
        conn.close()
        t2 = time.time()
        print(f'Запись с id {id} обновлена за {t2 - t1} секунд')


def view_all_entries():
    """Проход по всем записям бд."""

    pool = Pool(processes=min(15, 5))
    pool.map(update_entries, range(1, 16))
    pool.close()
    pool.join()


def main():
    """Обьединение логики модуля."""

    try:
        t1 = time.time()
        view_all_entries()
        t2 = time.time()
        print(f'Задача завершена!\n {t2 - t1} секунд')

    except Exception as e:
        return e


if __name__ == '__main__':
    fill_database()
    main()
