# ==============================================================
# Imports
# ==============================================================
from fastapi import FastAPI, HTTPException, Request
import sqlite3
from typing import Any, List, Dict
import requests
import os

# Print current working directory for debugging
print("Current working directory:", os.getcwd())

# ==============================================================
# FastAPI application instance
# ==============================================================
app = FastAPI()

# ==============================================================
# Database filenames
# ==============================================================
DB_SIMPLE = "movies.db"              # Prosta baza filmów
DB_EXTENDED = "movies-extended.db"   # Rozszerzona baza z aktorami i filmami

# ==============================================================
# Helper function for database connection
# ==============================================================
def get_db(db_name: str):
    """Return a database connection and cursor for the given database"""
    db = sqlite3.connect(db_name)
    cursor = db.cursor()
    return db, cursor

# ==============================================================
# ==============================================================
# Basic test endpoints
# ==============================================================
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/sum")
def sum(x: int = 0, y: int = 10):
    return x + y

@app.get("/subtract")
def subtract(x: int = 0, y: int = 0):
    return x - y

@app.get("/multiply")
def multiply(x: int = 1, y: int = 1):
    return x * y

@app.get("/geocode")
def geocode(lat: float, lon: float):
    """Reverse geocode coordinates using OpenStreetMap API"""
    url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    return response.json()

# ==============================================================
# Movie functions
# ==============================================================
def fetch_all_movies(db_name: str) -> List[Dict[str, Any]]:
    """Return all movies from the selected database"""
    db, cursor = get_db(db_name)
    # Choose columns based on database
    if db_name == DB_SIMPLE:
        cursor.execute("SELECT id, title, year, actors FROM movies")
        movies = cursor.fetchall()
        db.close()
        return [{"id": m[0], "title": m[1], "year": m[2], "actors": m[3]} for m in movies]
    else:
        cursor.execute("SELECT id, title, director, year, description FROM movie")
        movies = cursor.fetchall()
        db.close()
        return [{"id": m[0], "title": m[1], "director": m[2], "year": m[3], "description": m[4]} for m in movies]

def fetch_movie(db_name: str, movie_id: int) -> Dict[str, Any]:
    """Return a single movie by ID from the selected database"""
    db, cursor = get_db(db_name)
    if db_name == DB_SIMPLE:
        movie = cursor.execute("SELECT id, title, year, actors FROM movies WHERE id=?", (movie_id,)).fetchone()
        db.close()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return {"id": movie[0], "title": movie[1], "year": movie[2], "actors": movie[3]}
    else:
        movie = cursor.execute("SELECT id, title, director, year, description FROM movie WHERE id=?", (movie_id,)).fetchone()
        db.close()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return {"id": movie[0], "title": movie[1], "director": movie[2], "year": movie[3], "description": movie[4]}

def add_movie(db_name: str, params: dict[str, Any]) -> Dict[str, Any]:
    """Add a new movie to the selected database"""
    if db_name == DB_SIMPLE:
        title = params.get("title", "").strip()
        year = params.get("year", "").strip()
        actors = params.get("actors", "").strip()
        if not title or not year or not actors:
            raise HTTPException(status_code=400, detail="All fields (title, year, actors) are required")
        db, cursor = get_db(db_name)
        cursor.execute("INSERT INTO movies (title, year, actors) VALUES (?, ?, ?)", (title, year, actors))
        db.commit()
        new_id = cursor.lastrowid
        db.close()
        return {"message": "Movie added successfully", "id": new_id}
    else:
        title = params.get("title", "").strip()
        director = params.get("director", "").strip()
        year = params.get("year", "").strip()
        description = params.get("description", "").strip()
        if not title or not director or not year:
            raise HTTPException(status_code=400, detail="Title, director, and year are required")
        db, cursor = get_db(db_name)
        cursor.execute("INSERT INTO movie (title, director, year, description) VALUES (?, ?, ?, ?)", (title, director, year, description))
        db.commit()
        new_id = cursor.lastrowid
        db.close()
        return {"message": "Movie added successfully", "id": new_id}

def update_movie(db_name: str, movie_id: int, params: dict[str, Any]) -> Dict[str, Any]:
    """Update movie fields dynamically"""
    db, cursor = get_db(db_name)
    fields, values = [], []
    if db_name == DB_SIMPLE:
        title = params.get("title")
        year = params.get("year")
        actors = params.get("actors")
        if title is not None: fields.append("title=?"); values.append(title)
        if year is not None: fields.append("year=?"); values.append(year)
        if actors is not None: fields.append("actors=?"); values.append(actors)
    else:
        title = params.get("title")
        director = params.get("director")
        year = params.get("year")
        description = params.get("description")
        if title is not None: fields.append("title=?"); values.append(title)
        if director is not None: fields.append("director=?"); values.append(director)
        if year is not None: fields.append("year=?"); values.append(year)
        if description is not None: fields.append("description=?"); values.append(description)
    if not fields:
        db.close()
        raise HTTPException(status_code=400, detail="No fields to update")
    values.append(movie_id)
    table = "movies" if db_name == DB_SIMPLE else "movie"
    cursor.execute(f"UPDATE {table} SET {', '.join(fields)} WHERE id=?", values)
    db.commit()
    if cursor.rowcount == 0:
        db.close()
        raise HTTPException(status_code=404, detail="Movie not found")
    db.close()
    return {"message": f"Movie with id {movie_id} updated successfully"}

def delete_movie(db_name: str, movie_id: int) -> Dict[str, Any]:
    """Delete a movie by ID"""
    db, cursor = get_db(db_name)
    table = "movies" if db_name == DB_SIMPLE else "movie"
    cursor.execute(f"DELETE FROM {table} WHERE id=?", (movie_id,))
    db.commit()
    rowcount = cursor.rowcount
    db.close()
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"message": "Movie deleted successfully"}

