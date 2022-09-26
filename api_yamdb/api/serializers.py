from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class UserForAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role')
        read_only_fields = ('role',)


class TokenSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=None)
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code', 'user')

    def validate(self, data):
        try:
            self.user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            raise exceptions.NotFound({
                'username': 'Пользователь не найден!'
            })

        if data['confirmation_code'] != self.user.confirmation_code:
            raise exceptions.ValidationError({
                'confirmation_code': 'Неверный код подтверждения!'
            })

        return data


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Title
        fields = '__all__'


class TitleWriteSerializer(TitleReadSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Review
        exclude = ('title', )
        read_only_fields = ('id',)

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title = get_object_or_404(
            Title,
            pk=self.context.get('view').kwargs.get('title_id')
        )
        if (request.method == 'POST'
           and Review.objects.filter(title=title, author=author).exists()):
            raise exceptions.ValidationError(
                {'title': 'Может существовать только один отзыв'}
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        exclude = ('review', )
        read_only_fields = ('id',)
