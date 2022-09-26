
## Api_yamdb
***
![yamdb_final_workflow](https://github.com/cooper30/yamdb_final/workflows/yamdb_final_workflow/badge.svg)


### Описание проекта:

Api_yamdb главный конкурент IMDB.

***
### Шаблон наполнения env-файла:

```
SECRET_KEY=
DB_ENGINE=django.db.backends.postgresql
DB_NAME=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=
DB_PORT=
```

***
### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/cooper30/yamdb_final.git
```

Перейти в директорию с инфраструктурой проекта:
```
cd infra_sp2/infra
```

Запуск docker-compose:

```
docker-compose up -d --build 
```

Выполнить миграции:
```
docker-compose exec web python manage.py migrate
```

Создать суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```

Собрать статику:
```
docker-compose exec web python manage.py collectstatic --no-input 
```

***
## Tech
Yatube API uses a number of open source projects to work properly:

- [Python] - a programming language that lets you work quickly and integrate systems more effectively.
- [Django] - a high-level Python web framework
***
## Authors
- cooper30
- IrinaSMR
- Monshou1251

***
## Requests examples
Samples of how this API works could be found through Redoc - http://127.0.0.1:8000/redoc/

Comments GET request:
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/
```sh
[
  {
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
      {
        "id": 0,
        "text": "string",
        "author": "string",
        "pub_date": "2019-08-24T14:15:22Z"
      }
    ]
  }
]
```

Comments POST request:
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/
```sh
{
  "text": "string"
}
```
Response samples:
```sh
{
  "id": 0,
  "text": "string",
  "author": "string",
  "pub_date": "2019-08-24T14:15:22Z"
}
```
