# # importy
# from fastapi import FastAPI
# import requests
# import sqlite3
# from typing import Any
#
#
# from fastapi import HTTPException
# from fastapi import FastAPI
# import requests
# import sqlite3
#
# from typing import Any
#
# # utworzenie aplikacji
# app = FastAPI()
#
# # ====================================
# # wcześniejsze endpointy
# # ====================================
#
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
#
# @app.get("/sum")
# def sum(x: int = 0, y: int = 10):
#     return x + y
#
# @app.get("/subtract")
# def subtract(x: int = 0, y: int = 0):
#     return x - y
#
# @app.get("/multiply")
# def multiply(x: int = 1, y: int = 1):
#     return x * y
#
# @app.get("/geocode")
# def geocode(lat: float, lon: float):
#     url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}"
#     response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#     return response.json()
#
# # ====================================
# # nowe endpointy: obsługa bazy filmów
# # ====================================
#
# # Pobranie wszystkich filmów
# @app.get("/movies")
# def get_movies():
#     output = []
#     db = sqlite3.connect("movies.db")
#     cursor = db.cursor()
#     cursor.execute("SELECT * FROM movies")
#     for movie in cursor:
#         movie_dict = {
#             "id": movie[0],
#             "title": movie[1],
#             "year": movie[2],
#             "actors": movie[3]
#         }
#         output.append(movie_dict)
#     db.close()
#     return output
#
# # Pobranie pojedynczego filmu po ID
# @app.get("/movies/{movie_id}")
# def get_movie(movie_id: int):
#     db = sqlite3.connect("movies.db")
#     cursor = db.cursor()
#     movie = cursor.execute("SELECT * FROM movies WHERE id=?", (movie_id,)).fetchone()
#     db.close()
#     if movie is None:
#         return {"message": "Movie not found"}
#     return {"id": movie[0], "title": movie[1], "year": movie[2], "actors": movie[3]}
#
# # Dodanie nowego filmu
# @app.post("/movies")
# def add_movie(params: dict[str, Any]):
#     title = params.get("title", "").strip()
#     year = params.get("year", "").strip()
#     actors = params.get("actors", "").strip()
#
#     # walidacja pól
#     if not title or not year or not actors:
#         return {"message": "All fields (title, year, actors) are required"}
#
#     db = sqlite3.connect("movies.db")
#     cursor = db.cursor()
#     cursor.execute("INSERT INTO movies (title, year, actors) VALUES (?, ?, ?)", (title, year, actors))
#     db.commit()
#     new_id = cursor.lastrowid
#     db.close()
#
#     return {"message": "Movie added successfully", "id": new_id}
#
#
# # PUT aktualizacja filmu po ID     #### Działa
# @app.put("/movies/{movie_id}")
# def update_movie(movie_id: int, params: dict[str, Any]):
#     db = sqlite3.connect("movies.db")
#     cursor = db.cursor()
#
#     # Pobieramy wartości z params (jeżeli brak, zostawiamy puste)
#     title = params.get("title")
#     year = params.get("year")
#     actors = params.get("actors")
#
#     # Budujemy dynamicznie SET tylko dla podanych pól
#     fields = []
#     values = []
#     if title is not None:
#         fields.append("title=?")
#         values.append(title)
#     if year is not None:
#         fields.append("year=?")
#         values.append(year)
#     if actors is not None:
#         fields.append("actors=?")
#         values.append(actors)
#
#     if not fields:
#         db.close()
#         raise HTTPException(status_code=400, detail="No fields to update")
#
#     values.append(movie_id)  # dla WHERE id=?
#     sql = f"UPDATE movies SET {', '.join(fields)} WHERE id=?"
#     cursor.execute(sql, values)
#     db.commit()
#     updated_count = cursor.rowcount
#     db.close()
#
#     if updated_count == 0:
#         raise HTTPException(status_code=404, detail="Movie not found")
#
#     return {"message": f"Movie with id {movie_id} updated successfully"}
#
# # --- Usuwanie filmu ---
# @app.delete("/movies/{movie_id}")
# def delete_movie(movie_id: int):
#     db = sqlite3.connect("movies.db")
#     cursor = db.cursor()
#     cursor.execute("DELETE FROM movies WHERE id=?", (movie_id,))
#     db.commit()
#     rowcount = cursor.rowcount
#     db.close()
#     if rowcount == 0:
#         return {"message": "Movie not found"}
#     return {"message": "Movie deleted successfully"}
#
#
# # test usuwanie pojedyńczego filmu
# # Invoke-RestMethod -Uri http://127.0.0.1:8000/movies/4 -Method Delete
#
# # DELETE wszystkich filmów
# @app.delete("/movies")
# def delete_all_movies():
#     db = sqlite3.connect("movies.db")
#     cursor = db.cursor()
#     cursor.execute("DELETE FROM movies")
#     db.commit()
#     deleted_count = cursor.rowcount
#     db.close()
#
#     return {"message": f"{deleted_count} movies deleted successfully"}
#

