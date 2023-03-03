import uuid
from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, EmailField, empty
from reviews.models import Category, Comment, Genre, Review, Title, User


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for categories.
    """

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """
    Serializer for Genre.
    """

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Serializer for Title. Method Get.
    """
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for Title. Methods: POST, PATCH, DELETE.
    """
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, value):
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего!'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review. Methods: GET, POST, PATCH, DELETE.
    """
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    def validate(self, data):
        request = self.context['request']
        if request.method != 'POST':
            return data
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if Review.objects.filter(title=title, author=author).exists():
            raise ValidationError('Вы не можете добавить более'
                                  'одного отзыва на произведение')
        return data

    class Meta:
        model = Review
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment. Methods: GET, POST, PATCH, DELETE.
    """
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'


class SignupSerializer(serializers.Serializer):
    """
    Serializer for Signup(APIView). Method: POST.
    """
    username = CharField(
        help_text=(
            'Обязательное поле. Не более 150 символов. '
            'Только буквы, цифры и символы @/./+/-/_.'
        ),
        label='Имя пользователя',
        max_length=150
    )
    email = EmailField(label='E-mail адрес', max_length=254)

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                'Имя "me" использовать нельзя!'
            )
        try:
            obj1 = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            obj1 = None
        try:
            obj2 = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            obj2 = None
        if obj1 == obj2:
            return data
        raise serializers.ValidationError(
            'Сочетание имени пользователя и пароля содержит ошибку!'
        )

    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            email=validated_data['email'],
            username=validated_data['username']
        )
        if created:
            user.is_active = False
        user.confirmation_code = uuid.uuid4()
        user.send_confirmation_code(user.confirmation_code)
        user.save()
        return user


class TokenSerializer(serializers.Serializer):
    """
    Serializer for ObtainToken(APIView). Method: POST.
    """
    username = serializers.CharField(
        write_only=True
    )
    confirmation_code = serializers.CharField(
        max_length=100,
        write_only=True
    )
    token = serializers.CharField(
        read_only=True
    )

    def create(self, validated_data):
        user = get_object_or_404(User, username=validated_data['username'])
        if user.confirmation_code != validated_data['confirmation_code']:
            raise serializers.ValidationError(
                'Код подтверждения неверен!'
            )
        user.is_active = True
        user.confirmation_code = None
        user.save()
        token = user.get_token()
        self.validated_data['token'] = token
        return self.validated_data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User. Methods: GET, POST, PATCH, DELETE.
    """

    def __init__(self, instance=None, data=empty, **kwargs):
        self.request_method = kwargs.pop('request_method', 'GET')
        super().__init__(instance, data, **kwargs)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role"
        ]

    def validate(self, data):
        if self.request_method != 'GET' and 'role' in data.keys():
            data.pop('role')
        return data
