from rest_framework import serializers
from ..models import Profile
import re


# Serializer for viewing and updating Profile data
class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='id', read_only=True)  # Expose 'id' field under the name 'user'

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name',
            'file', 'location', 'tel', 'description',
            'working_hours', 'type', 'email', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']  # These fields cannot be modified by the user

    def validate_email(self, email):
        """Validates that the email is unique."""
        queryset = Profile.objects.filter(email=email)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError("This email address is already in use.")
        return email

    def validate_tel(self, tel):
        """Validates that the phone number contains only valid characters and is unique."""
        if not re.match(r'^[\d\s\-\+\(\)]+$', tel):
            raise serializers.ValidationError(
                "Phone number can only contain digits and the characters '+', '-', '()', and spaces."
            )

        queryset = Profile.objects.filter(tel=tel)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return tel


# Serializer for business profiles with limited fields
class BusinessProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
        ]


# Serializer for customer profiles with a different field set
class CustomerProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'created_at',
            'type',
        ]


# Serializer used for user registration
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = Profile
        fields = ['username', 'email', 'password', 'repeated_password', 'type']

    def validate(self, attrs):
        # Ensure both passwords match
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({'password': ['Passwords do not match.']})
        return attrs

    def validate_email(self, email):
        # Ensure email is unique
        if Profile.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': ['This email address is already in use.']})
        return email

    def validate_username(self, username):
        # Ensure username is unique
        if Profile.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': ['This username is already in use.']})
        return username

    def create(self, validated_data):
        # Remove repeated_password and create user with hashed password
        validated_data.pop('repeated_password')
        user = Profile(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


# Serializer used for login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    # Simulated guest users for quick access
    GUEST_USERS = {
        "andrey": {"password": "asdasd", "type": "customer"},
        "kevin": {"password": "asdasd24", "type": "business"},
    }

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Handle guest users
        if username in self.GUEST_USERS:
            guest = self.GUEST_USERS[username]
            if password == guest["password"]:
                user, _ = Profile.objects.get_or_create(
                    username=username,
                    defaults={
                        "email": f"{username}@guest.com",
                        "type": guest["type"]
                    }
                )
                attrs["user"] = user
                return attrs
            else:
                raise serializers.ValidationError({"detail": ["Incorrect guest password."]})

        # Handle regular users
        try:
            user = Profile.objects.get(username=username)
        except Profile.DoesNotExist:
            raise serializers.ValidationError({"detail": ["User does not exist."]})

        if not user.check_password(password):
            raise serializers.ValidationError({"detail": ["Incorrect password."]})

        attrs['user'] = user
        return attrs