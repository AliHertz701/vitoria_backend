from django.contrib import admin
from .models import (
    User,
    Product,
    Branch,
    Inquiry,
    ContactMessage,
    Category,
    Invoice,
    InvoiceItem,
    Banner,
    images,
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_admin', 'is_guest', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {"slug": ("name",)}  # admin will auto-fill slug

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discounted_price', 'is_active', 'is_featured']
    search_fields = ['name', 'sku', 'material', 'brand']
    list_filter = ['category', 'is_active', 'is_featured', 'is_new_arrival', 'gender']
    readonly_fields = ['discounted_price']  # computed property

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'primery_branch']
    search_fields = ['name', 'phone_number']

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'guest_id', 'quantity', 'status', 'city']
    search_fields = ['product__name', 'user__username', 'guest_id', 'city']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'created_at']
    search_fields = ['user__username', 'email']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'city', 'subtotal', 'total', 'created_at']
    search_fields = ['name', 'city']

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'name', 'quantity', 'price', 'subtotal']
    search_fields = ['name']

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active']
    list_editable = ['order', 'is_active']

@admin.register(images)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']
