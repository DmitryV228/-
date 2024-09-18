#Пожауйста установите необходимые библиотеки
#!pip install requests
#!pip install bs4
#!pip install fake_useragent

import re
import requests
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
import psycopg2
import random
from functools import lru_cache
import datetime
import sys
import time

#Исходные данные для дальнейшей работы
headers = {"User-Agent": UserAgent().random}
proxies = {'https': f'http://TKuHHH:Nwjxdt@147.45.202.117:8000'}
url = 'https://snkhan.co.uk/stuff/iTunes.php?chart=RU'
url1 = 'https://music.yandex.ru/chart'

#Парсинг первого сайта для получения списков альбомов, песен, музыкантов, жанров, дат выхода и мест в чарте
@lru_cache(None)
def songs_info(url):
    c = 0
    song_name_info_list = []
    album_info_list = []
    artists_info_list = []
    genre_info_list = []
    release_date_list = []
    respounse = requests.get(url=url, headers=headers)
    soup = BS(respounse.text, 'lxml')
    section_main = soup.find('section', {'class': 'main'})
    table = section_main.find_all('table')
    for index in table:
        table_main = index.find('table')
        if table_main != None:
            clear_table = table_main.find('tr').find_all('td')[2]
            song_info = clear_table.find_all('a')
            song_name = song_info[0].text
            album = song_info[1].text
            release_date_info = clear_table.find(string=re.compile('Дата релиза', re.I))
            artist = song_info[2].text
            genre = song_info[3].text
            song_name_info_list.append(song_name)
            album_info_list.append(album)
            artists_info_list.append(artist)
            genre_info_list.append(genre)
            release_date_list.append(release_date_info)
    return album_info_list, song_name_info_list, artists_info_list, genre_info_list, release_date_list

#Получение ссылок на артистов с первого сайта для дальнейшего парсинга данных
@lru_cache(None)
def urls_info(url):
    urls_list = []
    respounse = requests.get(url=url, headers=headers)
    soup = BS(respounse.text, 'lxml')
    section_main = soup.find('section', {'class': 'main'})
    table = section_main.find_all('table')
    for index in table:
        table_main = index.find('table')
        if table_main != None:
            clear_table = table_main.find('tr').find_all('td')[2]
            url_info = clear_table.find_all('a')
            urls = url_info[2].get('href')
            urls_list.append(urls)
    return urls_list

#Парсинг сайта эпл музыка по полученным сыллкам для получения данных об артистах
@lru_cache(None)
def artists_info(url):
    urls = urls_info(url)
    last_release_list = []
    froms_list = []
    date_of_birthday_list = []
    main_genre_list = []
    main_of_artist_list = []
    for url_ in urls:
        respounse = requests.get(url=url_, headers=headers)
        soup = BS(respounse.text, 'lxml')
        try:
            last_release = soup.find('div', {'id': 'scrollable-page'}).find('div', {
                'class': 'latest-release__container svelte-m5su2n'}).find('a').text
            decoded_last_release = last_release.encode('latin1').decode('utf-8')
            last_release_list.append(decoded_last_release)
        except:
            last_release = 'Данные отсутствуют'
            last_release_list.append(last_release)
        try:
            check_froms = soup.find('div', {'id': 'scrollable-page'}).find_all('dt', {
                'class': 'group-text-list__detail-title svelte-1ro1xab'})[0].text
            decoded_check_froms = check_froms.encode('latin1').decode('utf-8')
            if decoded_check_froms == "ОТКУДА":
                froms = soup.find('div', {'id': 'scrollable-page'}).find('dd', {
                    'class': 'group-text-list__detail-description svelte-1ro1xab'}).text
                decoded_froms = froms.encode('latin1').decode('utf-8')
                froms_list.append(decoded_froms)
            else:
                froms_list.append('Данные отсутствуют')
        except:
            froms = 'Данные отсутствуют'
            froms_list.append(froms)
        try:
            check_date = soup.find('div', {'id': 'scrollable-page'}).find_all('dt', {
                'class': 'group-text-list__detail-title svelte-1ro1xab'})[-2].text
            decoded_check_date = check_date.encode('latin1').decode('utf-8')
            if decoded_check_date == 'ДАТА РОЖДЕНИЯ':
                date_of_birthday = soup.find('div', {'id': 'scrollable-page'}).find_all('dd', {
                    'class': 'group-text-list__detail-description svelte-1ro1xab'})[-2].text
                decoded_date_of_birthday = date_of_birthday.encode('latin1').decode('utf-8')
                date_of_birthday_list.append(decoded_date_of_birthday)
            else:
                date_of_birthday_list.append('Данные отсутствуют')
        except:
            date_of_birthday = 'Данные отсутствуют'
            date_of_birthday_list.append(date_of_birthday)
        try:
            main_genre = soup.find('div', {'id': 'scrollable-page'}).find_all('dd', {
                'class': 'group-text-list__detail-description svelte-1ro1xab'})[-1].text
            decoded_main_genre = main_genre.encode('latin1').decode('utf-8')
            main_genre_list.append(decoded_main_genre)
        except:
            main_genre = 'Данные отсутствуют'
            main_genre_list.append(main_genre)
        try:
            main_of_artist = soup.find('div', {'id': 'scrollable-page'}).find('p', {'data-testid': 'truncate-text'}).text
            decoded_main_of_artist = main_of_artist.encode('latin1').decode('utf-8')
            main_of_artist_list.append(decoded_main_of_artist)
        except:
            main_of_artist = 'Данные отсутствуют'
            main_of_artist_list.append(main_of_artist)
    return last_release_list, froms_list, date_of_birthday_list, main_genre_list, main_of_artist_list

