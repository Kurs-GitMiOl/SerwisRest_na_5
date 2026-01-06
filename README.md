# MovieDB REST API – FastAPI (Extended Version)

This is a FastAPI project.  
The application provides a REST API for managing a movie database with actors, stored in SQLite.

The project implements topics such as:
- REST endpoints (GET, POST, PUT, DELETE),
- working with SQLite database,
- database relations (movies – actors),
- basic validation and error handling,
- refactoring database logic into helper functions,
- testing REST services using Swagger UI and console tools.


# The application provides the following endpoints:

## Movie endpoints
- GET /movies – get all movies
- GET /movies/{movie_id} – get one movie by ID
- GET /movies/{movie_id}/actors – get actors assigned to a movie
- GET /movies/count – get total number of movies in the database
- GET /movies/search?title={title} – search movies by title (partial match)
- GET /movies/year/{year} – get movies from a specific year

## Actor endpoints
- GET /actors – get all actors
- GET /actors/{actor_id} – get one actor by ID
- POST /actors – add a new actor
- PUT /actors/{actor_id} – update an actor
- DELETE /actors/{actor_id} – delete an actor

## Database

The project uses a local SQLite database with extended schema.

- file: `movies-extended.db`
- tables:
  - `movie`
  - `actor`
  - `movie_actor_through`

The database file is located in the main project directory and is included in the repository.



## Requirements

Project dependencies are listed in the `requirements.txt` file.

Install dependencies using:
 pip install -r requirements.txt

# Running the application

Option 1 – run from terminal 
- From the project directory run:
   uvicorn main:app --reload
The application will be available at: http://127.0.0.1:8000

Option 2 – run from terminal in IDE
- From terminal in your IDE run:
fastapi dev main.py
or commend:
uvicorn main:app --reload
The application will be available at: http://127.0.0.1:8000

After starting the application, open:
http://127.0.0.1:8000/docs for testing the API it allows you:
- see all endpoints,
- send requests (GET, POST, PUT DELETE),
- test the API without external tools.



## Testing from console
"NOTE: When testing the application, review the database view, e.g., in the IDE console;
this will help you better verify the correctness of query results."
### You can also use console to use this software by commands for example:


- Get all movies:
Invoke-RestMethod -Uri "http://127.0.0.1:8000/movies" -Method GET

- Get one movie by ID:
Invoke-RestMethod -Uri "http://127.0.0.1:8000/movies/1" -Method GET

- Get all actors:
Invoke-RestMethod -Uri "http://127.0.0.1:8000/actors" -Method GET

- Get one actor by ID:
Invoke-RestMethod -Uri "http://127.0.0.1:8000/actors/1" -Method GET

- Update an actor by ID:

$body = @{
    name = "New"
    surname = "Actor"
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/actors/1" -Method PUT -Body $body -ContentType "application/json"


- Get actors for a movie

for example: movie_id=4 has attached actor_id=7

$actors_in_movie = Invoke-RestMethod -Uri "http://127.0.0.1:8000/movies/4/actors" -Method GET
Write-Host "Actors in movie with ID=4:"
$actors_in_movie | Format-Table


 # Testing in browser for some queries 

 ## Movies


- Get all movies
http://127.0.0.1:8000/movies

- Get one movie by ID (example: movie_id = 4)
http://127.0.0.1:8000/movies/4

- Get actors for a movie (example: movie_id = 4)
http://127.0.0.1:8000/movies/4/actors


## Actors


- Get all actors
http://127.0.0.1:8000/actors

- Get one actor by ID (example: actor_id = 7)
http://127.0.0.1:8000/actors/7


## Using curl:

- Get all movies
curl -X GET http://127.0.0.1:8000/movies

- Get one movie by ID
curl -X GET http://127.0.0.1:8000/movies/1

- Get all actors
curl -X GET http://127.0.0.1:8000/actors

- Get one actor by ID
curl -X GET http://127.0.0.1:8000/actors/1

- Update an actor by ID
curl -X PUT http://127.0.0.1:8000/actors/1 -H "Content-Type: application/json" -d "{\"name\":\"New\",\"surname\":\"Actor\"}"

- Get actors for a movie
 for example: movie_id=4 has attached actor_id=7
curl -X GET http://127.0.0.1:8000/movies/4/actors
