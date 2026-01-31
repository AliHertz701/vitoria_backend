from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny ,IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from django.db.models import Sum, Count, Avg, Q, F,Value
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal ,ROUND_HALF_UP
import json
import uuid
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.db.models.functions import Coalesce
from .models import *
from .serializers import *
from django.db.models import DecimalField 
from django.core.paginator import Paginator
from .utils import parse_json_field, parse_bool
from datetime import datetime
from django.db.models.functions import TruncMonth

# -----------------------
# Authentication API
# -----------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user and user.is_admin:
        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    return Response({
        'success': False,
        'error': 'Invalid credentials or not an admin'
    }, status=401)


# -----------------------
# Dashboard Stats
# -----------------------
@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    total_products = Product.objects.count()
    total_orders = Invoice.objects.count()
    total_categories = Category.objects.count()
    total_branches = Branch.objects.count()
    
    week_ago = timezone.now() - timedelta(days=7)
    recent_orders = Invoice.objects.filter(created_at__gte=week_ago).count()
    
    total_revenue = Invoice.objects.aggregate(total=Sum('total'))['total'] or 0
    
    today = timezone.now().date()
    today_orders = Invoice.objects.filter(created_at__date=today).count()
    
    low_stock_products = Product.objects.filter(quantity_available__lt=10).count()
    
    return Response({
        'success': True,
        'stats': {
            'total_products': total_products,
            'total_orders': total_orders,
            'total_categories': total_categories,
            'total_branches': total_branches,
            'recent_orders': recent_orders,
            'total_revenue': float(total_revenue),
            'today_orders': today_orders,
            'low_stock_products': low_stock_products
        }
    })


