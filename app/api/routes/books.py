"""
Extensions CRUD for books
"""

from datetime import datetime

import logging

from typing import Optional, List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

logger = logging.getLogger(__name__)

class BookBase(BaseModel):
    """
    Schéma de base pour un livre.
    Contient les champs communs à la création et à la mise à jour.
    """

    title: str = Field(..., min_length=1, max_length=200, description="Titre du livre")
    author: str = Field(..., min_length=1, max_length=100, description="Auteur du livre")
    isbn: str = Field(
        ..., pattern=r"^[\d-]+$", description="ISBN du livre (format: 978-0451524935)"
    )
    published_year: int = Field(
        ..., ge=1000, le=datetime.now().year, description="Année de publication"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "1984",
                "author": "George Orwell",
                "isbn": "978-0451524935",
                "published_year": 1949,
            }
        }
    )


class BookCreate(BookBase):
    """
    Schéma pour créer un nouveau livre.
    Hérite de BookBase, peut ajouter des champs spécifiques à la création.
    """

    pass


class BookUpdate(BaseModel):
    """
    Schéma pour mettre à jour un livre.
    Tous les champs sont optionnels (on peut modifier seulement certains champs).
    """

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    isbn: Optional[str] = Field(None, pattern=r"^[\d-]+$")
    published_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    available: Optional[bool] = None


class Book(BookBase):
    """
    Schéma complet d'un livre (avec ID).
    Utilisé pour les réponses de l'API.
    """

    id: int = Field(..., description="Identifiant unique du livre")
    available: bool = Field(default=True, description="Disponibilité du livre")
    created_at: datetime = Field(default_factory=datetime.now, description="Date de création")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "1984",
                "author": "George Orwell",
                "isbn": "978-0451524935",
                "published_year": 1949,
                "available": True,
                "created_at": "2024-01-15T10:30:00",
            }
        }
    )



books_db: List[dict] = [
    {
        "id": 1,
        "title": "1984",
        "author": "George Orwell",
        "isbn": "978-0451524935",
        "published_year": 1949,
        "available": True,
        "created_at": datetime(2024, 1, 1, 10, 0, 0),
    },
    {
        "id": 2,
        "title": "Le Petit Prince",
        "author": "Antoine de Saint-Exupéry",
        "isbn": "978-2070612758",
        "published_year": 1943,
        "available": True,
        "created_at": datetime(2024, 1, 1, 10, 0, 0),
    },
    {
        "id": 3,
        "title": "Harry Potter à l'école des sorciers",
        "author": "J.K. Rowling",
        "isbn": "978-2070584628",
        "published_year": 1997,
        "available": False,
        "created_at": datetime(2024, 1, 1, 10, 0, 0),
    },
    {
        "id": 4,
        "title": "Les Misérables",
        "author": "Victor Hugo",
        "isbn": "978-2070409228",
        "published_year": 1862,
        "available": True,
        "created_at": datetime(2024, 1, 1, 10, 0, 0),
    },
]

NEXT_ID = 5

def find_book_by_id(book_id: int) -> Optional[dict]:

    """
    Recherche un livre par son ID

    Args :
    book-id (int) : L'identifiant du livre

    Returns :
    Optionnal[dict] : Livre si trouvé, None sinon
    """
    for book in books_db:
        if book ["id"]==books_db:
            return book
    return None


def find_book_by_isbn(book_isbn: str) -> Optional[dict]:

    """
    Recherche un livre par son ISBN

    Args :
     : L'identifiant du livre

    Returns :
    Optionnal[dict] : Livre si trouvé, None sinon
    """
    for book in books_db:
        if book ["isbn"]==book_isbn:
            return book
    return None

@router.get("/", response_model=List[Book], status_code=status.HTTP_200_OK)
async def get_all_books(available: Optional[bool] = None, author: Optional[str] = None):
    """
    Récupère la liste de tous les livres.

    Paramètres de filtrage optionnels :
    - available: Filtrer par disponibilité (true/false)
    - author: Filtrer par auteur (recherche partielle, insensible à la casse)

    Returns:
        Liste des livres correspondant aux critères
    """
    result = books_db.copy()

    logger.info(f"GET /books/ - Filtres: available={available}, author={author}")

    if available is not None:
        result = [book for book in result if book["available"] == available]

    if author:
        result = [book for book in result if author.lower() in book["author"].lower()]

    logger.info(f"Retour de {len(result)} livres")

    return result


@router.get("/{book_id}", response_model=Book, status_code=status.HTTP_200_OK)
async def get_book(book_id: int):
    """
    Récupère les détails d'un livre spécifique par son ID.

    Args:
        book_id: L'identifiant du livre

    Returns:
        Les informations complètes du livre

    Raises:
        HTTPException 404: Si le livre n'existe pas
    """
    book = find_book_by_id(book_id)

    if not book:
        logger.warning(f"Livre {book_id} non trouvé")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Le livre avec l'ID {book_id} n'existe pas",
        )

    logger.info(f"Livre {book_id} trouvé: {book['title']}")
    return book


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate):
    """
    Crée un nouveau livre dans la bibliothèque.

    Args:
        book: Les informations du livre à créer

    Returns:
        Le livre créé avec son ID et sa date de création

    Raises:
        HTTPException 400: Si un livre avec le même ISBN existe déjà
    """
    global NEXT_ID

    existing_book = find_book_by_isbn(book.isbn)
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Un livre avec l'ISBN {book.isbn} existe déjà (ID: {existing_book['id']})",
        )

    new_book = {
        "id": NEXT_ID,
        **book.model_dump(),
        "available": True,
        "created_at": datetime.now(),
    }

    books_db.append(new_book)
    NEXT_ID += 1

    return new_book


@router.put("/{book_id}", response_model=Book, status_code=status.HTTP_200_OK)
async def update_book(book_id: int, book_update: BookUpdate):
    """
    Met à jour les informations d'un livre existant.
    Seuls les champs fournis sont modifiés.

    Args:
        book_id: L'identifiant du livre à modifier
        book_update: Les champs à mettre à jour

    Returns:
        Le livre mis à jour

    Raises:
        HTTPException 404: Si le livre n'existe pas
        HTTPException 400: Si l'ISBN modifié existe déjà sur un autre livre
    """
    book = find_book_by_id(book_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Le livre avec l'ID {book_id} n'existe pas",
        )

    update_data = book_update.model_dump(exclude_unset=True)
    if "isbn" in update_data:
        existing_book = find_book_by_isbn(update_data["isbn"])
        if existing_book and existing_book["id"] != book_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Un autre livre utilise déjà l'ISBN {update_data['isbn']}",
            )

    book.update(update_data)

    return book