from author.models import Author
from django.db import models, transaction


class Book(models.Model):
    """
    This class represents an Book. \n
    Attributes:
    -----------
    param name: Describes name of the book
    type name: str max_length=128
    param description: Describes description of the book
    type description: str
    param count: Describes count of the book
    type count: int default=10
    param authors: list of Authors
    type authors: list->Author
    """

    id: int

    name = models.CharField(max_length=128, default="")
    description = models.TextField(blank=True, default="")
    count = models.IntegerField(default=1)
    authors = models.ManyToManyField(Author, related_name="books")

    def __str__(self) -> str:
        """
        Magic method is redefined to show all information about Book.
        :return: book id, book name, book description, book count, book authors
        """
        return f"'id': {self.id}, 'name': '{self.name}', 'description': '{self.description}', 'count': {self.count}, 'authors': {[author.id for author in self.authors.all()] if self.authors else []}"

    def __repr__(self) -> str:
        """
        This magic method is redefined to show class and id of Book object.
        :return: class, id
        """
        return f"{self.__class__.__name__}(id={self.id})"

    @staticmethod
    def get_by_id(book_id: int) -> "Book | None":
        """
        :param book_id: SERIAL: the id of a Book to be found in the DB
        :return: book object or None if a book with such ID does not exist
        """
        return Book.objects.filter(id=book_id).first()

    @staticmethod
    def delete_by_id(book_id: int) -> bool:
        """
        :param book_id: an id of a book to be deleted
        :type book_id: int
        :return: True if object existed in the db and was removed or False if it didn't exist
        """
        return Book.objects.filter(id=book_id).delete()[0] > 0

    @staticmethod
    def create(
        name: str,
        description: str,
        count: int = 10,
        authors: list["Author"] | None = None,
    ) -> "Book | None":
        """
        param name: Describes name of the book
        type name: str max_length=128
        param description: Describes description of the book
        type description: str
        param count: Describes count of the book
        type count: int default=10
        param authors: list of Authors
        type authors: list->Author
        :return: a new book object which is also written into the DB
        """

        if not isinstance(name, str) or not name.strip() or len(name) > 128:
            return None

        if not isinstance(description, str):
            return None

        if type(count) is not int or count < 0:
            return None

        if authors and not all(isinstance(author, Author) for author in authors):
            return None

        try:
            with transaction.atomic():
                book = Book.objects.create(
                    name=name,
                    description=description,
                    count=count,
                )
                if authors:
                    book.authors.add(*authors)
                return book
        except Exception:
            return None

    def to_dict(self) -> dict:
        """
        :return: book id, book name, book description, book count, book authors
        :Example:
        | {
        |   'id': 8,
        |   'name': 'django book',
        |   'description': 'bla bla bla',
        |   'count': 10',
        |   'authors': []
        | }
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "count": self.count,
            "authors": [author.to_dict() for author in self.authors.all()],
        }

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        count: int | None = None,
    ) -> None:
        """
        Updates book in the database with the specified parameters.\n
        param name: Describes name of the book
        type name: str max_length=128
        param description: Describes description of the book
        type description: str
        param count: Describes count of the book
        type count: int default=10
        :return: None
        """

        if name is not None and (
            not isinstance(name, str) or not name.strip() or len(name) > 128
        ):
            return

        if description is not None and not isinstance(description, str):
            return

        if count is not None and (type(count) is not int or count < 0):
            return

        if name is not None:
            self.name = name

        if description is not None:
            self.description = description

        if count is not None:
            self.count = count

        self.save()

    def add_authors(self, authors: list["Author"]) -> None:
        """
        Add  authors to  book in the database with the specified parameters.\n
        param authors: list authors
        :return: None
        """
        if not authors or not isinstance(authors, (list, tuple)):
            return

        if not all(isinstance(author, Author) for author in authors):
            return

        self.authors.add(*authors)

    def remove_authors(self, authors: list["Author"]) -> None:
        """
        Remove authors to  book in the database with the specified parameters.\n
        param authors: list authors
        :return: None
        """
        if not authors or not isinstance(authors, (list, tuple)):
            return

        if not all(isinstance(author, Author) for author in authors):
            return

        self.authors.remove(*authors)

    @staticmethod
    def get_all() -> list["Book"]:
        """
        returns data for json request with QuerySet of all books
        """
        return list(Book.objects.all())