#Проверка, является ли альбом синглом (состоит ли он только из одной песни)
def single_albums_info():
    albums = songs_info(url)[0]
    single_album_list = []
    for album in albums:
        if '-' in album and ('Single' in album or 'EP' in album):
            single_album = album
            single_album_list.append(single_album)
    return single_album_list

#Парсинг сайта яндекс музыки (второго) для получения длительности треков
def song_durations(url1):
    song_durations_info_list = []
    album_durations_info_list = []
    respounse = requests.get(url=url1, headers=headers)
    time.sleep(3)
    soup = BS(respounse.text, 'lxml')
    time.sleep(3)
    main_page = soup.find('div', {'class': 'centerblock-wrapper centerblock-wrapper_full-width deco-pane'}).find('div', {
        'class': 'page-main__line page-main__line_chart'}).find_all('div', {
        'class': 'd-track typo-track d-track_selectable d-track_with-cover d-track_with-chart'})
    for duration_section in main_page:
        duration = duration_section.find('div', {'class': 'd-track__overflowable-column'}).find('div', {
            'class': 'd-track__info d-track__nohover'}).text
        song_durations_info_list.append('00:' + '0' + duration)
        album_durations_info_list.append(duration)
    return song_durations_info_list, album_durations_info_list


def count_of_song_in_album():
    count_of_song = []
    albums = songs_info(url)[0]
    single_albums = single_albums_info()
    for album in albums:
        if album in single_albums:
            count_of_song.append('1')
        else:
            count_of_song.append(random.randint(6, 18))
    return count_of_song

#Генерация индивидуальных номеров песен
def songid_list():
    all_values = list(range(5, 1001))
    songid = []
    x = random.sample(all_values, 99)
    songid.append('4')
    for i in range(len(x)):
        songid.append(x[i])
    return songid

def place_on_the_chart_list():
    place_on_the_chart = []
    x = 0
    for i in range(1, 101):
        x += 1
        place_on_the_chart.append(x)
    return place_on_the_chart

#Проверка наличия даты релиза песни
def clear_release():
    releases = songs_info(url)[4]
    release_list = []
    for release in releases:
        if release is not None:
            release = release.split(':')[-1].strip()
            release_list.append(release)
        else:
            release_list.append('Данные отсутствуют')
    return release_list


def duration_of_albums():
    duration_of_album = []
    count_songs = count_of_song_in_album()
    duration_song = song_durations(url1)[1]
    for i in range(len(count_songs)):
        if count_songs[i] == '1':
            duration_of_album.append(duration_song[i])
        else:
            number = count_songs[i]
            time_str = duration_song[i]
            time_obj = datetime.datetime.strptime(time_str, "%H:%M").time()
            total_seconds = time_obj.hour * 3600 + time_obj.minute * 60
            result_seconds = int(number) * total_seconds
            result_hours, remainder = divmod(result_seconds, 3600)
            result_minutes, _ = divmod(remainder, 60)
            result_time = "{:02d}:{:02d}".format(result_hours, result_minutes)
            duration_of_album.append(result_time)
    return duration_of_album, count_songs