#######################################################################
#######################################################################
###### po modyfikacj wedlug punktu 8
#######################################################################

# importy
from fastapi import FastAPI
import requests
import sqlite3
from typing import Any


from fastapi import HTTPException
from fastapi import FastAPI, Request
import requests
import sqlite3

from typing import Any


app = FastAPI()

#####################################################################
################################################################
#####################  nadole przed refaktoryzacją

#
# @app.get("/movies")
# def get_movies():
#     # Połączenie z bazą danych
#     db = sqlite3.connect("movies-extended.db")
#     cursor = db.cursor()
#
#     # Pobieramy dane filmu (bez aktorów!)
#     cursor.execute("SELECT id, title, director, year, description FROM movie")
#     movies = cursor.fetchall()
#
#     # Zamykamy połączenie
#     db.close()
#
#     # Lista wynikowa
#     output = []
#
#     # Każdy rekord z bazy zamieniamy na słownik
#     for m in movies:
#         output.append({
#             "id": m[0],
#             "title": m[1],
#             "director": m[2],
#             "year": m[3],
#             "description": m[4]
#         })
#
#     return output # zwrot jako JASON
#
#
#
# # POBRANIE JEDNEGO FILMU PO ID
# @app.get("/movies/{movie_id}")
# def get_movie(movie_id: int):
#     db = sqlite3.connect("movies-extended.db")
#     cursor = db.cursor()
#
#     # Szukamy filmu o konkretnym ID
#     movie = cursor.execute(
#         "SELECT id, title, director, year, description FROM movie WHERE id=?",
#         (movie_id,)
#     ).fetchone()
#
#     db.close()
#
#     # Jeśli filmu nie ma → błąd 404
#     if movie is None:
#         raise HTTPException(status_code=404, detail="Movie not found")
#
#     # Zwracamy znaleziony film
#     return {
#         "id": movie[0],
#         "title": movie[1],
#         "director": movie[2],
#         "year": movie[3],
#         "description": movie[4]
#     }
#
#
# # endpointy dla aktorów
#
# @app.get("/actors")
# def get_actors():
#     db = sqlite3.connect("movies-extended.db")
#     cursor = db.cursor()
#
#     # Pobieramy wszystkich aktorów
#     cursor.execute("SELECT id, name, surname FROM actor")
#     actors = cursor.fetchall()
#     db.close()
#
#     # Zamieniamy rekordy na listę słowników
#     return [
#         {"id": a[0], "name": a[1], "surname": a[2]}
#         for a in actors
#     ]
#
#
# #pojedyńczy aktor
# @app.get("/actors/{actor_id}")
# def get_actor(actor_id: int):
#     db = sqlite3.connect("movies-extended.db")
#     cursor = db.cursor()
#
#     actor = cursor.execute(
#         "SELECT id, name, surname FROM actor WHERE id=?",
#         (actor_id,)
#     ).fetchone()
#
#     db.close()
#
#     if actor is None:
#         raise HTTPException(status_code=404, detail="Actor not found")
#
#     return {
#         "id": actor[0],
#         "name": actor[1],
#         "surname": actor[2]
#     }
#
#
# # dodanie aktora
# @app.post("/actors")
# def add_actor(params: dict[str, Any]):
#     # Pobieramy dane z JSON-a
#     name = params.get("name", "").strip()
#     surname = params.get("surname", "").strip()
#
#     # Walidacja
#     if not name or not surname:
#         raise HTTPException(status_code=400, detail="Name and surname are required")
#
#     db = sqlite3.connect("movies-extended.db")
#     cursor = db.cursor()
#
#     # Dodanie do bazy
#     cursor.execute(
#         "INSERT INTO actor (name, surname) VALUES (?, ?)",
#         (name, surname)
#     )
#
#     db.commit()
#     new_id = cursor.lastrowid
#     db.close()
#
#     return {"message": "Actor added", "id": new_id}
#
#
# # aktualizacja aktora
# @app.put("/actors/{actor_id}")
# def update_actor(actor_id: int, params: dict[str, Any]):
#     name = params.get("name")
#     surname = params.get("surname")
#
#     if not name and not surname:
#         raise HTTPException(status_code=400, detail="No data to update")
#
#     fields = []
#     values = []
#
#     # Budujemy zapytanie dynamicznie
#     if name:
#         fields.append("name=?")
#         values.append(name)
#     if surname:
#         fields.append("surname=?")
#         values.append(surname)
#
#     values.append(actor_id)
#
#     db = sqlite3.connect("movies-extended.db")
#     cursor = db.cursor()
#
#     cursor.execute(
#         f"UPDATE actor SET {', '.join(fields)} WHERE id=?",
#         values
#     )
#
#     db.commit()
#     count = cursor.rowcount
#     db.close()
#
#     if count == 0:
#         raise HTTPException(status_code=404, detail="Actor not found")
#
#     return {"message": "Actor updated"}
#
#
#
# # usuwanie aktora
# @app.delete("/actors/{actor_id}")
# def delete_actor(actor_id: int):
#     db = sqlite3.connect("movies-extended.db")
#     cursor = db.cursor()
#
#     cursor.execute("DELETE FROM actor WHERE id=?", (actor_id,))
#     db.commit()
#     count = cursor.rowcount
#     db.close()
#
#     if count == 0:
#         raise HTTPException(status_code=404, detail="Actor not found")
#
#     return {"message": "Actor deleted"}
#
# # aktorzy dla filmu
# @app.get("/movies/{movie_id}/actors")
# def get_movie_actors(movie_id: int):
#     db = sqlite3.connect("movies-extended.db")
#     cursor = db.cursor()
#
#     # Łączymy 3 tabele (JOIN)
#     cursor.execute("""
#         SELECT actor.id, actor.name, actor.surname
#         FROM actor
#         JOIN movie_actor_through mat ON actor.id = mat.actor_id
#         WHERE mat.movie_id = ?
#     """, (movie_id,))
#
#     actors = cursor.fetchall()
#     db.close()
#
#     return [
#         {"id": a[0], "name": a[1], "surname": a[2]}
#         for a in actors
#     ]


