from rest_framework import filters, generics, permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination

from posts.models import Comment, Follow, Group, Post, User

from .permissions import AuthorOrReadOnly
from .serializers import (
    CommentSerializer,
    FollowSerializer,
    GroupSerializer,
    PostSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrReadOnly,)

    def get_queryset(self):
        post = generics.get_object_or_404(Post, pk=self.kwargs.get("post_id"))
        new_querryset = Comment.objects.filter(post=post)
        return new_querryset

    def perform_create(self, serializer):
        post = generics.get_object_or_404(Post, pk=self.kwargs.get("post_id"))
        serializer.save(author=self.request.user, post=post)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("following__username",)

    def get_queryset(self):
        new_queryset = Follow.objects.filter(user=self.request.user)
        return new_queryset

    def perform_create(self, serializer):
        if "following" not in self.request.data:
            raise ValidationError("Отсутсвуют данные для подписки")
        following = generics.get_object_or_404(
            User, username=self.request.data["following"]
        )
        if self.request.user.username == self.request.data["following"]:
            raise ValidationError("Нельзя подписаться на себя")
        if Follow.objects.filter(
                user=self.request.user, following=following).exists():
            raise ValidationError("Подписка уже оформлена")

        serializer.save(user=self.request.user, following=following)
