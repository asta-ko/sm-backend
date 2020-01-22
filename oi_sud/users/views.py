from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from oi_sud.users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'regions', 'favorite_cases']


#
class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['regions', 'favorite_cases']


class CurrentUserView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'data': serializer.data})

    def patch(self, request):
        current_user = request.user
        serializer = UpdateUserSerializer(current_user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            other_serializer = UserSerializer(request.user)
            return Response({'data': other_serializer.data}, status=201)

        return Response({'error': 'wrong parameters', 'e': serializer.errors}, status=400)


class LogoutView(APIView):
    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
