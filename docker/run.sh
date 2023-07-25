if [ -z "$SKIPMIGRATIONS" ]; then
    python manage.py migrate
fi

if [ ! -z "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py createsuperuser --username andrew --email andrew@aeracode.org --noinput
fi

gunicorn herebedragons.wsgi:application -b "0.0.0.0:$PORT"
