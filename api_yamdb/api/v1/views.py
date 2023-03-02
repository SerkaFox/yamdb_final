from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from reviews.models import Category, Genre, Review, Title, User
from api.v1.filters import TitleFilter
from api.v1.permissions import (AdministratorOrReadOnly, AuthorOrReadOnly,
                                IsAdministrator, IsModerator)
from api.v1.serializers import (CategorySerializer, CommentSerializer,
                                GenreSerializer, ReviewSerializer,
                                SignupSerializer, TitleReadSerializer,
                                TitleWriteSerializer, TokenSerializer,
                                UserSerializer)


class CreateListDeleteViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    pass


class CategoryViewSet(CreateListDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdministratorOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdministratorOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    Getting a list of works,
    obtaining a separate work,
    update, deletion of a separate work.
    """
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all()
    permission_classes = (AdministratorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [AuthorOrReadOnly | IsModerator | IsAdministrator]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [AuthorOrReadOnly | IsModerator | IsAdministrator]

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get("review_id"),
            title=self.kwargs.get('title_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, review=review)


class Signup(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ObtainToken(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdministrator & IsAuthenticated]
    pagination_class = PageNumberPagination
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated],
        url_name='me',
        url_path='me'
    )
    def personal_detail(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = UserSerializer(
                request.user,
                data=request.data,
                request_method=request.method,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