#Проверка, что все таблицы созданы
def check_tables():
    try:
        cursor.execute("SELECT * FROM chart")
        connection.commit()
    except:
        print('Таблица chart не создана, пожалуйста запустите файл create.py')
        sys.exit(1)
    try:
        cursor.execute("SELECT * FROM song")
        connection.commit()
    except:
        print('Таблица song не создана, пожалуйста запустите файл create.py')
        sys.exit(1)
    try:
        cursor.execute("SELECT * FROM artists")
        connection.commit()
    except:
        print('Таблица artists не создана, пожалуйста запустите файл create.py')
        sys.exit(1)
    try:
        cursor.execute("SELECT * FROM album_info")
        connection.commit()
    except:
        print('Таблица album_info не создана, пожалуйста запустите файл create.py')
        sys.exit(1)


#Основная функия заполнения БД данными
if __name__ == '__main__':
    #Подключение к серверу
    connection = psycopg2.connect(user='user_test',  # Имя пользователя
                                  password='itmo_online',  # Пароль для пользователя
                                  host='146.185.211.205',  # Адрес
                                  port='5432',  # Порт
                                  database='dbstud')  # Имя БД

    cursor = connection.cursor()

    print('Успешное подключение к серверу')

    #Проверка, что все таблицы созданы
    check_tables()

    print('Загрузка данных')

    # Заполнение таблицы song
    songid = songid_list()
    artists = songs_info(url)[2]
    albums = songs_info(url)[0]
    duration = song_durations(url1)[0]
    song_genres = songs_info(url)[3]


    try:
        for i in range(len(artists)):
            cursor.execute("INSERT INTO song (songid, musician, album, duration, song_genre) VALUES (%s, %s, %s, %s, %s)",
                           (songid[i], artists[i], albums[i], duration[i], song_genres[i]))
            connection.commit()
        print('Успешное заполнение таблицы song')
    except Exception:
        print('Ошибка заполнения таблицы song \nПожалуйста, попробуйте запустить программу еще раз')
        sys.exit(1)


    # Заполнение таблицы chart
    song_name = songs_info(url)[1]
    place_on_the_chart = place_on_the_chart_list()

    for i in range(len(song_name)):
        cursor.execute("INSERT INTO chart (songid, song_name, place_on_the_chart) VALUES (%s, %s, %s)",
                       (songid[i], song_name[i], place_on_the_chart[i]))
        connection.commit()
    print('Успешное заполнение таблицы chart')



    # Заполнение таблицы album_info
    release_date = clear_release()
    count_of_songs = duration_of_albums()[1]
    duration_of_album = duration_of_albums()[0]
    album_genres = songs_info(url)[3]

    for i in range(len(count_of_songs)):
        cursor.execute("INSERT INTO album_info (album, date_of_release, count_of_songs, duration_of_album, album_genre) VALUES (%s, %s, %s, %s, %s)",
                       (albums[i], release_date[i], count_of_songs[i], duration_of_album[i], album_genres[i]))
        connection.commit()
    print('Успешное заполнение таблицы album_info')



    # Заполнение таблицы artists
    print('Данные загружаются, пожалуйста подождите (это займет около 1 минуты)')
    latest_release = artists_info(url)[0]
    main_genre = artists_info(url)[3]
    wherefrom = artists_info(url)[1]
    date_of_birthday = artists_info(url)[2]
    short_description = artists_info(url)[4]

    print('Данные успешно получены, загрузка данных в таблицу')
    for i in range(len(artists)):
        cursor.execute("INSERT INTO artists (musician, latest_release, main_genre, wherefrom, date_of_birthday, short_description) VALUES (%s, %s, %s, %s, %s, %s)",
                       (artists[i], latest_release[i], main_genre[i], wherefrom[i], date_of_birthday[i], short_description[i]))
        connection.commit()
    print('Успешное заполнение таблицы artists')


    #Закрытие соединения с сервером
    cursor.close()
    connection.close()
    print('Соединение с сервером закрыто')