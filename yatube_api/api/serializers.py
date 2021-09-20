from rest_framework import serializers, validators
from rest_framework.relations import SlugRelatedField
from rest_framework.exceptions import ValidationError

from posts.models import Comment, Follow, Group, Post, User


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "title", "slug", "description")


class PostSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field="username", read_only=True)
    group = GroupSerializer

    class Meta:
        fields = "__all__"
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        fields = "__all__"
        model = Comment


class FollowSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    following = SlugRelatedField(
        slug_field="username",
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = ("user", "following")
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Follow.objects.all(), fields=["user", "following"],
                message="Подписка уже оформлена."
            )
        ]

    def validate(self, data):
        request = self.context.get("request")
        if request.user == data["following"]:
            raise ValidationError("Нельзя подписаться на себя")
        return data

    def create(self, validated_data):
        return Follow.objects.create(**validated_data)
