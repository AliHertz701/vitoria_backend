from rest_framework import serializers
from .models import *
import json
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = [
            'id',
            'user',
            'guest_id',
            'product',
            'quantity',
            'phone_number',
            'address',
            'city',
            'latitude',
            'longitude',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = images
        fields = ['id', 'image']


class ProductSerializer1(serializers.ModelSerializer):
    additional_images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)  # 👈 category name

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'quantity_available',
            'price',
            'discount_percentage',
            'show_price',
            'show_quantity',
            'place_orders',
            'image',
            'video',
            'category',
            'sku',
            'sizes',
            'material',
            'season',
            'gender',
            'brand',
            'color',
            'care_instructions',
            'is_featured',
            'is_new_arrival',
            'is_active',
            'additional_images',  # 👈 HERE
        ]
class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'image_url']

    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url  # just return the relative path
        return None


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'user', 'email', 'phone_number', 'subject', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class DashboardStatsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_categories = serializers.IntegerField()
    total_branches = serializers.IntegerField()
    low_stock_products = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    average_order_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    recent_orders_count = serializers.IntegerField()
    total_customers = serializers.IntegerField()

class TopProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', allow_null=True)
    sold_quantity = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'category', 'sold_quantity', 'revenue', 'quantity_available', 'image']
class OrderSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='id')
    customer_name = serializers.CharField(source='name')
    customer_phone = serializers.CharField(source='phone')
    total_amount = serializers.DecimalField(source='total', max_digits=12, decimal_places=2)

    status = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()

    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")

    class Meta:
        model = Invoice
        fields = [
            'id',
            'order_number',
            'customer_name',
            'customer_phone',
            'total_amount',
            'status',
            'payment_status',
            'items_count',
            'city',
            'address',
            'created_at',
        ]

    def get_status(self, obj):
        # يرجع النص العربي مباشرة
        return obj.get_status_display()

    def get_payment_status(self, obj):
        # بما إن النظام Guest وبدون Payments حقيقي
        if obj.status == Invoice.Status.COMPLETED:
            return 'مدفوع'
        return 'غير مدفوع'

    def get_items_count(self, obj):
        return obj.items.count() if hasattr(obj, 'items') else 0

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', allow_null=True)
    product_name = serializers.CharField(source='product.name', allow_null=True)
    unit_price = serializers.DecimalField(source='price', max_digits=10, decimal_places=2)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = InvoiceItem
        fields = [
            'id',
            'product_id',
            'product_name',
            'quantity',
            'unit_price',
            'total_price',
            'discount_percentage'
        ]

    def get_total_price(self, obj):
        return (obj.price or Decimal('0.00')) * (obj.quantity or 0)


class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = images
        fields = ['id', 'image', 'image_url']
        read_only_fields = ['id']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class CategorySerializer1(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'slug', 'is_active']
        read_only_fields = ['id', 'slug']

class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer1(read_only=True)
    main_image = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    additional_images = serializers.SerializerMethodField()  # <-- added

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category', 'price', 'discount_percentage',
            'discounted_price', 'quantity_available', 'is_active', 'is_featured',
            'is_new_arrival', 'brand', 'gender', 'main_image', 'additional_images', 'created_at'
        ]

    def get_main_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_discounted_price(self, obj):
        if obj.price and obj.discount_percentage:
            discount = obj.price * (obj.discount_percentage / 100)
            return round(obj.price - discount, 2)
        return obj.price

    def get_additional_images(self, obj):
        """
        Returns list of URLs for additional images
        """
        request = self.context.get('request')
        images_qs = obj.additional_images.all()  # related_name from images model
        urls = []
        for img in images_qs:
            if img.image and hasattr(img.image, 'url'):
                if request:
                    urls.append(request.build_absolute_uri(img.image.url))
                else:
                    urls.append(img.image.url)
        return urls

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer1(read_only=True)
    additional_images = ImageSerializer(many=True, read_only=True)
    main_image_url = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def get_main_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_discounted_price(self, obj):
        if obj.price and obj.discount_percentage:
            discount = obj.price * (obj.discount_percentage / 100)
            return round(obj.price - discount, 2)
        return obj.price
    
    def get_sizes(self, obj):
        if isinstance(obj.sizes, str):
            try:
                return json.loads(obj.sizes)
            except:
                return []
        return obj.sizes or []
    
    def get_color(self, obj):
        if isinstance(obj.color, str):
            try:
                return json.loads(obj.color)
            except:
                return []
        return obj.color or []

