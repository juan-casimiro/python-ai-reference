from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# TODO 1: Define a Pydantic model `Book` with fields: title (str), author (str), year (int)
# This is your DTO/validation layer — like a @Valid-annotated request body class in Spring


class Book(BaseModel):
    title: str
    author: str
    year: int


# TODO 2: In-memory "database" — just a list, same as your reference library exercises
books = [
    Book(title="Clean Code", author="Robert Martin", year=2008),
    Book(title="another book", author="another-author", year=2024),
    Book(title="Focus", author="Some-author", year=2016),
    Book(title="The power of now", author="Eckhart Tolle", year=1999),
]

# TODO 3: GET /books — return the full list


@app.get("/books")
def get_books():
    return books


# TODO 4: POST /books — accept a Book in the request body, append it to `books`, return it
@app.post("/books")
def post_books(book: Book):
    books.append(book)
    return book


# TODO 5: GET /books/{index} — return a single book by its position in the list
# (handle the case where index is out of range — return a 404)
@app.get("/books/{index}")
def get_books_by_index(index: int):
    if index < 0 or index >= len(books):
        raise HTTPException(status_code=404, detail="Book not found")

    return books[index]
