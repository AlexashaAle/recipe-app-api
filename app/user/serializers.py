from django.contrib.auth import get_user_model, authenticate
# при выводе любых сообщений на экран на любом языка
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

# сериализатор переводить данные из джонсон и обратно


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users objects"""

    class Meta:
        model = get_user_model()
        # определяем поля для конвертации при реквесте
        fields = ('email', 'password', 'name')
        # специальные условия для пароля
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        # validated_data инф полученная после http реквеста и создающая юзера
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user , setting the password correctly and return it"""
        # instance- премер
        # вытаскиваем пороль, из подтвержденых данных
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        # если юзер изменил пароль меняем его
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Seriakizer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': "password"},
        #  по умолчани джанго удаляет пробел, тут мы этого избегаем
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validete and authenticate the user"""
        # validate - подтвердить
        # attrs -  это поля заданные в сериализаторе выше

        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            # отправляет в окружение и направляет запрос в сериализатор
            request=self.context.get('request'),
            username=email,
            password=password
        )
        #  если не вышло аторизоваться
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            # ловит ошибку валидации и показывает сообщение
            raise serializers.ValidationError(msg, code='authorization')
        # сохраняем юзера подтвержденным
        attrs['user'] = user
        # возвращаем данные
        return attrs
