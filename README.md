[![License](https://img.shields.io/badge/license-MIT-green)](https://tldrlegal.com/license/mit-license) <br>

<hr>

Тестовое CRUD-приложение системы складского учёта на Django 3.0.3 с базой данных SQLite3.
Использованы внешние библиотеки mptt, jquery formsets, qrcode.

<hr>

### Что можно сделать:
- создать поставку на странице /cargo_new
![Страница поставки](1.png)

- создать покупку на странице /order;
![Страница покупки](2.png)

- выбрать созданные поставку и покупку на страницах /admin/cargo/cargo/
и /admin/shipment/shipment;
![Страница списка поставок](3.png)
![Страница списка покупок](4.png)

- на странице поставки нажать "Подтвердить получение поставки";
- на странице покупки нажать "Подтвердить готовность к отправке"
(если количество товаров в покупке превышает количество товаров на складе,
кнопка будет скрыта).
![Страница товаров](5.png)
![Страница категорий](6.png)

<hr>

### Как запустить:

- клонировать в нужную директорию
```
$ git clone https://github.com/96tm/warehouse-management-test.git
```
- создать виртуальное окружение
```
$ python3.8 -m venv environment
```
- активировать окружение
```
$ source environment/bin/activate
```
- установить pipenv <br>
```
$ pip3 install pipenv
```
- установить зависимости <br>
```
$ pipenv install
```
- выполнить миграции
```
$ python manage.py migrate
```
- создать пользователя с правами администратора
```
$ python manage.py createsuperuser
```
- заполнить базу данных тестовыми значениями
```
$ python manage.py shell
>>> from common.fill_db import fill_db
>>> fill_db()
>>> exit()
```
- изменить email в файле warehouse-management-test/settings.py <br>
(EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, <br>
DEFAULT_FROM_EMAIL, SERVER_EMAIL, ADMINS)

- запустить сервер
```
$ python manage.py runserver
```
