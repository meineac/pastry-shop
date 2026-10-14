```
git clone <repo-url>
cd pastry-shop
cp .env.example .env
```

```
python -m venv .venv
source .venv/bin/activate
```

```
pip install -r requirements.txt
```

```
python manage.py migrate
```

```
python manage.py seed_all
```

```
python manage.py runserver
```