#######################################
################################### u góry przed refaktoryzacją

from fastapi import FastAPI, HTTPException
import sqlite3
from typing import Any, List, Dict

app = FastAPI()
DB_EXTENDED = "movies-extended.db"

# ===============================
# Funkcja pomocnicza do połączenia z bazą
# ===============================
def get_db():
    """Zwraca połączenie i kursor do bazy danych"""
    db = sqlite3.connect(DB_EXTENDED)
    cursor = db.cursor()
    return db, cursor

# ===============================
# Funkcje operujące na filmach
# ===============================
def fetch_all_movies() -> List[Dict[str, Any]]:
    db, cursor = get_db()
    cursor.execute("SELECT id, title, director, year, description FROM movie")
    movies = cursor.fetchall()
    db.close()
    return [{"id": m[0], "title": m[1], "director": m[2], "year": m[3], "description": m[4]} for m in movies]

def fetch_movie(movie_id: int) -> Dict[str, Any]:
    db, cursor = get_db()
    movie = cursor.execute(
        "SELECT id, title, director, year, description FROM movie WHERE id=?", (movie_id,)
    ).fetchone()
    db.close()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"id": movie[0], "title": movie[1], "director": movie[2], "year": movie[3], "description": movie[4]}

# ===============================
# Funkcje operujące na aktorach
# ===============================
def fetch_all_actors() -> List[Dict[str, Any]]:
    db, cursor = get_db()
    cursor.execute("SELECT id, name, surname FROM actor")
    actors = cursor.fetchall()
    db.close()
    return [{"id": a[0], "name": a[1], "surname": a[2]} for a in actors]