class ProductCreateSerializer(serializers.ModelSerializer):
    # Remove the custom validation for sizes and color - let Django handle them
    class Meta:
        model = Product
        fields = '__all__'
    
    def to_internal_value(self, data):
        """Convert incoming FormData for validation"""
        # First get the internal value from parent
        validated_data = super().to_internal_value(data)
        
        # Handle sizes field
        if 'sizes' in data:
            sizes_value = data['sizes']
            
            # If it's already a list, keep it
            if isinstance(sizes_value, list):
                validated_data['sizes'] = sizes_value
            # If it's a string, try to parse it
            elif isinstance(sizes_value, str):
                sizes_value = sizes_value.strip()
                if not sizes_value or sizes_value == '[]':
                    validated_data['sizes'] = []
                elif sizes_value.startswith('[') and sizes_value.endswith(']'):
                    # It's a JSON string
                    try:
                        validated_data['sizes'] = json.loads(sizes_value)
                    except json.JSONDecodeError:
                        # Fallback to comma-separated
                        cleaned = sizes_value.strip('[]').replace('"', '').replace("'", "")
                        items = [item.strip() for item in cleaned.split(',') if item.strip()]
                        validated_data['sizes'] = items
                else:
                    # Comma-separated string
                    items = [item.strip() for item in sizes_value.split(',') if item.strip()]
                    validated_data['sizes'] = items
        
        # Handle color field similarly
        if 'color' in data:
            color_value = data['color']
            
            if isinstance(color_value, list):
                validated_data['color'] = color_value
            elif isinstance(color_value, str):
                color_value = color_value.strip()
                if not color_value or color_value == '[]':
                    validated_data['color'] = []
                elif color_value.startswith('[') and color_value.endswith(']'):
                    try:
                        validated_data['color'] = json.loads(color_value)
                    except json.JSONDecodeError:
                        cleaned = color_value.strip('[]').replace('"', '').replace("'", "")
                        items = [item.strip() for item in cleaned.split(',') if item.strip()]
                        validated_data['color'] = items
                else:
                    items = [item.strip() for item in color_value.split(',') if item.strip()]
                    validated_data['color'] = items
        
        return validated_data
    
    def to_representation(self, instance):
        """Convert database representation for output"""
        representation = super().to_representation(instance)
        
        # Parse sizes from JSON string if needed
        if isinstance(representation.get('sizes'), str):
            try:
                representation['sizes'] = json.loads(representation['sizes'])
            except json.JSONDecodeError:
                representation['sizes'] = []
        
        # Parse color from JSON string if needed
        if isinstance(representation.get('color'), str):
            try:
                representation['color'] = json.loads(representation['color'])
            except json.JSONDecodeError:
                representation['color'] = []
        
        return representation
    
    def create(self, validated_data):
        """Convert lists to JSON strings before saving to database"""
        # Convert sizes list to JSON string
        if 'sizes' in validated_data:
            if isinstance(validated_data['sizes'], list):
                validated_data['sizes'] = json.dumps(validated_data['sizes'])
            elif validated_data['sizes'] is None:
                validated_data['sizes'] = '[]'
        
        # Convert color list to JSON string
        if 'color' in validated_data:
            if isinstance(validated_data['color'], list):
                validated_data['color'] = json.dumps(validated_data['color'])
            elif validated_data['color'] is None:
                validated_data['color'] = '[]'
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Convert lists to JSON strings before updating database"""
        # Convert sizes list to JSON string
        if 'sizes' in validated_data:
            if isinstance(validated_data['sizes'], list):
                validated_data['sizes'] = json.dumps(validated_data['sizes'])
            elif validated_data['sizes'] is None:
                validated_data['sizes'] = '[]'
        
        # Convert color list to JSON string
        if 'color' in validated_data:
            if isinstance(validated_data['color'], list):
                validated_data['color'] = json.dumps(validated_data['color'])
            elif validated_data['color'] is None:
                validated_data['color'] = '[]'
        
        return super().update(instance, validated_data)




class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'product', 'name', 'quantity','color','size', 'price', 'discount_percentage', 'original_price']


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'name', 'status', 'total', 'subtotal', 'delivery_fee', 'discount_amount', 'created_at']


class InvoiceDetailSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'name', 'status', 'total', 'subtotal', 'delivery_fee',
            'discount_amount', 'created_at', 'city', 'address', 'phone', 'items' 
        ]


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'



class WAInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WAInfo
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']