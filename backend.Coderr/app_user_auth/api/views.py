from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.authtoken.models import Token
from ..models import Profile
from .serializers import ProfileSerializer, BusinessProfileSerializer, CustomerProfileSerializer, RegistrationSerializer, LoginSerializer
from django.contrib.auth import authenticate


class ProfileViewSet(viewsets.GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        profile = self.get_queryset().filter(id=pk).first()
        if not profile:
            return Response({"error": "Das Benutzerprofil wurde nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        profile = self.get_queryset().filter(id=pk).first()
        if not profile:
            return Response({"error": "Das Benutzerprofil wurde nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        if profile.id != request.user.id:
            return Response({"error": "Sie dürfen nur Ihr eigenes Profil bearbeiten."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessProfileListView(ListAPIView):
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(type='business')


class CustomerProfileListView(ListAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(type='customer')


class RegistrationView(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Falls du Token-Authentifizierung nutzt, erstelle direkt ein Token für den Nutzer
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key, 
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(generics.GenericAPIView):

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]

            user = authenticate(username=username, password=password)

            if user is None:
                return Response({"error": "Ungültige Anmeldeinformationen"}, status=status.HTTP_400_BAD_REQUEST)

            # Token generieren oder abrufen
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)