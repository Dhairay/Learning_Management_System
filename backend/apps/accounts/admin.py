from django.contrib import admin
from .models import User, Organization, OrganizationMembership, Invitation, Role

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'created_at')
    search_fields = ('name', 'display_name')
    ordering = ('name',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('role', 'is_staff', 'is_active', 'created_at')
    ordering = ('-created_at',)

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'status', 'created_at')
    search_fields = ('name', 'slug')
    list_filter = ('status',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'status', 'joined_at')
    list_filter = ('role', 'status', 'organization')
    search_fields = ('user__email', 'organization__name')

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'organization', 'role', 'status', 'invited_by', 'created_at')
    list_filter = ('role', 'status', 'organization')
    search_fields = ('email', 'organization__name')
