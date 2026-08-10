import datetime
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

ROLE_CHOICES = (
    (0, 'visitor'),
    (1, 'admin'),
)

class CustomUser(models.Model):
    """
        This class represents a basic user. \n
        Attributes:
        -----------
        param first_name: Describes first name of the user
        type first_name: str max length=20
        param last_name: Describes last name of the user
        type last_name: str max length=20
        param middle_name: Describes middle name of the user
        type middle_name: str max length=20
        param email: Describes the email of the user
        type email: str, unique, max length=100
        param password: Describes the password of the user
        type password: str
        param created_at: Describes the date when the user was created. Can't be changed.
        type created_at: int (timestamp)
        param updated_at: Describes the date when the user was modified
        type updated_at: int (timestamp)
        param role: user role, default role (0, 'visitor')
        type updated_at: int (choices)
        param is_active: user role, default value False
        type updated_at: bool

    """
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=20)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    role = models.IntegerField(choices=ROLE_CHOICES, default=0)
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        current_time = timezone.now()
        
        if not self.created_at:
            self.created_at = current_time
        self.updated_at = current_time
        
        super(CustomUser, self).save(*args, **kwargs)

    def __str__(self):
        """
        Magic method is redefined to show all information about CustomUser.
        :return: user id, user first_name, user middle_name, user last_name,
                 user email, user password, user updated_at, user created_at,
                 user role, user is_active
        """
        c_timestamp = int(self.created_at.timestamp()) if self.created_at else 0
        u_timestamp = int(self.updated_at.timestamp()) if self.updated_at else 0
        return (f"'id': {self.id}, "
                f"'first_name': '{self.first_name}', "
                f"'middle_name': '{self.middle_name}', "
                f"'last_name': '{self.last_name}', "
                f"'email': '{self.email}', "
                f"'created_at': {c_timestamp}, "
                f"'updated_at': {u_timestamp}, "
                f"'role': {self.role}, "
                f"'is_active': {self.is_active}")

    def __repr__(self):
        """
        This magic method is redefined to show class and id of CustomUser object.
        :return: class, id
        """
        return f"CustomUser(id={self.id})"

    @staticmethod
    def get_by_id(user_id):
        """
        :param user_id: SERIAL: the id of a user to be found in the DB
        :return: user object or None if a user with such ID does not exist
        """
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None

    @staticmethod
    def get_by_email(email):
        """
        Returns user by email
        :param email: email by which we need to find the user
        :type email: str
        :return: user object or None if a user with such ID does not exist
        """
        try:
            return CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return None

    @staticmethod
    def delete_by_id(user_id):
        """
        :param user_id: an id of a user to be deleted
        :type user_id: int
        :return: True if object existed in the db and was removed or False if it didn't exist
        """
        try:
            user = CustomUser.objects.get(id=user_id)
            user.delete()
            return True
        except CustomUser.DoesNotExist:
            return False

    @staticmethod
    def create(email, password, first_name=None, middle_name=None, last_name=None):
        """
        :param first_name: first name of a user
        :type first_name: str
        :param middle_name: middle name of a user
        :type middle_name: str
        :param last_name: last name of a user
        :type last_name: str
        :param email: email of a user
        :type email: str
        :param password: password of a user
        :type password: str
        :return: a new user object which is also written into the DB
        """
        if (first_name and len(first_name) > 20) or \
           (middle_name and len(middle_name) > 20) or \
           (last_name and len(last_name) > 20):
            return None
        if CustomUser.objects.filter(email=email).exists():
            return None
        try:
            validate_email(email)
        except ValidationError:
            return None

        try:
            user = CustomUser(
                email=email,
                password=password,
                first_name=first_name if first_name else "",
                middle_name=middle_name if middle_name else "",
                last_name=last_name if last_name else ""
            )
            user.save()
            return user
        except Exception:
            return None

    def to_dict(self):
        """
        :return: user id, user first_name, user middle_name, user last_name,
                 user email, user password, user updated_at, user created_at, user is_active
        :Example:
        | {
        |   'id': 8,
        |   'first_name': 'fn',
        |   'middle_name': 'mn',
        |   'last_name': 'ln',
        |   'email': 'ln@mail.com',
        |   'created_at': 1509393504,
        |   'updated_at': 1509402866,
        |   'role': 0
        |   'is_active:' True
        | }
        """
        c_timestamp = int(self.created_at.timestamp()) if self.created_at else 0
        u_timestamp = int(self.updated_at.timestamp()) if self.updated_at else 0
        return {
            'id': self.id,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'email': self.email,
            'created_at': c_timestamp,
            'updated_at': u_timestamp,
            'role': self.role,
            'is_active': self.is_active
        }

    def update(self,
               first_name=None,
               middle_name=None,
               last_name=None,
               password=None,
               role=None,
               is_active=None):
        """
        Updates user profile in the database with the specified parameters.\n
        :param first_name: first name of a user
        :type first_name: str
        :param middle_name: middle name of a user
        :type middle_name: str
        :param last_name: last name of a user
        :type last_name: str
        :param password: password of a user
        :type password: str
        :param role: role id
        :type role: int
        :param is_active: activation state
        :type is_active: bool
        :return: None
        """
        if first_name is not None:
            self.first_name = first_name
        if middle_name is not None:
            self.middle_name = middle_name
        if last_name is not None:
            self.last_name = last_name
        if password is not None:
            self.password = password
        if role is not None:
            self.role = role
        if is_active is not None:
            self.is_active = is_active
        self.save()

    @staticmethod
    def get_all():
        """
        returns data for json request with QuerySet of all users
        """
        return CustomUser.objects.all()

    def get_role_name(self):
        """
        returns str role name
        """
        return self.get_role_display()
