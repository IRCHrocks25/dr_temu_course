release: python manage.py migrate && python manage.py createcachetable && python manage.py collectstatic --noinput
web: gunicorn myProject.wsgi:application -c gunicorn_config.py
