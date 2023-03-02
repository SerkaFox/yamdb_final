from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    """
    Ordinary user permission class.
    Authenticated user (user) - can read everything,
    can publish reviews and rate works (movies / books / songs),
    can comment on reviews;
    can edit and delete their reviews and comments,
    edit their ratings of works.
    This role is assigned by default to every new user.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class AdministratorOrReadOnly(permissions.BasePermission):
    """
    Special permission class.
    Unauthenticated user (user) - can read everything,
    Administrator - has full rights to manage all project content.
    Can create and delete works, categories and genres.
    Can assign roles to users.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAdministrator(permissions.BasePermission):
    """
    Administrator permission class.
    Administrator (admin) has full rights to manage all project content.
    Can create and delete works, categories and genres.
    Can assign roles to users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )


class IsModerator(permissions.BasePermission):
    """Moderator permission class.
    Moderator (moderator) has the same rights as an Authenticated User,
    plus the right to delete and edit any reviews and comments.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_moderator
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user.is_moderator
        )
