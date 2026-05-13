from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from contact_app.models import AppUser,City,CountryCode,Festival,Contact,ContactPhoto


# =========================================================
# GROUP LIST SERIALIZER
# =========================================================

class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ["id", "name"]


# =========================================================
# SIGNUP SERIALIZER
# =========================================================

class UserSignupSerializer(serializers.ModelSerializer):

    role = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AppUser

        fields = (
            "id",
            "full_name",
            "email",
            "mobile_number",
            "emp_id",
            "role",
            "password",
            "confirm_password",
            "token",
        )

        extra_kwargs = {
            "full_name": {
                "required": True,
                "error_messages": {
                    "required": "Full name is required",
                    "blank": "Full name cannot be blank",
                }
            },
            "email": {
                "required": True,
                "error_messages": {
                    "required": "Email is required",
                    "blank": "Email cannot be blank",
                }
            },
            "mobile_number" :{
                "required": True,
                "error_messages": {
                    "required": "Mobile number is required",
                    "blank": "Mobile number cannot be blank",
                }
            },
            "emp_id": {
                "required": True,
                "error_messages": {
                    "required": "Employee ID is required",
                    "blank": "Employee ID cannot be blank",
                }
            },
            "password": {
                "write_only": True,
                "validators": [validate_password]
            }
        }

    def get_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key

    def validate(self, attrs):

        email = attrs.get("email")
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        role = attrs.get("role")

        if email is None and email == '':
            raise serializers.ValidationError(_("Email field is required"))

        if role is None and role == '':
            raise serializers.ValidationError(_("Role field is required"))

        if password is None and password == '':
            raise serializers.ValidationError(_("Password field is required"))

        if password != confirm_password:
            raise serializers.ValidationError(_("Password & confirm password should be similer."))

        # Email validation
        if AppUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "email": "Email already exists"
            })

        # Password match
        if password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match"
            })

        # Group exists or not
        if not Group.objects.filter(name=role).exists():
            raise serializers.ValidationError({
                "role": "Invalid role/group"
            })

        return attrs

    def create(self, validated_data):

        role = validated_data.pop("role")
        validated_data.pop("confirm_password")

        password = validated_data.pop("password")

        user = AppUser.objects.create(
            **validated_data
        )

        # Hash password
        user.set_password(password)
        user.save()

        # Assign group
        group = Group.objects.get(name=role)
        user.groups.add(group)

        return user


# =========================================================
# LOGIN SERIALIZER
# =========================================================

class UserLoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    token = serializers.CharField(read_only=True)

    def validate(self, attrs):

        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            email=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                {
                    "message": "Invalid email or password"
                }
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {
                    "message": "User account is disabled"
                }
            )

        token, created = Token.objects.get_or_create(user=user)

        attrs["user"] = user
        attrs["token"] = token.key

        return attrs

# =========================================================
# CITY SERIALIZER
# =========================================================

class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = (
            "id",
            "name",
        )


# =========================================================
# COUNTRY CODE SERIALIZER
# =========================================================

class CountryCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CountryCode
        fields = (
            "id",
            "country_name",
            "country_code",
            "iso_code",
            "is_default",
        )


# =========================================================
# FESTIVAL SERIALIZER
# =========================================================

class FestivalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Festival
        fields = (
            "id",
            "name",
            "festival_date",
        )


# =========================================================
# CONTACT PHOTO SERIALIZER
# =========================================================

class ContactPhotoSerializer(serializers.ModelSerializer):

    image = serializers.ImageField(read_only=True)

    class Meta:
        model = ContactPhoto
        fields = (
            "id",
            "image",
        )


# =========================================================
# CONTACT CREATE SERIALIZER
# =========================================================

class ContactCreateSerializer(serializers.ModelSerializer):

    city_id = serializers.IntegerField(write_only=True)

    country_code_id = serializers.IntegerField(
        write_only=True,
        required=False,
        default=1,
    )

    festival_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
    )

    photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )

    city = CitySerializer(read_only=True)

    country_code = CountryCodeSerializer(read_only=True)

    festivals = FestivalSerializer(
        many=True,
        read_only=True,
    )

    contact_photos = serializers.SerializerMethodField()

    class Meta:
        model = Contact

        fields = (
            "id",
            "uuid",

            "full_name",
            "mobile_number",
            "email",
            "full_address",

            "city_id",
            "country_code_id",

            "festival_ids",
            "photos",

            "city",
            "country_code",
            "festivals",
            "contact_photos",

            "is_gift_reminder",

            "created_at",
        )

    # def get_contact_photos(self, obj):
    #
    #     photos = obj.photos.all()
    #
    #     return ContactPhotoSerializer(
    #         photos,
    #         many=True
    #     ).data
    def get_contact_photos(self, obj):

        return ContactPhotoSerializer(
            obj.photos.all(),
            many=True
        ).data


    def validate_city_id(self, value):

        if not City.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Invalid city id"
            )

        return value

    def validate_country_code_id(self, value):

        if not CountryCode.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Invalid country code id"
            )

        return value

    def create(self, validated_data):

        request = self.context["request"]

        photos = validated_data.pop("photos", [])

        festival_ids = validated_data.pop(
            "festival_ids",
            []
        )

        city_id = validated_data.pop("city_id")

        country_code_id = validated_data.pop(
            "country_code_id",
            1
        )

        city = City.objects.get(id=city_id)

        country_code = CountryCode.objects.get(
            id=country_code_id
        )

        contact = Contact.objects.create(
            city=city,
            country_code=country_code,
            created_by=request.user,
            updated_by=request.user,
            **validated_data
        )

        # festivals
        if festival_ids:

            festivals = Festival.objects.filter(
                id__in=festival_ids
            )

            contact.festivals.set(festivals)

        # photos
        for photo in photos:

            ContactPhoto.objects.create(
                contact=contact,
                image=photo,
                created_by=request.user,
                updated_by=request.user,
            )

        return contact

