from django.contrib import admin
from .models import Product, Inquiry, Branch, Message

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity_available', 'price', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'address', 'created_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('created_at',)

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'latitude', 'longitude')
    search_fields = ('name',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)