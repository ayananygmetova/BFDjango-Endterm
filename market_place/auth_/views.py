import json

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, status, generics
from rest_framework_simplejwt.tokens import RefreshToken

from common.permissions import AdminPermission, DirectorPermission
from auth_.serializers import UserSerializer, UserDetailsSerializer, RegistrationSerializer, ChangeDetailsSerializer, \
    ChangePasswordSerializer
from common import messages

from common.constants import ADMIN
from core.models import City
from auth_.models import User
import logging

logger = logging.getLogger(__name__)

class UsersView(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.action == 'list' or self.action == 'destroy' or self.action == 'retrieve':
            permission_classes = [AdminPermission, ] or [DirectorPermission, ]
        else:
            permission_classes = [AllowAny, ]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'update':
            return UserDetailsSerializer
        return UserSerializer

    def get_queryset(self):
        if (self.action == 'list' or self.action == 'retrieve' or self.action == 'update') and self.request.user.roles == ADMIN:
            return User.objects.all()
        return User.objects.managers()


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            logger.info(f'login: {str(request.user.username)}')
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'info': 'Logget out'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.error(f'login: {str(request.user.username)} - {str(e)}')
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    def post(self, request):
        try:
            logger.info('new user registered')
            if User.objects.filter(username=request.data.get('username')).first():
                raise Exception(messages.USERNAME_EXISTS)
            serializer = RegistrationSerializer(data={"username": request.data.get('username'),
                                                      "password": request.data.get('password'),
                                                      "email": request.data.get('email'),
                                                      "first_name": request.data.get('first_name'),
                                                      "last_name": request.data.get('last_name')})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'new user registered - {str(e)}')
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ChangeDetailsView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangeDetailsSerializer

    def put(self, request):
        try:
            logger.info(f'{request.user.username} change profile details')
            data = json.loads(request.body)
            serializer = ChangeDetailsSerializer(data=request.data, context={'request': self.request}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.change_details()
            if data.get('password'):
                serializer = ChangePasswordSerializer(data=self.request.data,
                                                      context={'request': self.request})
                serializer.is_valid(raise_exception=True)
                serializer.change_password()
            user = UserDetailsSerializer(request.user)
            return Response(user.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'{request.user.username} change profile details - {str(e)}')
            raise Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CurrentCityView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            data = json.loads(request.body)
            city = City.objects.filter(id=data['city_id']).first()
            if not city:
                raise Exception('Данный город не зарегистрирован в базе данных!')
            user = request.user
            user.cur_city = city
            user.save()
            return Response({'info': 'Current city changed'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)