# -----------------------
# Product APIs
# -----------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def products(request):
    if request.method == 'GET':
        queryset = Product.objects.all().order_by('-id')
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(brand__icontains=search)
            )
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        status_filter = request.query_params.get('status')
        if status_filter == 'low_stock':
            queryset = queryset.filter(quantity_available__lt=10)
        elif status_filter == 'featured':
            queryset = queryset.filter(is_featured=True)
        elif status_filter == 'new':
            queryset = queryset.filter(is_new_arrival=True)
        serializer = ProductSerializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data})
    
    # POST - create
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        # Handle sizes/colors
        if 'sizes' in request.data:
            try:
                sizes = json.loads(request.data['sizes']) if isinstance(request.data['sizes'], str) else request.data['sizes']
                serializer.validated_data['sizes'] = sizes
            except json.JSONDecodeError:
                pass
        if 'color' in request.data:
            try:
                colors = json.loads(request.data['color']) if isinstance(request.data['color'], str) else request.data['color']
                serializer.validated_data['color'] = colors
            except json.JSONDecodeError:
                pass
        serializer.save()
        return Response({'success': True, 'message': 'Product created', 'data': serializer.data}, status=201)
    
    return Response({'success': False, 'errors': serializer.errors}, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'success': False, 'error': 'Product not found'}, status=404)
    
    if request.method == 'GET':
        serializer = ProductSerializer1(product)
        return Response({'success': True, 'data': serializer.data})
    
    if request.method == 'PUT':
        serializer = ProductSerializer1(product, data=request.data, partial=True)
        if serializer.is_valid():
            if 'sizes' in request.data:
                try:
                    sizes = json.loads(request.data['sizes']) if isinstance(request.data['sizes'], str) else request.data['sizes']
                    serializer.validated_data['sizes'] = sizes
                except json.JSONDecodeError:
                    pass
            if 'color' in request.data:
                try:
                    colors = json.loads(request.data['color']) if isinstance(request.data['color'], str) else request.data['color']
                    serializer.validated_data['color'] = colors
                except json.JSONDecodeError:
                    pass
            serializer.save()
            return Response({'success': True, 'message': 'Product updated', 'data': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=400)
    
    if request.method == 'DELETE':
        product.delete()
        return Response({'success': True, 'message': 'Product deleted'})


# -----------------------
# Category APIs
# -----------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def categories(request):
    if request.method == 'GET':
        queryset = Category.objects.all().order_by('name')
        serializer = CategorySerializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data})
    
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': 'Category created', 'data': serializer.data}, status=201)
    return Response({'success': False, 'errors': serializer.errors}, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def category_detail(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({'success': False, 'error': 'Category not found'}, status=404)
    
    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response({'success': True, 'data': serializer.data})
    
    if request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Category updated', 'data': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=400)
    
    if request.method == 'DELETE':
        category.delete()
        return Response({'success': True, 'message': 'Category deleted'})


# -----------------------
# Branch APIs
# -----------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def branches(request):
    if request.method == 'GET':
        queryset = Branch.objects.all().order_by('-primery_branch', 'name')
        serializer = BranchSerializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data})
    
    serializer = BranchSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': 'Branch created', 'data': serializer.data}, status=201)
    return Response({'success': False, 'errors': serializer.errors}, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def branch_detail(request, pk):
    try:
        branch = Branch.objects.get(pk=pk)
    except Branch.DoesNotExist:
        return Response({'success': False, 'error': 'Branch not found'}, status=404)
    
    if request.method == 'GET':
        serializer = BranchSerializer(branch)
        return Response({'success': True, 'data': serializer.data})
    
    if request.method == 'PUT':
        serializer = BranchSerializer(branch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Branch updated', 'data': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=400)
    
    if request.method == 'DELETE':
        branch.delete()
        return Response({'success': True, 'message': 'Branch deleted'})


# -----------------------
# Banner APIs
# -----------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def banners(request):
    if request.method == 'GET':
        queryset = Banner.objects.all().order_by('order')
        serializer = BannerSerializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data})
    
    serializer = BannerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': 'Banner created', 'data': serializer.data}, status=201)
    return Response({'success': False, 'errors': serializer.errors}, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def banner_detail(request, pk):
    try:
        banner = Banner.objects.get(pk=pk)
    except Banner.DoesNotExist:
        return Response({'success': False, 'error': 'Banner not found'}, status=404)
    
    if request.method == 'GET':
        serializer = BannerSerializer(banner)
        return Response({'success': True, 'data': serializer.data})
    
    if request.method == 'PUT':
        serializer = BannerSerializer(banner, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Banner updated', 'data': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=400)
    
    if request.method == 'DELETE':
        banner.delete()
        return Response({'success': True, 'message': 'Banner deleted'})


# -----------------------
# Invoice APIs
# -----------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def invoices(request):
    if request.method == 'GET':
        queryset = Invoice.objects.all().order_by('-created_at')
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(phone__icontains=search) |
                Q(id__icontains=search)
            )
        status_filter = request.query_params.get('status')
        if status_filter == 'today':
            today = timezone.now().date()
            queryset = queryset.filter(created_at__date=today)
        elif status_filter == 'week':
            week_ago = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(created_at__gte=week_ago)
        serializer = InvoiceSerializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data})
    
    serializer = InvoiceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': 'Invoice created', 'data': serializer.data}, status=201)
    return Response({'success': False, 'errors': serializer.errors}, status=400)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def invoice_items(request, pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        return Response({'success': False, 'error': 'Invoice not found'}, status=404)
    
    items = invoice.items.all()
    serializer = InvoiceItemSerializer(items, many=True)
    return Response({'success': True, 'items': serializer.data})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def invoice_stats(request):
    current_month = timezone.now().month
    monthly_revenue = Invoice.objects.filter(
        created_at__month=current_month
    ).aggregate(total=Sum('total'))['total'] or 0

    orders_by_city = Invoice.objects.values('city').annotate(
        count=Count('id'),
        revenue=Sum('total')
    ).order_by('-count')

    top_products = InvoiceItem.objects.values('product_id', 'name').annotate(
        total_sold=Sum('quantity'),
        revenue=Sum('price')
    ).order_by('-total_sold')[:10]

    return Response({
        'success': True,
        'monthly_revenue': float(monthly_revenue),
        'orders_by_city': list(orders_by_city),
        'top_products': list(top_products)
    })


# -----------------------
# Contact Messages
# -----------------------
@api_view(['GET'])
@permission_classes([IsAdminUser])
def contact_messages(request):
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer = ContactMessageSerializer(queryset, many=True)
    return Response({'success': True, 'data': serializer.data})


# -----------------------
# File Upload
# -----------------------
@api_view(['POST'])
@permission_classes([IsAdminUser])
def upload_file(request):
    file_type = request.data.get('type', 'product')
    file = request.FILES.get('file')
    
    if not file:
        return Response({'success': False, 'error': 'No file provided'}, status=400)
    
    filename = f"{uuid.uuid4()}_{file.name}"
    
    if file_type == 'product':
        path = f'products/{filename}'
    elif file_type == 'banner':
        path = f'banners/{filename}'
    elif file_type == 'category':
        path = f'categories/{filename}'
    else:
        path = f'uploads/{filename}'
    
    return Response({'success': True, 'url': f'/media/{path}', 'filename': filename})

from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard_stats(request):
    """
    Get dashboard statistics for admin panel
    """
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    try:
        # -------- Products, Categories, Branches --------
        total_products = Product.objects.filter(is_active=True).count()
        total_categories = Category.objects.count()
        total_branches = Branch.objects.count()
        low_stock_products = Product.objects.filter(
            quantity_available__lt=10,
            quantity_available__gt=0,
            is_active=True
        ).count()

        # -------- Orders --------
        completed_invoices = Invoice.objects.filter(status=Invoice.Status.COMPLETED)
        total_orders = completed_invoices.count()  # total completed orders
        recent_orders = completed_invoices.filter(created_at__date__gte=thirty_days_ago)
        recent_orders_count = recent_orders.count()

        # -------- Revenue & Average --------
        total_revenue = completed_invoices.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        total_revenue = total_revenue.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        avg_order_value = recent_orders.aggregate(avg=Avg('total'))['avg'] or Decimal('0.00')
        avg_order_value = avg_order_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # -------- Orders by status --------
        pending_orders = Invoice.objects.filter(status=Invoice.Status.PENDING).count()
        completed_orders = total_orders  # already counted above

        # -------- Total customers (distinct phone numbers) --------
        total_customers = completed_invoices.exclude(
            phone__isnull=True
        ).exclude(
            phone__exact=''
        ).values('phone').distinct().count()

        # -------- Prepare stats dict --------
        stats = {
            'total_orders': total_orders,
            'total_products': total_products,
            'total_revenue': total_revenue,
            'total_categories': total_categories,
            'total_branches': total_branches,
            'low_stock_products': low_stock_products,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'average_order_value': avg_order_value,
            'recent_orders_count': recent_orders_count,
            'total_customers': total_customers,
        }

        serializer = DashboardStatsSerializer(data=stats)
        serializer.is_valid(raise_exception=True)

        return Response({
            'success': True,
            'data': serializer.validated_data
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_orders_list(request):
    """
    Get list of orders with filtering and pagination
    """
    try:
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        status_filter = request.GET.get('status')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        queryset = Invoice.objects.all().order_by('-created_at')

        # ✅ Filter by invoice status
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Date filters
        if start_date:
            try:
                queryset = queryset.filter(
                    created_at__date__gte=datetime.strptime(start_date, '%Y-%m-%d')
                )
            except ValueError:
                pass

        if end_date:
            try:
                queryset = queryset.filter(
                    created_at__date__lte=datetime.strptime(end_date, '%Y-%m-%d')
                )
            except ValueError:
                pass

        total_count = queryset.count()
        orders = queryset[offset: offset + limit]

        serializer = OrderSerializer(orders, many=True)

        return Response({
            'success': True,
            'results': serializer.data,
            'count': total_count,
            'next': None if offset + limit >= total_count else f"?offset={offset + limit}&limit={limit}",
            'previous': None if offset == 0 else f"?offset={max(0, offset - limit)}&limit={limit}"
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_order_detail(request, order_id):
    """
    Get detailed information for a specific order
    """
    try:
        order = Invoice.objects.get(id=order_id)

        items = order.items.all()

        return Response({
            'success': True,
            'order': OrderSerializer(order).data,
            'items': OrderItemSerializer(items, many=True).data
        })

    except Invoice.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_top_products(request):
    """
    Get top selling products based on completed orders
    """
    try:
        # -------- Query parameters --------
        limit = int(request.GET.get('limit', 10))
        period = request.GET.get('period', 'month')  # day, week, month, year

        today = timezone.now().date()

        # -------- Determine start date --------
        if period == 'day':
            start_date = today
        elif period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'year':
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=30)

        # -------- Annotate products with sales data --------
        products = Product.objects.filter(
            is_active=True
        ).annotate(
            sold_quantity=Coalesce(
                Sum(
                    'invoice_items__quantity',
                    filter=Q(
                        invoice_items__invoice__status=Invoice.Status.COMPLETED,
                        invoice_items__invoice__created_at__date__gte=start_date
                    )
                ),
                0
            ),
            revenue=Coalesce(
                Sum(
                    F('invoice_items__price') * F('invoice_items__quantity'),
                    output_field=DecimalField(max_digits=20, decimal_places=2),
                    filter=Q(
                        invoice_items__invoice__status=Invoice.Status.COMPLETED,
                        invoice_items__invoice__created_at__date__gte=start_date
                    )
                ),
                Decimal('0.00')
            )
        ).filter(
            sold_quantity__gt=0
        ).order_by('-sold_quantity')[:limit]

        # -------- Prepare response data --------
        results = []
        for product in products:
            results.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku or '',
                'category': product.category.name if product.category else 'غير مصنف',
                'sold_quantity': int(product.sold_quantity),
                'revenue': float(product.revenue),
                'stock_quantity': product.quantity_available,
                'image': request.build_absolute_uri(product.image.url) if product.image else None,
            })

        return Response({
            'success': True,
            'results': results,
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': today.isoformat()
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_quick_actions(request, action):
    """
    Handle quick actions from dashboard
    """
    try:
        if request.method == 'GET':
            # Handle different quick actions
            if action == 'add_product':
                return Response({
                    'success': True,
                    'message': 'Redirecting to add product page',
                    'redirect_url': '/admin/products/new'
                })
            elif action == 'create_banner':
                return Response({
                    'success': True,
                    'message': 'Redirecting to create banner page',
                    'redirect_url': '/admin/banners/new'
                })
            elif action == 'view_reports':
                return Response({
                    'success': True,
                    'message': 'Redirecting to analytics page',
                    'redirect_url': '/admin/analytics'
                })
            elif action == 'manage_users':
                return Response({
                    'success': True,
                    'message': 'Redirecting to users page',
                    'redirect_url': '/admin/users'
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Unknown action'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        elif request.method == 'POST':
            # Handle POST actions
            data = request.data
            
            if action == 'update_order_status':
                order_id = data.get('order_id')
                new_status = data.get('status')
                
                try:
                    # Update invoice status if you have a status field
                    # For now, we'll update Inquiry status
                    inquiry = Inquiry.objects.get(id=order_id)
                    inquiry.status = new_status
                    inquiry.save()
                    
                    return Response({
                        'success': True,
                        'message': f'Order status updated to {new_status}'
                    })
                except Inquiry.DoesNotExist:
                    return Response({
                        'success': False,
                        'error': 'Order not found'
                    }, status=status.HTTP_404_NOT_FOUND)
                    
            else:
                return Response({
                    'success': False,
                    'error': 'Unknown action'
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def product_list(request):
    """
    Get list of products with filtering, sorting, and pagination.
    """
    try:
        # --- Query parameters ---
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        search = request.GET.get('search', '').strip()
        status_filter = request.GET.get('status', None)
        category_id = request.GET.get('category', None)
        featured = request.GET.get('featured', None)
        new_arrival = request.GET.get('new_arrival', None)
        sort_by = request.GET.get('sort_by', '-created_at')

        # --- Base queryset ---
        products = Product.objects.all().select_related('category')

        # --- Apply search filter ---
        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(sku__icontains=search) |
                Q(brand__icontains=search)
            )

        # --- Status filter ---
        if status_filter == 'active':
            products = products.filter(is_active=True)
        elif status_filter == 'inactive':
            products = products.filter(is_active=False)
        elif status_filter == 'low_stock':
            products = products.filter(quantity_available__lte=10, quantity_available__gt=0)
        elif status_filter == 'out_of_stock':
            products = products.filter(quantity_available=0)

        # --- Category filter ---
        if category_id:
            products = products.filter(category_id=category_id)

        # --- Featured & New Arrival ---
        if featured == 'true':
            products = products.filter(is_featured=True)
        if new_arrival == 'true':
            products = products.filter(is_new_arrival=True)

        # --- Sorting safely ---
        allowed_sort_fields = ['name', 'price', 'quantity_available', 'created_at']
        if sort_by.lstrip('-') in allowed_sort_fields:
            products = products.order_by(sort_by)
        else:
            products = products.order_by('-created_at')

        # --- Pagination ---
        paginator = Paginator(products, limit)
        page_obj = paginator.get_page(page)

        # --- Serialization ---
        serializer = ProductListSerializer(page_obj, many=True, context={'request': request})

        # --- Response ---
        return Response({
            'success': True,
            'products': serializer.data,
            'pagination': {
                'total': paginator.count,
                'pages': paginator.num_pages,
                'current_page': page_obj.number,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def product_detail(request, pk):
    """
    Get single product details
    """
    try:
        product = Product.objects.select_related('category').prefetch_related('additional_images').get(pk=pk)
        serializer = ProductDetailSerializer(product, context={'request': request})
        return Response({
            'success': True,
            'product': serializer.data
        })
    except Product.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def product_create(request):
    data = request.data
    files = request.FILES

    try:
        category = None
        if data.get('category'):
            category = Category.objects.get(id=data.get('category'))

        product = Product.objects.create(
            name=data.get('name', '').strip(),
            description=data.get('description', ''),
            quantity_available=int(data.get('quantity_available', 0)),
            price=Decimal(data.get('price')) if data.get('price') else None,
            discount_percentage=Decimal(data.get('discount_percentage', 0)),
            sku=data.get('sku', ''),
            sizes=parse_json_field(data.get('sizes')),
            material=data.get('material', ''),
            season=data.get('season', ''),
            gender=data.get('gender', 'unisex'),
            brand=data.get('brand', ''),
            color=parse_json_field(data.get('color')),
            care_instructions=data.get('care_instructions', ''),
            show_quantity=parse_bool(data.get('show_quantity'), True),
            show_price=parse_bool(data.get('show_price'), True),
            place_orders=parse_bool(data.get('place_orders'), True),
            is_featured=parse_bool(data.get('is_featured')),
            is_new_arrival=parse_bool(data.get('is_new_arrival')),
            is_active=parse_bool(data.get('is_active'), True),
            category=category,
            image=files.get('image'),
            video=files.get('video'),
            buy_price=Decimal(data.get('buy_price')) if data.get('buy_price') else None,
            source=data.get('source', ''),
        )

        # Handle additional images (if you have a related model)
        for img in files.getlist('additional_images'):
            product.additional_images.create(image=img)

        return Response({
            "success": True,
            "product_id": product.id
        }, status=status.HTTP_201_CREATED)

    except Category.DoesNotExist:
        return Response({
            "success": False,
            "error": "Invalid category"
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def product_update(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({
            "success": False,
            "error": "Product not found"
        }, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    files = request.FILES

    try:
        if data.get('category'):
            product.category = Category.objects.get(id=data.get('category'))

        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.quantity_available = int(data.get('quantity_available', product.quantity_available))
        product.price = Decimal(data.get('price')) if data.get('price') else product.price
        product.discount_percentage = Decimal(data.get('discount_percentage', product.discount_percentage))
        product.sku = data.get('sku', product.sku)
        product.sizes = parse_json_field(data.get('sizes'), product.sizes)
        product.material = data.get('material', product.material)
        product.season = data.get('season', product.season)
        product.gender = data.get('gender', product.gender)
        product.brand = data.get('brand', product.brand)
        product.color = parse_json_field(data.get('color'), product.color)
        product.care_instructions = data.get('care_instructions', product.care_instructions)
        product.buy_price = Decimal(data.get('buy_price', product.buy_price)) if data.get('buy_price') else product.buy_price
        product.source = data.get('source', product.source)
        product.show_quantity = parse_bool(data.get('show_quantity'), product.show_quantity)
        product.show_price = parse_bool(data.get('show_price'), product.show_price)
        product.place_orders = parse_bool(data.get('place_orders'), product.place_orders)
        product.is_featured = parse_bool(data.get('is_featured'), product.is_featured)
        product.is_new_arrival = parse_bool(data.get('is_new_arrival'), product.is_new_arrival)
        product.is_active = parse_bool(data.get('is_active'), product.is_active)

        if files.get('image'):
            product.image = files.get('image')

        if files.get('video'):
            product.video = files.get('video')

        product.save()

        # Append new additional images
        for img in files.getlist('additional_images'):
            product.additional_images.create(image=img)

        return Response({
            "success": True
        }, status=status.HTTP_200_OK)

    except Category.DoesNotExist:
        return Response({
            "success": False,
            "error": "Invalid category"
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def product_delete(request, pk):
    """
    Delete product
    """
    try:
        product = Product.objects.get(pk=pk)
        product.delete()
        return Response({
            'success': True,
            'message': 'Product deleted successfully'
        })
    except Product.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def product_toggle_active(request, pk):
    """
    Toggle product active status
    """
    try:
        product = Product.objects.get(pk=pk)
        product.is_active = not product.is_active
        product.save()
        
        action = "activated" if product.is_active else "deactivated"
        return Response({
            'success': True,
            'message': f'Product {action} successfully',
            'is_active': product.is_active
        })
    except Product.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def product_toggle_featured(request, pk):
    """
    Toggle featured status
    """
    try:
        product = Product.objects.get(pk=pk)
        product.is_featured = not product.is_featured
        product.save()
        
        action = "added to" if product.is_featured else "removed from"
        return Response({
            'success': True,
            'message': f'Product {action} featured products',
            'is_featured': product.is_featured
        })
    except Product.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def product_update_stock(request, pk):
    """
    Update stock quantity
    """
    try:
        product = Product.objects.get(pk=pk)
        quantity = request.data.get('quantity')
        
        if quantity is None:
            return Response({
                'success': False,
                'error': 'Quantity is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quantity = int(quantity)
            product.quantity_available = quantity
            product.save()
            return Response({
                'success': True,
                'message': f'Stock updated to {quantity}',
                'quantity_available': product.quantity_available
            })
        except ValueError:
            return Response({
                'success': False,
                'error': 'Invalid quantity value'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Product.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def product_upload_images(request, pk):
    """
    Upload additional images for product
    """
    try:
        product = Product.objects.get(pk=pk)
        uploaded_files = request.FILES.getlist('images')  # renamed to avoid collision
        
        if not uploaded_files:
            return Response({
                'success': False,
                'error': 'No images provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        created_images = []
        for img_file in uploaded_files:
            img_instance = images.objects.create(product=product, image=img_file)  # model class
            created_images.append(img_instance)
        
        serializer = ImageSerializer(created_images, many=True, context={'request': request})
        
        return Response({
            'success': True,
            'message': f'{len(created_images)} images uploaded successfully',
            'images': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Product.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def product_delete_image(request, pk, image_id):
    """
    Delete specific image
    """
    try:
        product = Product.objects.get(pk=pk)
        image = product.additional_images.get(id=image_id)
        image.delete()
        
        return Response({
            'success': True,
            'message': 'Image deleted successfully'
        })
        
    except (Product.DoesNotExist, Images.DoesNotExist):
        return Response({
            'success': False,
            'error': 'Product or image not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def product_stats(request):
    """
    Get product statistics
    """
    try:
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        low_stock = Product.objects.filter(quantity_available__lte=10, quantity_available__gt=0).count()
        out_of_stock = Product.objects.filter(quantity_available=0).count()
        featured_products = Product.objects.filter(is_featured=True).count()
        new_arrivals = Product.objects.filter(is_new_arrival=True).count()
        
        return Response({
            'success': True,
            'stats': {
                'total_products': total_products,
                'active_products': active_products,
                'low_stock': low_stock,
                'out_of_stock': out_of_stock,
                'featured_products': featured_products,
                'new_arrivals': new_arrivals
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def category_list(request):
    """
    Get all categories for dropdown
    """
    try:
        categories = Category.objects.all()
        serializer = CategorySerializer1(categories, many=True, context={'request': request})
        return Response({
            'success': True,
            'categories': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_staff,  # Adjust based on your user model
            'is_staff': user.is_staff,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })

# 1️⃣ List all invoices (GET)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-created_at')
    serializer = InvoiceSerializer(invoices, many=True)
    return Response({'success': True, 'invoices': serializer.data}, status=status.HTTP_200_OK)


# 2️⃣ Retrieve / Update invoice status
from django.db import transaction

@api_view(['GET', 'PUT'])
@permission_classes([IsAdminUser])
def invoice_detail(request, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return Response({'success': False, 'error': 'Invoice not found'}, status=404)

    if request.method == 'GET':
        serializer = InvoiceDetailSerializer(invoice)
        return Response({'success': True, 'invoice': serializer.data})

    elif request.method == 'PUT':
        status_value = request.data.get('status')
        delivered_by = request.data.get('delivered_by')  # new field

        if status_value not in [s[0] for s in Invoice.Status.choices]:
            return Response({'success': False, 'error': 'Invalid status'}, status=400)

        invoice.status = status_value

        # If status is shipped, require delivered_by
        if status_value == Invoice.Status.SHIPPED:
            if not delivered_by:
                return Response({'success': False, 'error': 'Please specify delivered by'}, status=400)
            invoice.delveried_by = delivered_by

        # Decrease product quantity if status is COMPLETED
        if status_value == Invoice.Status.COMPLETED:
            with transaction.atomic():  # ensure all updates succeed or rollback
                for item in invoice.items.all():
                    if item.product:
                        if item.product.quantity_available >= item.quantity:
                            item.product.quantity_available -= item.quantity
                            item.product.save()
                        else:
                            return Response({
                                'success': False,
                                'error': f"Not enough quantity for product {item.product.name}"
                            }, status=400)

        invoice.save()
        serializer = InvoiceDetailSerializer(invoice)
        return Response({'success': True, 'invoice': serializer.data})



# 3️⃣ Delete invoice
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def invoice_delete(request, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        invoice.delete()
        return Response({'success': True, 'message': 'Invoice deleted successfully'}, status=status.HTTP_200_OK)
    except Invoice.DoesNotExist:
        return Response({'success': False, 'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def banners_api(request):
    """
    Single API for GET (list), POST (create), PUT (update), DELETE (delete)
    """
    if request.method == 'GET':
        banners = Banner.objects.all()
        serializer = BannerSerializer(banners, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BannerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        banner_id = request.data.get('id')
        if not banner_id:
            return Response({"error": "Banner ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            banner = Banner.objects.get(id=banner_id)
        except Banner.DoesNotExist:
            return Response({"error": "Banner not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BannerSerializer(banner, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        banner_id = request.data.get('id')
        if not banner_id:
            return Response({"error": "Banner ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            banner = Banner.objects.get(id=banner_id)
            banner.delete()
            return Response({"success": "Banner deleted"})
        except Banner.DoesNotExist:
            return Response({"error": "Banner not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def categories_api(request):
    if request.method == 'GET':
        # List all categories
        categories = Category.objects.all().order_by('id')
        data = []
        for c in categories:
            data.append({
                'id': c.id,
                'name': c.name,
                'slug': c.slug,
                'description': c.description,
                'image': c.image.url if c.image else None,
                'is_active': c.is_active,
            })
        return Response(data)

    elif request.method == 'POST':
        # Create new category
        name = request.data.get('name')
        slug = request.data.get('slug') or slugify(name)
        description = request.data.get('description', '')
        is_active = request.data.get('is_active', 'true') in ['true', True, '1']

        category = Category(name=name, slug=slug, description=description, is_active=is_active)
        if 'image' in request.FILES:
            category.image = request.FILES['image']
        category.save()

        return Response({
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'description': category.description,
            'image': category.image.url if category.image else None,
            'is_active': category.is_active,
        }, status=status.HTTP_201_CREATED)

    elif request.method == 'PUT':
        # Update category
        category_id = request.data.get('id')
        if not category_id:
            return Response({'error': 'Category ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        
        category.name = request.data.get('name', category.name)
        category.slug = request.data.get('slug') or slugify(category.name)
        category.description = request.data.get('description', category.description)
        category.is_active = request.data.get('is_active', str(category.is_active)) in ['true', True, '1']

        if 'image' in request.FILES:
            category.image = request.FILES['image']

        category.save()

        return Response({
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'description': category.description,
            'image': category.image.url if category.image else None,
            'is_active': category.is_active,
        })

    elif request.method == 'DELETE':
        # Delete category
        category_id = request.data.get('id')
        if not category_id:
            return Response({'error': 'Category ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return Response({'success': True})
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_analytics(request):
    # 1. Messages
    messages = ContactMessage.objects.all().order_by('-created_at')[:50]
    messages_data = [
        {
            "id": m.id,
            "email": m.email,
            "phone_number": m.phone_number,
            "subject": m.subject,
            "message": m.message,
            "created_at": m.created_at,
            "is_read": m.is_read
        } for m in messages
    ]

    # 2. WhatsApp Info
    wa_info_list = WAInfo.objects.all().order_by('-updated_at')
    wa_data = WAInfoSerializer(wa_info_list, many=True).data if wa_info_list.exists() else []

    # 3. Sales & Revenue - only completed invoices
    completed_invoices = Invoice.objects.filter(status=Invoice.Status.COMPLETED)
    total_sales = completed_invoices.count()
    total_revenue = completed_invoices.aggregate(total=Sum('total'))['total'] or 0
    total_invoices = completed_invoices.count()

    # Monthly revenue data
    monthly_revenue = completed_invoices.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        revenue=Sum('total'),
        orders=Count('id')
    ).order_by('month')[:12]

    # 4. Recent invoices
    recent_invoices = completed_invoices.order_by('-created_at')[:10]
    recent_invoices_data = [
        {
            "id": inv.id,
            "name": inv.name,
            "total": inv.total,
            "status": inv.status,
            "created_at": inv.created_at,
            "items_count": inv.items.count() if hasattr(inv, 'items') else 0
        } for inv in recent_invoices
    ]

    # 5. Branches
    branches = Branch.objects.all()
    branches_data = BranchSerializer(branches, many=True).data if branches.exists() else []

    # 6. Top products
    top_products = Product.objects.filter(
        invoice_items__invoice__status=Invoice.Status.COMPLETED
    ).annotate(
        sold_quantity=Sum('invoice_items__quantity'),
        revenue=Sum(F('invoice_items__quantity') * F('invoice_items__price'))
    ).order_by('-sold_quantity')[:10]

    top_products_data = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category.name if p.category else "",
            "sold_quantity": p.sold_quantity or 0,
            "revenue": float(p.revenue or 0)
        } for p in top_products
    ]

    return Response({
        "messages": messages_data,
        "wa_info": wa_data,
        "sales": {
            "total_sales": total_sales,
            "total_revenue": float(total_revenue),
            "total_invoices": total_invoices,
            "recent_invoices": recent_invoices_data,
            "monthly_revenue": list(monthly_revenue)
        },
        "branches": branches_data,
        "top_products": top_products_data,
        "stats": {
            "unread_messages": ContactMessage.objects.filter(is_read=False).count(),
            "pending_orders": Invoice.objects.filter(status=Invoice.Status.PENDING).count(),
            "active_branches": branches.filter(primery_branch=True).count(),
            "low_stock_products": Product.objects.filter(quantity_available__lt=10).count()
        }
    })

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_wa_info(request, id):
    try:
        wa_info = WAInfo.objects.get(id=id)
        serializer = WAInfoSerializer(wa_info, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except WAInfo.DoesNotExist:
        return Response({"error": "WAInfo not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_wa_info(request):
    serializer = WAInfoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_branch(request, id):
    try:
        branch = Branch.objects.get(id=id)
        serializer = BranchSerializer(branch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Branch.DoesNotExist:
        return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_branch(request):
    serializer = BranchSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_branch(request, id):
    try:
        branch = Branch.objects.get(id=id)
        branch.delete()
        return Response({"message": "Branch deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Branch.DoesNotExist:
        return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def mark_message_read(request, id):
    try:
        message = ContactMessage.objects.get(id=id)
        message.is_read = True
        message.save()
        return Response({"message": "Marked as read"})
    except ContactMessage.DoesNotExist:
        return Response({"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND)





@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def cities_list(request):
    if request.method == 'GET':
        cities = City.objects.all().order_by('name')
        serializer = CitySerializer(cities, many=True)
        return Response({'success': True, 'data': serializer.data})
    
    if request.method == 'POST':
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'City created', 'data': serializer.data}, status=201)
        return Response({'success': False, 'errors': serializer.errors}, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def city_detail(request, pk):
    try:
        city = City.objects.get(pk=pk)
    except City.DoesNotExist:
        return Response({'success': False, 'error': 'City not found'}, status=404)
    
    if request.method == 'GET':
        serializer = CitySerializer(city)
        return Response({'success': True, 'data': serializer.data})
    
    if request.method == 'PUT':
        serializer = CitySerializer(city, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'City updated', 'data': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=400)
    
    if request.method == 'DELETE':
        city.delete()
        return Response({'success': True, 'message': 'City deleted'})