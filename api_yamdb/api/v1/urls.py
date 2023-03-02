from api.v1.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                          ObtainToken, ReviewViewSet, Signup, TitleViewSet,
                          UserViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='user')
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)'
    r'/comments',
    CommentViewSet,
    basename='comments'
)

auth_patterns = ([
    path('signup/', Signup.as_view(), name='signup'),
    path('token/', ObtainToken.as_view(), name='token'),
], 'auth')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include(auth_patterns))

]
