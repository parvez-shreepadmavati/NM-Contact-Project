from django.contrib.auth.models import Group

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from contact_app.models import AppUser, City, CountryCode, Festival, Contact, ContactPhoto, GIFT_STATUS_CHOICES

from .serializers import (
    GroupSerializer,
    UserLoginSerializer,
    UserSignupSerializer,
    CitySerializer,
    CountryCodeSerializer,
    FestivalSerializer,
    ContactCreateSerializer,
    ContactListSerializer,
    UserListSerializer,
    UserUpdateSerializer,
    ContactUpdateSerializer,
    ContactStatusUpdateSerializer,
    GiftStatusSerializer
)


# =========================================================
# AUTH VIEWSET
# =========================================================

class AuthViewSet(GenericViewSet):

    queryset = AppUser.objects.all()

    # =====================================================
    # SIGNUP API
    # =====================================================

    @action(
        methods=["post"],
        detail=False,
        permission_classes=[AllowAny],
        url_path="signup",
    )
    def signup(self, request):

        serializer = UserSignupSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            {
                "success": True,
                "message": "User registered successfully",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    # =====================================================
    # LOGIN API
    # =====================================================

    @action(
        methods=["post"],
        detail=False,
        permission_classes=[AllowAny],
        url_path="login",
    )
    def login(self, request):

        serializer = UserLoginSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token = serializer.validated_data["token"]

        return Response(
            {
                "success": True,
                "message": "Login successful",
                "data": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "mobile_number": user.mobile_number,
                    "emp_id": user.emp_id,
                    "role": user.groups.first().name if user.groups.exists() else None,
                    "is_staff" :user.is_staff,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser,
                    "token": token,
                },
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # LOGOUT API
    # =====================================================
    @action(
        methods=["post"],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path="logout",
    )
    def logout(self, request):
        Token.objects.filter(
            user=request.user
        ).delete()

        return Response(
            {
                "success": True,
                "message": "Logout successful",
            },
            status=status.HTTP_200_OK
        )

    # =====================================================
    # GROUP LIST API
    # =====================================================

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path="role-list",
    )
    def group_list(self, request):

        groups = Group.objects.all().order_by("name")

        serializer = GroupSerializer(
            groups,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Group list fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# CITY API
# =========================================================

class CityViewSet(
    ListModelMixin,
    GenericViewSet,
):

    queryset = City.objects.filter(
        is_deleted=False,
        is_active=True,
    )

    serializer_class = CitySerializer

    permission_classes = [IsAuthenticated]


# =========================================================
# COUNTRY CODE API
# =========================================================

class CountryCodeViewSet(
    ListModelMixin,
    GenericViewSet,
):

    queryset = CountryCode.objects.filter(
        is_deleted=False,
        is_active=True,
    )

    serializer_class = CountryCodeSerializer

    permission_classes = [IsAuthenticated]


# =========================================================
# FESTIVAL API
# =========================================================

class FestivalViewSet(
    ListModelMixin,
    GenericViewSet,
):

    queryset = Festival.objects.filter(
        is_deleted=False,
        is_active=True,
    )

    serializer_class = FestivalSerializer

    permission_classes = [IsAuthenticated]


# =========================================================
# CONTACT API
# =========================================================

# class ContactViewSet(
#     CreateModelMixin,
#     ListModelMixin,
#     RetrieveModelMixin,
#     GenericViewSet,
# ):
#
#     serializer_class = ContactCreateSerializer
#
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#
#         return Contact.objects.filter(
#             is_deleted=False,
#             created_by=self.request.user,
#         ).select_related(
#             "city",
#             "country_code",
#         ).prefetch_related(
#             "festivals",
#             "photos",
#         ).order_by("-created_at")
#
#     # =====================================================
#     # DYNAMIC SERIALIZER
#     # =====================================================
#
#     def get_serializer_class(self):
#         if self.action in ["list", "retrieve"]:
#             return ContactListSerializer
#
#         return ContactCreateSerializer
#
#     def create(self, request, *args, **kwargs):
#
#         serializer = self.get_serializer(
#             data=request.data,
#             context={
#                 "request": request
#             }
#         )
#
#         serializer.is_valid(
#             raise_exception=True
#         )
#
#         contact = serializer.save()
#
#         return Response(
#             {
#                 "success": True,
#                 "message": "Contact created successfully",
#                 "data": ContactCreateSerializer(
#                     contact
#                 ).data
#             },
#             status=status.HTTP_201_CREATED
#         )

class ContactViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated]

    # lookup_field = "uuid"

    def get_queryset(self):

        # return Contact.objects.filter(
        #     is_deleted=False,
        #     created_by=self.request.user,
        # ).select_related(
        #     "city",
        #     "country_code",
        # ).prefetch_related(
        #     "festivals",
        #     "photos",
        # ).order_by("-created_at")
        queryset = Contact.objects.filter(
            is_deleted=False,
            created_by=self.request.user,
        ).select_related(
            "city",
            "country_code",
        ).prefetch_related(
            "festivals",
            "photos",
        ).order_by("-created_at")

        # =========================================
        # FILTER BY GIFT STATUS
        # =========================================

        gift_status = self.request.query_params.get(
            "gift_status"
        )

        if gift_status:
            queryset = queryset.filter(
                gift_status=gift_status
            )

        return queryset

    def get_serializer_class(self):

        if self.action in [
            "list",
            "retrieve",
        ]:
            return ContactListSerializer

        elif self.action in [
            "update",
            "partial_update",
        ]:
            return ContactUpdateSerializer

        return ContactCreateSerializer

    # =====================================================
    # CONTACT LIST API
    # =====================================================

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(
            self.get_queryset()
        )

        serializer = self.get_serializer(
            queryset,
            many=True,
            context={
                "request": request
            }
        )

        return Response(
            {
                "total_user": AppUser.objects.filter(
                    is_active=True,
                    is_deleted=False,
                ).count(),

                "total_contact": Contact.objects.filter(
                    is_active=True,
                    is_deleted=False,
                    created_by=request.user,
                ).count(),

                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):

        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        contact = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Contact updated successfully",
                "data": ContactCreateSerializer(
                    contact
                ).data
            },
            status=status.HTTP_200_OK
        )

    # =====================================================
    # CONTACT DELETE
    # =====================================================

    def destroy(self, request, *args, **kwargs):

        contact = self.get_object()

        contact.is_deleted = True
        contact.is_active = False
        contact.save()

        return Response(
            {
                "success": True,
                "message": "Contact deleted successfully",
            },
            status=status.HTTP_200_OK
        )

    # =====================================================
    # CONTACT STATUS UPDATE API
    # =====================================================

    @action(
        methods=["patch"],
        detail=True,
        url_path="update-status",
    )
    def update_status(self, request, pk=None):

        contact = self.get_object()

        serializer = ContactStatusUpdateSerializer(
            contact,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Gift status updated successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )

    # =====================================================
    # GIFT STATUS LIST API
    # =====================================================

    @action(
        methods=["get"],
        detail=False,
        url_path="gift-status-list",
    )
    def gift_status_list(self, request):

        data = [
            {
                "label": label,
                "value": value,
            }
            for value, label in GIFT_STATUS_CHOICES
        ]

        serializer = GiftStatusSerializer(
            data,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Gift status list fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )

