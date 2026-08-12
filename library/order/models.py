from datetime import datetime

from authentication.models import CustomUser
from book.models import Book
from django.db import models
from django.utils import timezone


class Order(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    end_at = models.DateTimeField(null=True, blank=True)
    plated_end_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        """
        Magic method is redefined to show all information about Order.
        :return: book id, book name, book description, book count, book authors
        """
        end_at_val = f"'{self.end_at}'" if self.end_at else None

        return (
            f"'id': {self.id}, "
            f"'user': {self.user!r}, "
            f"'book': {self.book!r}, "
            f"'created_at': '{self.created_at}', "
            f"'end_at': {end_at_val}, "
            f"'plated_end_at': '{self.plated_end_at}'"
        )

    def __repr__(self) -> str:
        """
        This magic method is redefined to show class and id of Order object.
        :return: class, id
        """
        return f"{self.__class__.__name__}(id={self.id})"

    @staticmethod
    def _ensure_datetime(value: datetime | int) -> datetime:
        if isinstance(value, int):
            current_tz = timezone.get_current_timezone()
            return datetime.fromtimestamp(value, tz=current_tz)
        return value

    def to_dict(self) -> dict:
        """
        :return: dict contains order id, book id, user id, order created_at, order end_at, order plated_end_at
        :Example:
        | {
        |   'id': 8,
        |   'book': 8,
        |   'user': 8',
        |   'created_at': 1509393504,
        |   'end_at': 1509393504,
        |   'plated_end_at': 1509402866,
        | }
        """
        return {
            "id": self.id,
            "book": self.book.id,
            "user": self.user.id,
            "created_at": self.created_at,
            "end_at": self.end_at,
            "plated_end_at": self.plated_end_at,
        }

    @staticmethod
    def create(
        user: CustomUser, book: Book, plated_end_at: datetime | int
    ) -> "Order | None":
        """
        :param user: the user who took the book
        :type user: CustomUser
        :param book: the book they took
        :type book: Book
        :param plated_end_at: planned return of data
        :type plated_end_at: int (timestamp)
        :return: a new order object which is also written into the DB
        """
        if user._state.adding or book._state.adding:
            return

        active_orders_for_this_book = Order.objects.filter(book=book).count()

        if active_orders_for_this_book >= book.count:
            return

        return Order.objects.create(
            user=user,
            book=book,
            plated_end_at=Order._ensure_datetime(plated_end_at),
        )

    @staticmethod
    def get_by_id(order_id: int) -> "Order | None":
        """
        :param order_id:
        :type order_id: int
        :return:  the object of the order, according to the specified id or null in case of its absence
        """
        return Order.objects.filter(id=order_id).first()

    def update(
        self,
        plated_end_at: datetime | int | None = None,
        end_at: datetime | int | None = None,
    ) -> None:
        """
        Updates order in the database with the specified parameters.\n
        :param plated_end_at: new plated_end_at
        :type plated_end_at: int (timestamp)
        :param end_at: new end_at
        :type plated_end_at: int (timestamp)
        :return: None
        """

        if plated_end_at is not None:
            self.plated_end_at = self._ensure_datetime(plated_end_at)
        if end_at is not None:
            self.end_at = self._ensure_datetime(end_at)
        self.save()

    @staticmethod
    def get_all() -> list["Order"]:
        """
        :return: all orders
        """
        return list(Order.objects.all())

    @staticmethod
    def get_not_returned_books() -> list["Order"]:
        """
        :return:  all orders that do not have a return date (end_at)
        """
        return list(Order.objects.filter(end_at__isnull=True))

    @staticmethod
    def delete_by_id(order_id: int) -> bool:
        """
        :param order_id: an id of a user to be deleted
        :type order_id: int
        :return: True if object existed in the db and was removed or False if it didn't exist
        """
        order = Order.objects.filter(id=order_id).first()
        if order:
            order.delete()
            return True
        return False
