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

## Option 1: Running with Virtual Environment

### Requirements
- Python 3.12
- MySQL

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Bri3die/news-application.git
cd news_application
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your database settings:
```
SECRET_KEY=your-secret-key
DATABASE_NAME=your-db-name
DATABASE_USER=your-db-user
DATABASE_PASSWORD=your-db-password
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the server:
```bash
python manage.py runserver
```

7. Open your browser at `http://localhost:8000`

---

## Option 2: Running with Docker

### Requirements
- Docker Desktop

### Setup

1. Pull the image:
```bash
docker pull bri3die/news-application:latest
```

2. Run the container:
```bash
docker run -p 8000:8000 bri3die/news-application:latest
```

3. Open your browser at `http://localhost:8000`

The Docker container uses SQLite by default so no database setup is required.

---

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

Sphinx documentation is available in the `docs/` folder. To view it, open `docs/_build/html/index.html` in your browser