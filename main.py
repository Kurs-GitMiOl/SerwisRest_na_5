
# imports
from fastapi import FastAPI, HTTPException
import sqlite3
from typing import Any, List, Dict
from fastapi import Request



# Create FastAPI application instance
app = FastAPI()

# Name of the extended database file
DB_EXTENDED = "movies-extended.db"

# Helper function for database connection
def get_db():
    """ Returns a database connection and cursor """
    db = sqlite3.connect(DB_EXTENDED)
    cursor = db.cursor()
    return db, cursor



# Functions for movie operations

def fetch_all_movies() -> List[Dict[str, Any]]:
    """ Returns a list of all movies in the database """
    db, cursor = get_db()
    cursor.execute("SELECT id, title, director, year, description FROM movie")
    movies = cursor.fetchall()
    db.close()
    return [{"id": m[0], "title": m[1], "director": m[2], "year": m[3], "description": m[4]} for m in movies]

def fetch_movie(movie_id: int) -> Dict[str, Any]:
    """ Returns a single movie by ID; raises HTTPException if not found"""
    db, cursor = get_db()
    movie = cursor.execute(
        "SELECT id, title, director, year, description FROM movie WHERE id=?", (movie_id,)
    ).fetchone()
    db.close()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"id": movie[0], "title": movie[1], "director": movie[2], "year": movie[3], "description": movie[4]}



# Functions for actor operations

def fetch_all_actors() -> List[Dict[str, Any]]:
    """ Returns a list of all actors"""
    db, cursor = get_db()
    cursor.execute("SELECT id, name, surname FROM actor")
    actors = cursor.fetchall()
    db.close()
    return [{"id": a[0], "name": a[1], "surname": a[2]} for a in actors]

def fetch_actor(actor_id: int) -> Dict[str, Any]:
    """ Returns a single actor by ID; raises HTTPException if not found """
    db, cursor = get_db()
    actor = cursor.execute("SELECT id, name, surname FROM actor WHERE id=?", (actor_id,)).fetchone()
    db.close()
    if not actor:
        raise HTTPException(status_code=404, detail="Actor not found")
    return {"id": actor[0], "name": actor[1], "surname": actor[2]}

def insert_actor(name: str, surname: str) -> int:
    """ Inserts a new actor into the database and returns their ID """
    db, cursor = get_db()
    cursor.execute("INSERT INTO actor (name, surname) VALUES (?, ?)", (name, surname))
    db.commit()
    new_id = cursor.lastrowid
    db.close()
    return new_id

def update_actor_db(actor_id: int, name: str = None, surname: str = None) -> None:
    """ Updates an actor in the database based on provided data """
    fields, values = [], []
    if name:
        fields.append("name=?")
        values.append(name)
    if surname:
        fields.append("surname=?")
        values.append(surname)
    if not fields:
        raise HTTPException(status_code=400, detail="No data to update")
    values.append(actor_id)

    db, cursor = get_db()
    cursor.execute(f"UPDATE actor SET {', '.join(fields)} WHERE id=?", values)
    db.commit()
    count = cursor.rowcount
    db.close()
    if count == 0:
        raise HTTPException(status_code=404, detail="Actor not found")

def delete_actor_db(actor_id: int) -> None:
    """Deletes an actor from the database by ID """
    db, cursor = get_db()
    cursor.execute("DELETE FROM actor WHERE id=?", (actor_id,))
    db.commit()
    count = cursor.rowcount
    db.close()
    if count == 0:
        raise HTTPException(status_code=404, detail="Actor not found")

def fetch_movie_actors_db(movie_id: int) -> List[Dict[str, Any]]:
    """ Returns a list of actors assigned to a given movie"""
    db, cursor = get_db()
    cursor.execute("""
        SELECT actor.id, actor.name, actor.surname
        FROM actor
        JOIN movie_actor_through mat ON actor.id = mat.actor_id
        WHERE mat.movie_id = ?
    """, (movie_id,))
    actors = cursor.fetchall()
    db.close()
    return [{"id": a[0], "name": a[1], "surname": a[2]} for a in actors]



# Endpoints for movie

@app.get("/movies/count")
def get_movies_count():
    """Returns the number of all movies in the database"""
    db, cursor = get_db()
    cursor.execute("SELECT COUNT(*) FROM movie")
    count = cursor.fetchone()[0]
    db.close()
    return {"count": count}
#########

@app.get("/movies/search")
def search_movies(title: str):
    """Returns a list of movies matching the given title (LIKE)"""
    db, cursor = get_db()
    cursor.execute(
        "SELECT id, title, director, year, description FROM movie WHERE title LIKE ?",
        (f"%{title}%",)
    )
    movies = cursor.fetchall()
    db.close()
    return [{"id": m[0], "title": m[1], "director": m[2], "year": m[3], "description": m[4]} for m in movies]


@app.get("/movies/year/{year}")
def get_movies_by_year(year: int):
    """Returns a list of movies from the given year"""
    db, cursor = get_db()
    cursor.execute(
        "SELECT id, title, director, year, description FROM movie WHERE year=?",
        (year,)
    )
    movies = cursor.fetchall()
    db.close()
    return [{"id": m[0], "title": m[1], "director": m[2], "year": m[3], "description": m[4]} for m in movies]


@app.get("/movies")
def get_movies():
    return fetch_all_movies()

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    """Returns a single movie by ID """
    return fetch_movie(movie_id)


# Actor endpoints
@app.get("/actors")
def get_actors():
    """Returns all actors"""
    return fetch_all_actors()

@app.get("/actors/{actor_id}")
def get_actor(actor_id: int):
    """ Returns a single actor by ID """
    return fetch_actor(actor_id)


# Endpoint for adding  actor

@app.post("/actors")
async def add_actor(request: Request):
    """ Adds a new actor to the database"""
    params = await request.json()
    name = params.get("name", "").strip()
    surname = params.get("surname", "").strip()

    if not name or not surname:
        raise HTTPException(status_code=400, detail="Name and surname are required")

    new_id = insert_actor(name, surname)
    return {"message": "Actor added", "id": new_id}

@app.put("/actors/{actor_id}")
def update_actor(actor_id: int, params: dict[str, Any]):
    """ Updates an actor by ID"""
    name = params.get("name")
    surname = params.get("surname")
    update_actor_db(actor_id, name, surname)
    return {"message": "Actor updated"}

@app.delete("/actors/{actor_id}")
def delete_actor(actor_id: int):
    """ Deletes an actor by ID """
    delete_actor_db(actor_id)
    return {"message": "Actor deleted"}

# Endpoint for actors of a movie
@app.get("/movies/{movie_id}/actors")
def get_movie_actors(movie_id: int):
    """ Returns actors assigned to a given movie """
    return fetch_movie_actors_db(movie_id)


# View on database

import sqlite3

db = sqlite3.connect("movies-extended.db")
cursor = db.cursor()

print("Actors:")
for row in cursor.execute("SELECT * FROM actor"):
    print(row)

print("\nMovies:")
for row in cursor.execute("SELECT * FROM movie"):
    print(row)

print("\nMovie-Actor relations:")
for row in cursor.execute("SELECT * FROM movie_actor_through"):
    print(row)

db.close()