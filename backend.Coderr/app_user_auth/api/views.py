from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.authtoken.models import Token
from ..models import Profile
from .serializers import ProfileSerializer, BusinessProfileSerializer, CustomerProfileSerializer, RegistrationSerializer, LoginSerializer
from django.contrib.auth import authenticate


# ViewSet for retrieving and updating Profile data
class ProfileViewSet(viewsets.GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    # Retrieve a single user profile by ID
    def retrieve(self, request, pk=None):
        profile = self.get_queryset().filter(id=pk).first()
        if not profile:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Partially update a user profile
    def partial_update(self, request, pk=None):
        profile = self.get_queryset().filter(id=pk).first()
        if not profile:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Users can only edit their own profile
        if profile.id != request.user.id:
            return Response(
                {"error": "You are only allowed to edit your own profile."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


# List view for all business profiles (type = 'business')
class BusinessProfileListView(ListAPIView):
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(type='business')


# List view for all customer profiles (type = 'customer')
class CustomerProfileListView(ListAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(type='customer')


# View to handle user registration
class RegistrationView(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # If using token authentication, generate a token for the new user
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View to handle user login and return token
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id
        }, status=status.HTTP_200_OK)