def delete_all_movies(db_name: str) -> Dict[str, Any]:
    """Delete all movies in the selected database"""
    db, cursor = get_db(db_name)
    table = "movies" if db_name == DB_SIMPLE else "movie"
    cursor.execute(f"DELETE FROM {table}")
    db.commit()
    deleted_count = cursor.rowcount
    db.close()
    return {"message": f"{deleted_count} movies deleted successfully"}

# ==============================================================
# Actor functions (operate only on extended DB)
# ==============================================================
def fetch_all_actors_ext() -> List[Dict[str, Any]]:
    db, cursor = get_db(DB_EXTENDED)
    cursor.execute("SELECT id, name, surname FROM actor")
    actors = cursor.fetchall()
    db.close()
    return [{"id": a[0], "name": a[1], "surname": a[2]} for a in actors]

def fetch_actor_ext(actor_id: int) -> Dict[str, Any]:
    db, cursor = get_db(DB_EXTENDED)
    actor = cursor.execute("SELECT id, name, surname FROM actor WHERE id=?", (actor_id,)).fetchone()
    db.close()
    if not actor:
        raise HTTPException(status_code=404, detail="Actor not found")
    return {"id": actor[0], "name": actor[1], "surname": actor[2]}

def insert_actor_ext(name: str, surname: str) -> int:
    db, cursor = get_db(DB_EXTENDED)
    cursor.execute("INSERT INTO actor (name, surname) VALUES (?, ?)", (name, surname))
    db.commit()
    new_id = cursor.lastrowid
    db.close()
    return new_id

def update_actor_ext(actor_id: int, name: str = None, surname: str = None) -> None:
    fields, values = [], []
    if name: fields.append("name=?"); values.append(name)
    if surname: fields.append("surname=?"); values.append(surname)
    if not fields:
        raise HTTPException(status_code=400, detail="No data to update")
    values.append(actor_id)
    db, cursor = get_db(DB_EXTENDED)
    cursor.execute(f"UPDATE actor SET {', '.join(fields)} WHERE id=?", values)
    db.commit()
    if cursor.rowcount == 0:
        db.close()
        raise HTTPException(status_code=404, detail="Actor not found")
    db.close()

def delete_actor_ext(actor_id: int) -> None:
    db, cursor = get_db(DB_EXTENDED)
    cursor.execute("DELETE FROM actor WHERE id=?", (actor_id,))
    db.commit()
    if cursor.rowcount == 0:
        db.close()
        raise HTTPException(status_code=404, detail="Actor not found")
    db.close()

def fetch_movie_actors_ext(movie_id: int) -> List[Dict[str, Any]]:
    db, cursor = get_db(DB_EXTENDED)
    cursor.execute("""
        SELECT actor.id, actor.name, actor.surname
        FROM actor
        JOIN movie_actor_through mat ON actor.id = mat.actor_id
        WHERE mat.movie_id = ?
    """, (movie_id,))
    actors = cursor.fetchall()
    db.close()
    return [{"id": a[0], "name": a[1], "surname": a[2]} for a in actors]

# ==============================================================
# ==============================================================
# Movie endpoints
# ==============================================================
@app.get("/movies")
def endpoint_get_movies(db: str = DB_SIMPLE):
    """Get all movies. Choose DB with 'db' param (default: movies.db)"""
    return fetch_all_movies(db)

@app.get("/movies/{movie_id}")
def endpoint_get_movie(movie_id: int, db: str = DB_SIMPLE):
    """Get one movie by ID. Choose DB with 'db' param (default: movies.db)"""
    return fetch_movie(db, movie_id)

@app.post("/movies")
def endpoint_add_movie(params: dict[str, Any], db: str = DB_SIMPLE):
    """Add a new movie to chosen DB"""
    return add_movie(db, params)

@app.put("/movies/{movie_id}")
def endpoint_update_movie(movie_id: int, params: dict[str, Any], db: str = DB_SIMPLE):
    """Update movie in chosen DB"""
    return update_movie(db, movie_id, params)

@app.delete("/movies/{movie_id}")
def endpoint_delete_movie(movie_id: int, db: str = DB_SIMPLE):
    """Delete a movie by ID in chosen DB"""
    return delete_movie(db, movie_id)

@app.delete("/movies")
def endpoint_delete_all_movies(db: str = DB_SIMPLE):
    """Delete all movies in chosen DB"""
    return delete_all_movies(db)

# ==============================================================
# Actor endpoints (extended DB only)
# ==============================================================
@app.get("/actors")
def endpoint_get_actors():
    return fetch_all_actors_ext()

@app.get("/actors/{actor_id}")
def endpoint_get_actor(actor_id: int):
    return fetch_actor_ext(actor_id)

@app.post("/actors")
async def endpoint_add_actor(request: Request):
    params = await request.json()
    name = params.get("name", "").strip()
    surname = params.get("surname", "").strip()
    if not name or not surname:
        raise HTTPException(status_code=400, detail="Name and surname required")
    new_id = insert_actor_ext(name, surname)
    return {"message": "Actor added", "id": new_id}

@app.put("/actors/{actor_id}")
def endpoint_update_actor(actor_id: int, params: dict[str, Any]):
    name = params.get("name")
    surname = params.get("surname")
    update_actor_ext(actor_id, name, surname)
    return {"message": "Actor updated"}

@app.delete("/actors/{actor_id}")
def endpoint_delete_actor(actor_id: int):
    delete_actor_ext(actor_id)
    return {"message": "Actor deleted"}

@app.get("/movies/{movie_id}/actors")
def endpoint_get_movie_actors(movie_id: int):
    return fetch_movie_actors_ext(movie_id)
