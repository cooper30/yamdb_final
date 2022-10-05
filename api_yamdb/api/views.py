from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title

from .filters import TitleFilter
from .mixins import CustomViewSet
from .permissions import (IsAdminOnly, IsAdminUserOrReadOnly,
                          IsStaffOrAuthorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          TokenSerializer, UserForAdminSerializer,
                          UserSerializer)

User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    """
    Работа с пользователями
    """
    queryset = User.objects.all()
    serializer_class = UserForAdminSerializer
    permission_classes = (IsAuthenticated, IsAdminOnly)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def get_current_user_info(self, request):
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UserForAdminSerializer(
                    request.user,
                    data=request.data,
                    partial=True
                )
            else:
                serializer = UserSerializer(
                    request.user,
                    data=request.data,
                    partial=True
                )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class Signup(APIView):
    """
    Получить код подтверждения по email.
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
        else:
            try:
                user = User.objects.get(
                    email=serializer.data.get('email'),
                    username=serializer.data.get('username')
                )
            except User.DoesNotExist:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)

        self.send_confirmation_code(
            user.username,
            user.email,
            user.confirmation_code
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def send_confirmation_code(username, email, confirmation_code):
        email_body = (
            f'Пользователь {username} успешно зарегистрирован!'
            f'\nКод подтвержения для доступа к API: '
            f'{confirmation_code}'
        )
        send_mail(
            'Код подтвержения для доступа к API!',
            email_body,
            settings.EMAIL_ADMIN,
            recipient_list=[email],
        )


class JWTToken(APIView):
    """
    Получение JWT-токена по username и confirmation code.
    """

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {
                    'token': str(
                        RefreshToken.for_user(
                            serializer.user
                        ).access_token
                    )
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseViewSet(CustomViewSet):
    """
    Базовый класс для работы с категориями и жанрами.
    """
    permission_classes = (IsAdminUserOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(BaseViewSet):
    """
    Работа с категориями.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseViewSet):
    """
    Работа с жанрами.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    Работа с произведениями.
    """
    queryset = Title.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return TitleWriteSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Проставление оценок для публикаций.
    Получение оценки по id публикации.
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsStaffOrAuthorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Комментирование оценок к публикациям.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsStaffOrAuthorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
