# Yamdb API


### Project Description

The YaMDb project collects user reviews of works. The works are divided into categories: "Books", "Movies", "Music", etc. 
The list of categories can be expanded by the administrator.

The works themselves are not stored in YaMDb — you can't watch a movie or listen to music here.

A work can be assigned a genre from a preset list. 
Only the administrator can create new genres.

Grateful or outraged users leave text reviews for the works and give the work a score from 1 to 10. 
A rating (average value) is generated from user ratings. The user can leave only one review per work.


### Technology stack

- Python 3.12
- Django 3.2
- Django REST Framework 3.12
- Simple JWT — authentication using JWT tokens
- django-filter — convenient filtering
- SQLite (by default, it is easily replaced by PostgreSQL)
- drf-yasg or drf-spectacular — automatic API Documentation (ReDoc)

## Endpoints API

#### Authorization

- POST  |	/api/v1/auth/signup/  |	 Registration — receiving a confirmation code by email
- POST  |  /api/v1/auth/token/  |  Getting a JWT token by username and confirmation_code

#### Users

##### Method/Endpoint/Description/Access

- GET  |	/api/v1/users/  |	List users  |	Admin
- POST  |  /api/v1/users/  |	Create users  |	Admin
- GET  |	/api/v1/users/{username}/  |  Profile users	 |  Admin
- PATCH  |  /api/v1/users/{username}/  |	Edit user  |  Admin
- DELETE  |	/api/v1/users/{username}/  |  delete user  |  Admin
- GET	  |  /api/v1/users/me/	|  Me profile  |  Author
- PATCH  | /api/v1/users/me/  |  Edit my profile  |	Author

#### Categories

##### Method/Endpoint/Description/Access

- GET  |	/api/v1/categories/  |	List category  |  All
- POST  |	/api/v1/categories/  |	Create category	  |  Admin
- DELETE  |	/api/v1/categories/{slug}/  |  Delete category  |	Admin

#### Genres

##### Method/Endpoint/Description/Access

- GET	 |  /api/v1/genres/	 |  List genres  |  All
- POST  |  /api/v1/genres/  |	Create genres  |  Admin
- DELETE  |	/api/v1/genres/{slug}/  |	Delete genre  |  Admin

#### Titles

##### Method/Endpoint/Description/Access

- GET	|  /api/v1/titles/  |   List titles (with filtering) |	All
- POST  |  /api/v1/titles/  |   Create title  | 	Admin
- GET	  |  /api/v1/titles/{id}/  | 	Info of title  |	All
- PATCH	|  /api/v1/titles/{id}/   |  Update title   | 	Admin
- DELETE  | 	/api/v1/titles/{id}/  |  Delete title  |  Admin

#### views

##### Method/Endpoint/Description/Access

- GET	|  /api/v1/titles/{id}/reviews/  |	List reviews  | 	All
- POST  | 	/api/v1/titles/{id}/reviews/  | 	Create reviews  | 	Author
- GET	  |  /api/v1/titles/{id}/reviews/{id}/  |	review  |	All
- PATCH  | 	/api/v1/titles/{id}/reviews/{id}/  | 	Update review  |  Author / Mod / Admin
- DELETE  |  /api/v1/titles/{id}/reviews/{id}/  |  Delete review  |	Author / Mod / Admin

#### Comments

##### Method/Endpoint/Description/Access

- GET	  | .../reviews/{id}/comments/  |	List comment  |  All
- POST  |  .../reviews/{id}/comments/	 |  Create comment	|  Author
- GET	 |  .../comments/{id}/	|  Comment	|  All
- PATCH	|  .../comments/{id}/	|  Update comment	|  Author / Mod / Admin
- DELETE	|  .../comments/{id}/	|  Delete comment	|  Author / Mod / Admin

#### Users roles

- Role  |  Opportunities
- Anonymous - Viewing of works, reviews, comments
- User -	Anonymous + posting reviews and comments, editing your own
- moderator - user + edit/delete any reviews and comments
- admin - Full access. Managing users, categories, genres, and works


## How to launch a project:

Clone the repository and open it:

```
git clone ...
```
```
cd api_yamdb
```

Create and activate a virtual environment:

```
python -m venv env
```
```
Source venv/Script/Activate
```

Install dependencies from a file requirements.txt:

```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

Perform migrations:

```
python manage.py migrate
```

Launch a project:

```
python manage.py runserver
```

#### Registration:

POST /api/v1/auth/signup/

```
{
    "username": "user1",
    "email": "user1@example.com"
}
```

#### Getting a token:

POST /api/v1/auth/token/
```
{
    "username": "user1",
    "confirmation_code": "12345"
}
```

#### Creating a review (with a token):

POST /api/v1/titles/1/reviews/

##### Request
Authorization: Bearer <token>
```
{
    "text": "Отличный фильм!",
    "score": 9
}
```

##### Response
#
```
{
    "id": 1,
    "text": "Отличный фильм!",
    "author": "user1",
    "score": 9,
    "pub_date": "2024-01-15T12:00:00Z"
}
```

## Authors: 
### Aristov Kirill - Team Lead/developer
##### Wrote models, serializers, views, and endpoints for
- Titles
- Genres
- Category
- Implemented data import from csv files.

Link to the GitHub
```
https://github.com/Outsider133
```

### Filin Nikita - developer
##### Wrote the whole part about user management:
- registration and authentication system
- access rights
- working with a token
- e-mail confirmation system

Link to the GitHub
```
https://github.com/click002
```

### Satsuro Konstantin - developer
##### Wrote models, serializers, views, and endpoints for
- Reviews
- Comments
- Implemented a rating of titles

Link to the GitHub
```
https://github.com/mercv21
```
