from django.contrib.auth import get_user_model
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
        # validated_data инф полученная после http реквеста и создающая из этого юзера
        return get_user_model().objects.create_user(**validated_data)

