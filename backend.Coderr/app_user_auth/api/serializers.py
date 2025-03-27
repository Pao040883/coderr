from rest_framework import serializers
from ..models import Profile
import re


class ProfileSerializer(serializers.ModelSerializer):
    
    user = serializers.IntegerField(source='id', read_only=True) 

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 
            'file', 'location', 'tel', 'description', 
            'working_hours', 'type', 'email', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']

    def validate_email(self, email):
        """Validates that the email is unique."""
        queryset = Profile.objects.filter(email=email)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError("Diese E-Mail ist bereits vergeben.")
        return email

    def validate_tel(self, tel):
        """Validates that the phone number contains only valid characters and is unique."""
        if not re.match(r'^[\d\s\-\+\(\)]+$', tel):
            raise serializers.ValidationError(
                "Telefonnummer darf nur Ziffern und die Zeichen '+', '-', '()', und Leerzeichen enthalten."
            )

        queryset = Profile.objects.filter(tel=tel)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError("Diese Telefonnummer ist bereits vergeben.")
        return tel


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


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = Profile
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({'password': ['Passwörter stimmen nicht überein.']})
        return attrs
    
    def validate_email(self, email):
        if Profile.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': ['Diese Email-Adresse wird bereits verwendet.']})
        return email
    
    def validate_username(self, username):
        if Profile.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': ['Dieser Username wird bereits verwendet.']})
        return username
    
    def create(self, validated_data):
        validated_data.pop('repeated_password')
        user = Profile(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    GUEST_USERS = {
        "andrey": {"password": "asdasd", "type": "customer"},
        "kevin": {"password": "asdasd24", "type": "business"},
    }

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Gastnutzer
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
                raise serializers.ValidationError({"detail": ["Gast-Passwort falsch"]})

        # Normale Benutzerprüfung
        try:
            user = Profile.objects.get(username=username)
        except Profile.DoesNotExist:
            raise serializers.ValidationError({"detail": ["Benutzer existiert nicht"]})

        if not user.check_password(password):
            raise serializers.ValidationError({"detail": ["Passwort ist falsch"]})

        attrs['user'] = user
        return attrs
