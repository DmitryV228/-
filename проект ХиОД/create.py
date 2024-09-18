import psycopg2

try:
        #Подключение к серверу
        connection = psycopg2.connect(user = 'user_test', # Имя пользователя
                password = 'itmo_online', # Пароль для пользователя
                host = '146.185.211.205', # Адрес
                port = '5432', # Порт
                database = 'dbstud') # Имя БД

        cursor = connection.cursor()

        #Создание таблицы chart
        chart_create = """create table chart (
                                songid integer,
                                song_name varchar, 
                                place_on_the_chart integer,
                                PRIMARY KEY (songid))"""

        cursor.execute(chart_create)
        connection.commit()
        print("Таблица chart успешно создана в PostgreSQL")

        #Создание таблицы song
        song_create = """create table song (
                                songid integer,
                                musician varchar, 
                                album varchar,
                                duration time,
                                song_genre varchar,
                                PRIMARY KEY (songid))"""

        cursor.execute(song_create)
        connection.commit()
        print("Таблица song успешно создана в PostgreSQL")

        #Создание таблицы artists
        artists_create = """create table artists (
                                musician varchar,
                                latest_release varchar,
                                main_genre varchar,
                                wherefrom varchar,
                                date_of_birthday varchar,
                                short_description varchar)"""

        cursor.execute(artists_create)
        connection.commit()
        print("Таблица artists успешно создана в PostgreSQL")

        #Создание таблицы album_info
        album_info_create = """create table album_info (
                                album varchar,
                                date_of_release varchar, 
                                count_of_songs varchar,
                                duration_of_album varchar,
                                album_genre varchar)"""

        cursor.execute(album_info_create)
        connection.commit()
        print("Таблица album_info успешно создана в PostgreSQL")

#Обработка ошибок
except (Exception) as error:
    print("Ошибка при работе с PostgreSQL", error)

#Закрытие соединения с сервером
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")