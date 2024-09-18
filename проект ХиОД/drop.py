import psycopg2

try:
    #Подключение к серверу
    connection = psycopg2.connect(user = 'user_test', # Имя пользователя
            password = 'itmo_online', # Пароль для пользователя
            host = '146.185.211.205', # Адрес
            port = '5432', # Порт
            database = 'dbstud') # Имя БД

    cursor = connection.cursor()

    #Удаление созданных таблиц
    drop = 'drop table chart, song, artists, album_info cascade'

    cursor.execute(drop)
    connection.commit()
    print('Таблицы успешно удалены')

#Обработка ошибок
except (Exception) as error:
    print("Ошибка при работе с PostgreSQL", error)

#Закрытие соединения с сервером
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")