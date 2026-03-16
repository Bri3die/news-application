# News Application

A Django-based news platform with role-based access control, built as a capstone project.

## Features

- **User Roles**: Reader, Editor, and Journalist with different permissions
- **Articles**: Create, view, approve, and manage news articles
- **Newsletters**: Curated collections of articles
- **Subscriptions**: Readers can subscribe to publishers and journalists
- **Email Notifications**: Subscribers get notified when articles are approved
- **REST API**: Full API with token authentication

## Setup

### 1. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# or
.venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install django djangorestframework mysqlclient
```

### 3. Database Setup

The project uses MariaDB. Create the database:

```sql
CREATE DATABASE news_app;
CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'news_password';
GRANT ALL PRIVILEGES ON news_app.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;
```

Or switch to SQLite in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Running with Docker

### Requirements
- Docker Desktop installed

### Setup

1. Pull the image:
```bash
docker pull yourusername/news-application:latest
```

2. Run the container:
```bash
docker run -p 8000:8000 yourusername/news-application:latest
```

3. Open your browser at `http://localhost:8000`

### 4. Run Migrations

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py setup_groups
```

### 5. Run the Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000

## API Endpoints

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | `/api/token/` | No | Get auth token |
| GET | `/api/articles/` | No | List approved articles |
| POST | `/api/articles/` | Journalist | Create article |
| GET | `/api/articles/subscribed/` | Yes | Subscribed articles |
| GET | `/api/newsletters/` | No | List newsletters |
| POST | `/api/newsletters/` | Journalist | Create newsletter |

## Running Tests

```bash
python manage.py test news
```

## User Roles

- **Reader**: View articles, subscribe to publishers/journalists
- **Editor**: Approve/delete articles, access editor dashboard
- **Journalist**: Create/edit/delete own articles and newsletters


## Documentation

Sphinx documentation is available in the `docs/` folder. To view it, open `docs/_build/html/index.html` in your browser.