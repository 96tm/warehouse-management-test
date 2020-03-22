Тестовое CRUD-приложение системы складского учёта на Django с базой данных SQLite3.
Использованы внешние библиотеки mptt, jquery formsets, qrcode.

Как запустить:
- клонировать в нужную директорию <br>
git clone https://github.com/96tm/warehouse-management-test.git

- выполнить миграции <br>
python manage.py migrate

- создать пользователя с правами администратора <br>
python manage.py createsuperuser

- заполнить базу данных тестовыми значениями <br>
python manage.py shell
from common.fill_db import fill_db
fill_db()
exit()

- изменить email в файле warehouse-management-test/settings.py <br>
(EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, <br>
DEFAULT_FROM_EMAIL, SERVER_EMAIL, ADMINS)

- запустить сервер <br>
python manage.py runserver

Что можно сделать:
- создать поставку на странице /cargo_new;
- создать покупку на странице /order;
- выбрать созданные поставку и покупку на страницах /admin/cargo/cargo/
и /admin/shipment/shipment;
- на странице поставки нажать "Подтвердить получение поставки";
- на странице покупки нажать "Подтвердить готовность к отправке"
(если количество товаров в покупке превышает количество товаров на складе,
кнопка будет скрыта).