def fetch_actor(actor_id: int) -> Dict[str, Any]:
    db, cursor = get_db()
    actor = cursor.execute("SELECT id, name, surname FROM actor WHERE id=?", (actor_id,)).fetchone()
    db.close()
    if not actor:
        raise HTTPException(status_code=404, detail="Actor not found")
    return {"id": actor[0], "name": actor[1], "surname": actor[2]}

def insert_actor(name: str, surname: str) -> int:
    db, cursor = get_db()
    cursor.execute("INSERT INTO actor (name, surname) VALUES (?, ?)", (name, surname))
    db.commit()
    new_id = cursor.lastrowid
    db.close()
    return new_id

def update_actor_db(actor_id: int, name: str = None, surname: str = None) -> None:
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
    db, cursor = get_db()
    cursor.execute("DELETE FROM actor WHERE id=?", (actor_id,))
    db.commit()
    count = cursor.rowcount
    db.close()
    if count == 0:
        raise HTTPException(status_code=404, detail="Actor not found")

def fetch_movie_actors_db(movie_id: int) -> List[Dict[str, Any]]:
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

# ===============================
# Endpointy filmów
# ===============================
@app.get("/movies")
def get_movies():
    return fetch_all_movies()

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    return fetch_movie(movie_id)

# ===============================
# Endpointy aktorów
# ===============================
@app.get("/actors")
def get_actors():
    return fetch_all_actors()

@app.get("/actors/{actor_id}")
def get_actor(actor_id: int):
    return fetch_actor(actor_id)


# # stara wersja
# @app.post("/actors")
# def add_actor(params: dict[str, Any]):
#     name = params.get("name", "").strip()
#     surname = params.get("surname", "").strip()
#     if not name or not surname:
#         raise HTTPException(status_code=400, detail="Name and surname are required")
#     new_id = insert_actor(name, surname)
#     return {"message": "Actor added", "id": new_id}

#nowa wersja
# --- Endpoint dodawania aktora ---
@app.post("/actors")
async def add_actor(request: Request):
    # Odczyt JSON z body
    params = await request.json()
    name = params.get("name", "").strip()
    surname = params.get("surname", "").strip()

    if not name or not surname:
        raise HTTPException(status_code=400, detail="Name and surname are required")

    new_id = insert_actor(name, surname)
    return {"message": "Actor added", "id": new_id}

@app.put("/actors/{actor_id}")
def update_actor(actor_id: int, params: dict[str, Any]):
    name = params.get("name")
    surname = params.get("surname")
    update_actor_db(actor_id, name, surname)
    return {"message": "Actor updated"}

@app.delete("/actors/{actor_id}")
def delete_actor(actor_id: int):
    delete_actor_db(actor_id)
    return {"message": "Actor deleted"}

# ===============================
# Endpoint aktorów dla filmu
# ===============================
@app.get("/movies/{movie_id}/actors")
def get_movie_actors(movie_id: int):
    return fetch_movie_actors_db(movie_id)


# Invoke-RestMethod -Uri "http://127.0.0.1:8000/actors/5" -Method Get