# class UserViewSet(ReadOnlyModelViewSet):
#
#     serializer_class = UserListSerializer
#     permission_classes = [IsAuthenticated]
#
#
#     def get_queryset(self):
#
#         queryset = AppUser.objects.filter(
#             is_active=True,
#             is_deleted=False,
#         ).prefetch_related(
#             "groups",
#         ).order_by("-date_joined")
#
#         # Filter by role
#         role = self.request.query_params.get("role")
#
#         if role:
#             queryset = queryset.filter(
#                 groups__name__iexact=role
#             )
#
#         return queryset

class UserViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated]

    # lookup_field = "uuid"

    def get_queryset(self):

        queryset = AppUser.objects.filter(
            is_active=True,
            is_deleted=False,
        ).prefetch_related(
            "groups",
        ).order_by("-date_joined")

        role = self.request.query_params.get("role")

        if role:
            queryset = queryset.filter(
                groups__name__iexact=role
            )

        return queryset

    def get_serializer_class(self):

        if self.action in [
            "update",
            "partial_update",
        ]:
            return UserListSerializer

        return UserListSerializer

    # =====================================================
    # USER DELETE
    # =====================================================

    def destroy(self, request, *args, **kwargs):

        user = self.get_object()

        user.is_deleted = True
        user.is_active = False
        user.save()

        # delete token
        Token.objects.filter(
            user=user
        ).delete()

        return Response(
            {
                "success": True,
                "message": "User deleted successfully",
            },
            status=status.HTTP_200_OK
        )