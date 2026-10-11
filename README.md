# Django Task Manager API — учебный starter

Windows PowerShell:
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py test
python manage.py runserver
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py test
python manage.py runserver
```

Откройте http://127.0.0.1:8000/api/tasks/. Это учебный проект на SQLite, без аутентификации и не для production.

## Доступ к админке

В Django нет логина и пароля по умолчанию. Создайте суперпользователя:

```bash
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')"
```

После этого откройте http://127.0.0.1:8000/admin/ (логин: `admin`, пароль: `admin`).
