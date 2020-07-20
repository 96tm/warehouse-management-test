#!/bin/sh
source venv/bin/activate
if [ ! -f "database/warehouse.db" ]; then
  python manage.py migrate
  python manage.py collectstatic --no-input
  if [ -n "$ADD_TEST_DATA" ]; then
    python manage.py add_test_data
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell
  fi
fi
exec gunicorn -b :8888 warehouse-management-test.wsgi