# =========================================================
# CONTACT LIST SERIALIZER
# =========================================================

class ContactListSerializer(serializers.ModelSerializer):

    role = serializers.SerializerMethodField()
    city = CitySerializer(read_only=True)
    festivals = FestivalSerializer(
        many=True,
        read_only=True,
    )
    contact_photos = ContactPhotoSerializer(
        source="photos",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Contact

        fields = (
            "id",
            "full_name",
            "mobile_number",
            "email",
            "role",
            "full_address",
            "city",
            "role",
            "is_gift_reminder",
            "festivals",
            "contact_photos"
        )

    def get_role(self, obj):

        if obj.created_by and obj.created_by.groups.exists():
            return obj.created_by.groups.first().name

        return None



class UserListSerializer(serializers.ModelSerializer):

    # full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = AppUser

        fields = (
            "id",
            "uuid",
            "full_name",
            "email",
            "mobile_number",
            "emp_id",
            "role",
        )

    # def get_full_name(self, obj):
    #
    #     full_name = f"{obj.first_name} {obj.last_name}"
    #     return full_name.strip()

    def get_role(self, obj):

        if obj.groups.exists():
            return obj.groups.first().name

        return None


# =========================================================
# USER UPDATE SERIALIZER
# =========================================================

class UserUpdateSerializer(serializers.ModelSerializer):

    role = serializers.CharField(required=False)

    class Meta:
        model = AppUser

        fields = (
            "full_name",
            "email",
            "mobile_number",
            "emp_id",
            "role",
        )

    def validate_email(self, value):

        user = self.instance

        if AppUser.objects.exclude(
            id=user.id
        ).filter(email=value).exists():

            raise serializers.ValidationError(
                "Email already exists"
            )

        return value

    def update(self, instance, validated_data):

        role = validated_data.pop("role", None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        # update role/group
        if role:

            group = Group.objects.filter(
                name=role
            ).first()

            if not group:
                raise serializers.ValidationError(
                    {
                        "role": "Invalid role"
                    }
                )

            instance.groups.clear()
            instance.groups.add(group)

        return instance


# =========================================================
# CONTACT UPDATE SERIALIZER
# =========================================================

class ContactUpdateSerializer(serializers.ModelSerializer):

    city_id = serializers.IntegerField(
        required=False
    )

    country_code_id = serializers.IntegerField(
        required=False
    )

    festival_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
    )

    # new images upload
    photos = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
    )

    # remove old images
    deleted_photo_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
    )

    class Meta:
        model = Contact

        fields = (
            "full_name",
            "mobile_number",
            "email",
            "full_address",

            "city_id",
            "country_code_id",

            "festival_ids",

            "photos",
            "deleted_photo_ids",

            "is_gift_reminder",
        )

    def update(self, instance, validated_data):

        request = self.context["request"]

        city_id = validated_data.pop(
            "city_id",
            None
        )

        country_code_id = validated_data.pop(
            "country_code_id",
            None
        )

        festival_ids = validated_data.pop(
            "festival_ids",
            None
        )

        photos = validated_data.pop(
            "photos",
            []
        )

        deleted_photo_ids = validated_data.pop(
            "deleted_photo_ids",
            []
        )

        # ============================================
        # UPDATE CITY
        # ============================================

        if city_id:

            instance.city = City.objects.get(
                id=city_id
            )

        # ============================================
        # UPDATE COUNTRY CODE
        # ============================================

        if country_code_id:

            instance.country_code = CountryCode.objects.get(
                id=country_code_id
            )

        # ============================================
        # UPDATE NORMAL FIELDS
        # ============================================

        for key, value in validated_data.items():

            setattr(instance, key, value)

        instance.updated_by = request.user

        instance.save()

        # ============================================
        # UPDATE FESTIVALS
        # ============================================

        if festival_ids is not None:

            festivals = Festival.objects.filter(
                id__in=festival_ids
            )

            instance.festivals.set(festivals)

        # ============================================
        # DELETE OLD PHOTOS
        # ============================================

        if deleted_photo_ids:

            ContactPhoto.objects.filter(
                id__in=deleted_photo_ids,
                contact=instance
            ).delete()

        # ============================================
        # ADD NEW PHOTOS
        # ============================================

        for photo in photos:

            ContactPhoto.objects.create(
                contact=instance,
                image=photo,
                created_by=request.user,
                updated_by=request.user,
            )

        return instance