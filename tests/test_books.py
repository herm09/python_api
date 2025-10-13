import pytest

from fastapi.testclient import TestClient

from app.api.routes.books import books_db

from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_database():
    original_db = books_db.copy()

    # le test s'exécute ici
    yield

    books_db.clear()
    books_db.extend(original_db)

def test_get_all_books():
    """
    Test que GET /books retourne tous les livres.
    """
    response = client.get("/books/")

    assert response.status_code == 200
    books = response.json()
    assert isinstance(books, list)
    assert len(books) == 4  # On a 4 livres dans la DB initiale

    # Vérifier la structure du premier livre
    first_book = books[0]
    assert "id" in first_book
    assert "title" in first_book
    assert "author" in first_book
    assert "isbn" in first_book
    assert "available" in first_book

def test_get_books_filter_author():
    """
    Test que GET /books/ author=John retourne tous les livres de John.
    """
    response = client.get("books/?author=J.K. Rowling")

    assert response.status_code == 200
    books = response.json()
    assert isinstance(books, list)
    assert len(books) == 1

    for book in books:
        assert book["author"] == "J.K. Rowling"
        assert book["available"] is False
        assert isinstance(book["id"], int)
        assert isinstance(book["isbn"], str)
        assert isinstance(book["title"], str)
        assert isinstance(book["author"], str)