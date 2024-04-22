'''
from django.contrib.auth.models import User

python -m django --version
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

#Команды для миграции с SQLite на PostreSQL
python -Xutf8 manage.py dumpdata -o data.json
python manage.py migrate --run-syncdb
python manage.py loaddata data.json

python manage.py startapp myapp1
'''