from rest_framework import generics, authentication, permissions
# создает токен направляя его в юрл
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new token for user"""
    serializer_class = AuthTokenSerializer
    #  визуализация базы данных в браузере, что бы логинится
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication)
    # доступы в нашем случает нет специальных доступов юзер может быть просто залогинен
    permissions_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrive and return auth user"""
        # Retrive -извлекать
        return self.request.user