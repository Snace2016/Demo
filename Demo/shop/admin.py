from django.contrib import admin

from .models import (
    AppUser, Category, Manufacturer, Order, OrderItem, OrderStatus,
    PickupPoint, Product, Supplier,
)


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'login', 'role')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('article', 'name', 'price', 'quantity', 'discount')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'status', 'order_date', 'delivery_date', 'client')


admin.site.register(Category)
admin.site.register(Manufacturer)
admin.site.register(Supplier)
admin.site.register(PickupPoint)
admin.site.register(OrderStatus)
admin.site.register(OrderItem)
