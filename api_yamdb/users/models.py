from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractUser):

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Administrator')
    ]
    password = models.CharField(
        'Пароль',
        max_length=128,
        blank=True,
        null=True
    )
    email = models.EmailField(
        'e-mail адрес',
        unique=True,
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль',
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=100,
        null=True,
        default=None
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def send_confirmation_code(self, code):
        send_mail(
            'Код подтверждения от YamDB',
            f'Ваш код подтверждения {code}',
            settings.ADMIN_EMAIL,
            [self.email],
            fail_silently=False,
        )

    def get_token(self):
        refresh = RefreshToken.for_user(self)
        return refresh.access_token

    @property
    def is_admin(self) -> bool:
        """Check if the user is administrator."""
        return self.role == self.ADMIN

    @property
    def is_moderator(self) -> bool:
        """Check if the user is moderator."""
        return self.role == self.MODERATOR
