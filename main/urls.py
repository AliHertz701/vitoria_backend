from django.urls import path
from . import views
from . import api_views
from . import admin_api
from .api_views import create_product, product_list_api,create_branch ,create_inquiry ,branch_list_api
from rest_framework_simplejwt.views import TokenVerifyView ,TokenRefreshView

urlpatterns = [
    # path('', views.home, name='home'),
    # path('about/', views.about, name='about'),
    # path('shop/', views.shop, name='shop'),
    # path('cart/', views.view_cart, name='view_cart'),
    # path('products/', views.products, name='products'),
    # path('contact/', views.contact, name='contact'),
    # path('clients/', views.clients, name='clients'),
    # path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
    # path('dashboard/', views.dashboard, name='dashboard'),
    # path('api/branches/', branch_list_api, name='branch-list-api'),
    # path('api/create-product/', create_product, name='create_product'),
    # path('api/create-branch/', create_branch, name='create_branch'),
    # path('api/create-inquiry/', create_inquiry, name='create_inquiry'),
    path('api/products/', product_list_api, name='api_products'),
    # path("products/api/<int:pk>/", api_views.product_detail_api, name="product_detail_api"),
    # path("products/api/<int:pk>/delete/", api_views.product_delete_api, name="product_delete_api"),
    # path("branches/api/<int:pk>/", api_views.branch_detail_api, name="branch_detail_api"),
    # path("branches/api/<int:pk>/delete/", api_views.branch_delete_api, name="branch_delete_api"),
    # path("branches/api/get-primary/", api_views.get_primary_branch, name="get_primary_branch"),
    # path('api/products/', views.get_products_api, name='products_api'),
    # path('add/cat', api_views.category_add, name='category_add'),
    # path('api/category/<int:category_id>/update/', api_views.category_update, name='category_update'),
    # path('api/category/<int:category_id>/delete/', api_views.category_delete, name='category_delete'),
    # path('api/category/<int:category_id>/', api_views.category_detail, name='category_detail'),
    path('api/categories/', api_views.api_categories, name='api-categories'),
    # path('api/products/cat', api_views.api_products_by_category, name='api-products-by-category'),
    path('api/home-data/', api_views.home_data, name='api-home-data'),
    # path('api/search/', api_views.search_products, name='api-search-products'),
    # path('api/categories/', api_views.get_categories, name='api-get-categories'),
    # path('api/product/<int:product_id>/', api_views.get_product_detail, name='api-product-detail'),
    # path('api/quick-view/', api_views.quick_view, name='api-quick-view'),
    # path('api/shop-page-data/', api_views.shop_page_data, name='shop_page_data'),
    # path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    # path('api/get-product/<int:product_id>/', views.get_product_api, name='get-product-api'),
    path('api/invoices/create/', api_views.create_invoice, name='create_invoice'),
    # path("banners/api/<int:pk>/", api_views.banner_detail_api, name="banner_detail_api"),
    # path("banners/api/<int:pk>/delete/", api_views.banner_delete_api, name="banner_delete_api"),
    # path("api/banner/create/", api_views.banner_create_api, name="banner_add"),
    # path('invoices/delete/<int:invoice_id>/', api_views.delete_invoice, name='delete_invoice'),
    # path('api/products/<int:product_id>/', api_views.product_detail_smart, name='product-detail-smart'),
    # path('api/contact/message/', api_views.contact_message_create_api, name='contact-message-create'),

    # Cities (new)
    path("cities/api/<int:pk>/", api_views.city_detail_api, name="city_detail_api"),
    path("cities/api/<int:pk>/delete/", api_views.city_delete_api, name="city_delete_api"),
    path("cities/create/", api_views.create_city, name="create_city"),
    path("api/cities/", api_views.city_list_api, name="city_list_api"),


   # -----------------------
    # Authentication
    # -----------------------
    path('api/admin/login/', admin_api.admin_login, name='admin-login'),

    # -----------------------
    # Dashboard
    # -----------------------
    path('dashboard-stats/', admin_api.dashboard_stats, name='dashboard-stats'),

    # -----------------------
    # Products
    # -----------------------
    path('products/', admin_api.products, name='products'),
    path('products/<int:pk>/', admin_api.product_detail, name='product-detail'),

    # -----------------------
    # Categories
    # -----------------------
    path('categories/', admin_api.categories, name='categories'),
    path('categories/<int:pk>/', admin_api.category_detail, name='category-detail'),

    # -----------------------
    # Branches
    # -----------------------
    path('branches/', admin_api.branches, name='branches'),
    path('branches/<int:pk>/', admin_api.branch_detail, name='branch-detail'),

    # -----------------------
    # Banners
    # -----------------------
    path('banners/', admin_api.banners, name='banners'),
    path('banners/<int:pk>/', admin_api.banner_detail, name='banner-detail'),

    # -----------------------
    # Invoices
    # -----------------------
    path('invoices/', admin_api.invoices, name='invoices'),
    path('invoices/<int:pk>/items/', admin_api.invoice_items, name='invoice-items'),
    path('invoices/stats/', admin_api.invoice_stats, name='invoice-stats'),

    # -----------------------
    # Contact Messages
    # -----------------------
    path('contact-messages/', admin_api.contact_messages, name='contact-messages'),

    # -----------------------
    # File Upload
    # -----------------------
    path('upload-file/', admin_api.upload_file, name='upload-file'),

    path('api/admin/dashboard/stats/', admin_api.admin_dashboard_stats, name='admin_dashboard_stats'),
    path('api/admin/orders/', admin_api.admin_orders_list, name='admin_orders_list'),
    path('api/admin/orders/<int:order_id>/', admin_api.admin_order_detail, name='admin_order_detail'),
    path('api/admin/products/top/', admin_api.admin_top_products, name='admin_top_products'),
    path('api/admin/quick-actions/<str:action>/', admin_api.admin_quick_actions, name='admin_quick_actions'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user/profile/', admin_api.UserProfileView.as_view(), name='user-profile'),
    #prodcut management
    path('api/admin/products/', admin_api.product_list, name='product-list'),
    path('api/admin/products/stats/', admin_api.product_stats, name='product-stats'),
    path('api/admin/products/create/', admin_api.product_create, name='product-create'),
    path('api/admin/products/<int:pk>/', admin_api.product_detail, name='product-detail'),
    path('api/admin/products/<int:pk>/update/', admin_api.product_update, name='product-update'),
    path('api/admin/products/<int:pk>/delete/', admin_api.product_delete, name='product-delete'),

    path('api/admin/products/<int:pk>/toggle-active/', admin_api.product_toggle_active, name='product-toggle-active'),
    path('api/admin/products/<int:pk>/toggle-featured/', admin_api.product_toggle_featured, name='product-toggle-featured'),
    path('api/admin/products/<int:pk>/update-stock/', admin_api.product_update_stock, name='product-update-stock'),
    path('api/admin/products/<int:pk>/upload-images/', admin_api.product_upload_images, name='product-upload-images'),
    path('api/admin/products/<int:pk>/delete-image/<int:image_id>/', admin_api.product_delete_image, name='product-delete-image'),

    path('api/admin/products/categories/', admin_api.category_list, name='category-list'),
#invoice management
    path('api/admin/invoices/', admin_api.invoice_list),
    path('api/admin/invoices/<int:invoice_id>/', admin_api.invoice_detail),
    path('api/admin/invoices/<int:invoice_id>/delete/', admin_api.invoice_delete),
    #banner management
    path('api/admin/banners/', admin_api.banners_api, name='banners-list'),
    #category management
    path('api/admin/categories/', admin_api.categories_api, name='admin-categories'),
    #analytics
    path('api/admin/analytics/', admin_api.admin_analytics, name='admin-analytics'),
    path('api/admin/wa-info/create/', admin_api.create_wa_info, name='create-wa-info'),
    path('api/admin/wa-info/<int:id>/update/', admin_api.update_wa_info, name='update-wa-info'),
    path('api/admin/cities/', admin_api.cities_list, name='cities-list'),
    path('api/admin/cities/<int:pk>/', admin_api.city_detail, name='city-detail'),
    # Branch CRUD
    path('api/admin/branches/', admin_api.create_branch, name='create-branch'),
    path('api/admin/branches/<int:id>/update/', admin_api.update_branch, name='update-branch'),
    path('api/admin/branches/<int:id>/delete/', admin_api.delete_branch, name='delete-branch'),

    # Contact Message
    path('api/admin/messages/<int:id>/read/', admin_api.mark_message_read, name='mark-message-read'),

]
