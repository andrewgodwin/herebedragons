if [ -z "$SKIPMIGRATIONS" ]; then
    python manage.py migrate
fi

gunicorn herebedragons.wsgi:application -b 0.0.0.0:8000
