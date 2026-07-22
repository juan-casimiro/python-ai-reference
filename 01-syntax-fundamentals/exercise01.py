from dataclasses import dataclass
from typing import Protocol


# TODO 1: Define a dataclass `Book` with fields: title (str), author (str), year (int)
@dataclass(frozen=True)
class Book:
    title: str
    author: str
    year: int

    def summary(self) -> str:
        return f"{self.title} by {self.author} ({self.year})"


# TODO 2: Given a list of Book objects, write a comprehension that returns
# titles of books published after 2015 (mirrors your Stream().filter().map())
books = [
    Book("Clean Code", "Robert Martin", 2008),
    Book("another book", "another-author", 2024),
    Book("Focus", "Some-author", 2016),
    Book("The power of now", "Eckhart Tolle", 1999),
]

titles = [b.title for b in books if b.year > 2015]

print(titles)


# TODO 3: Define a Protocol `Summarizable` with a method `summary(self) -> str`
# (this is Python's answer to a Java interface — structural, not declared)
class Summarizable(Protocol):
    def summary(self) -> str: ...


# TODO 4: Write a function `describe(item)` with a type hint that accepts
# anything satisfying Summarizable, and returns item.summary()


def describe(item: Summarizable) -> str:
    return item.summary()


print(books[1].summary())
print(describe(books[1]))


# TODO 5: Use match/case to handle a value that's either an int, a str, or a Book,
# printing a different message for each — compare mentally to the sealed-class
# pattern matching you just did in Java
def describe_type(obj) -> str:
    match obj:
        case int():
            return f"It's an int: {obj}"
        case str():
            return f"It's a string: {obj}"
        case Book():
            return f"It's a book: {obj.title}"
        case _:
            return "Unknown"


print(describe_type(books[1]))
print(describe_type("something"))
