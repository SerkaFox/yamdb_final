from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User


class Genre(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='slug жанра',
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название  категории'
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='slug категории',
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=250,
        verbose_name='Название'
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True, blank=True,
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        verbose_name='Категория',
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
    )
    year = models.IntegerField(verbose_name='Дата выхода',)

    class Meta:
        ordering = ('year',)
        default_related_name = 'titles'
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'category'),
                name='unique_category'
            )
        ]

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(1, 'Допустимы значения от 1 до 10'),
            MaxValueValidator(10, 'Допустимы значения от 1 до 10')
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        default_related_name = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]

    def __str__(self):
        return f'{self.author} - {self.title.name} - {self.text[30:]}...'


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['pub_date']

    def __str__(self):
        return f'{self.author} - {self.review.text[30:]} - {self.text[30:]}...'
