from django.contrib import admin
from .models import Enrollment, Entitlement, Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student_membership', 'course', 'status', 'enrolled_at')
    list_filter = ('status', 'organization')
    search_fields = ('student_membership__user__email', 'course__title')
    ordering = ('-enrolled_at',)

@admin.register(Entitlement)
class EntitlementAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'source_type', 'status', 'starts_at', 'expires_at')
    list_filter = ('source_type', 'status')
    search_fields = ('user__email', 'course__title')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer_user', 'organization', 'total_minor', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency', 'organization')
    search_fields = ('buyer_user__email', 'id')
    inlines = [OrderItemInline, PaymentInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount_minor', 'currency', 'provider', 'status', 'created_at')
    list_filter = ('status', 'provider', 'currency')
