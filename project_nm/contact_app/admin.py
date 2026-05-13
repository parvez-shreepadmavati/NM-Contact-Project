from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import AppUser,City,CountryCode,Festival,Contact,ContactPhoto


admin.site.site_header = "NM Contact Admin"
admin.site.index_title = "NM Contact Administration"


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = AppUser
        fields = (
            "email",
            "username",
            "emp_id",
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = AppUser
        fields = "__all__"

    def clean_password(self):
        password = self.initial.get("password")

        if password is None:
            return ""

        return password


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):

    model = AppUser

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    ordering = ("-date_joined",)

    list_display = (
        "id",
        "email",
        "emp_id",
        "full_name",
        "mobile_number",
        "get_groups",
        "is_staff",
        "is_active",
        # "is_email_verified",
        "date_joined",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
        "is_email_verified",
        "groups",
    )

    search_fields = (
        "email",
        "username",
        "emp_id",
        "uuid",
    )

    readonly_fields = (
        "uuid",
        "date_joined",
        "last_login",
        "last_modified",
        "last_user_activity",
    )

    fieldsets = (
        (
            "Login Credentials",
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),

        (
            "Personal Information",
            {
                "fields": (
                    "uuid",
                    "username",
                    "emp_id",
                    "full_name",
                    "mobile_number"
                )
            },
        ),

        (
            "Social Login",
            {
                "fields": (
                    "login_type",
                    "social_key",
                )
            },
        ),

        (
            "Verification",
            {
                "fields": (
                    "is_email_verified",
                )
            },
        ),

        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),

        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "last_modified",
                    "last_user_activity",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),

                "fields": (
                    "email",
                    "username",
                    "emp_id",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("groups")

    def get_groups(self, obj):
        return ", ".join(group.name for group in obj.groups.all())

    get_groups.short_description = "Groups"

@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "festival_date",
        "reminder_days_before",
        "is_public_holiday",
        "is_active",
    )

    list_filter = (
        "is_public_holiday",
        "is_active",
    )

    search_fields = (
        "name",
    )

    readonly_fields = (
        "uuid",
        "created_at",
        "updated_at",
    )


@admin.register(City)
class CityAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
    )


@admin.register(CountryCode)
class CountryCodeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "country_name",
        "country_code",
        "iso_code",
        "is_default",
        "is_active",
    )

    search_fields = (
        "country_name",
        "country_code",
        "iso_code",
    )


class ContactPhotoInline(admin.TabularInline):

    model = ContactPhoto

    extra = 1


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "full_name",
        "mobile_number",
        "email",
        "city",
        "country_code",
        "is_gift_reminder",
        "is_active",
        "created_by",
        "created_at",
    )

    list_filter = (
        "is_active",
        "is_deleted",
        "is_gift_reminder",
        "city",
        "festivals",
    )

    search_fields = (
        "full_name",
        "mobile_number",
        "email",
    )

    readonly_fields = (
        "uuid",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    filter_horizontal = (
        "festivals",
    )

    inlines = [
        ContactPhotoInline,
    ]

    def save_model(self, request, obj, form, change):

        if not obj.pk:
            obj.created_by = request.user

        obj.updated_by = request.user

        super().save_model(
            request,
            obj,
            form,
            change
        )