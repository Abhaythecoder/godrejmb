# app/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Product, Color
from django import template
register = template.Library()

# A dictionary to map the filename to the view name for clarity
# This is a good practice to manage your views
TEMPLATE_PAGES = {
    'about.html': 'about_view',
    'blog.html': 'blog_view',
    'blog-detail.html': 'blog_detail_view',
    'contact.html': 'contact_view',
    'home-02.html': 'home_02_view',
    'home-03.html': 'home_03_view',
    'index.html': 'index_view',
    'product.html': 'product_list_view',
    'product-detail.html': 'product_detail_view',
    'shoping-cart.html': 'shopping_cart_view',
}

def about_view(request):
    """Renders the about.html template."""
    return render(request, 'app/about.html')


def contact_view(request):
    """Renders the contact.html template."""
    return render(request, 'app/contact.html')

def index_view(request):
    """Renders the index.html template (homepage)."""
    query = request.GET.get('search', '').strip()
    products = Product.objects.all()
    if query:
        from django.db.models import Q
        products = products.filter(
            Q(name__icontains=query) |
            Q(features__icontains=query) |
            Q(materials__icontains=query) |
            Q(measurements__icontains=query) |
            Q(tags__icontains=query)
        )
    featured_product = products.first()
    context = {
        'products': products,
        'featured_product': featured_product,
        'search_query': query,
    }
    return render(request, 'app/index.html', context)

def product_list_view(request):
    """Renders the product.html template with all products from the database."""
    query = request.GET.get('search', '').strip()
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    color = request.GET.get('color')
    tag = request.GET.get('tag', '').lower()
    
    products = Product.objects.all()
    
    # Apply tag/category filter
    if tag:
        # Check if the tag is a category
        if tag in [choice[0] for choice in Product.CATEGORY_CHOICES]:
            products = products.filter(category=tag)
        # Check if it's a special tag
        elif tag in [choice[0] for choice in Product.TAG_CHOICES]:
            products = products.filter(tags__contains=tag)
    
    # Apply search filter
    if query:
        from django.db.models import Q
        products = products.filter(
            Q(name__icontains=query) |
            Q(features__icontains=query) |
            Q(materials__icontains=query) |
            Q(measurements__icontains=query) |
            Q(tags__icontains=query)
        )
    
    # Apply price filters
    if min_price:
        try:
            min_price = float(min_price)
            from django.db.models import Q
            products = products.filter(
                Q(discounted_price__gte=min_price) |
                (Q(discounted_price__isnull=True) & Q(original_price__gte=min_price))
            )
        except ValueError:
            pass
            
    if max_price:
        try:
            max_price = float(max_price)
            from django.db.models import Q
            products = products.filter(
                Q(discounted_price__lte=max_price) |
                (Q(discounted_price__isnull=True) & Q(original_price__lte=max_price))
            )
        except ValueError:
            pass
            
    # Apply color filter
    if color:
        products = products.filter(colors__name=color)
    
    from .models import Color
    colors = Color.objects.all()
    
    return render(request, 'app/product.html', {
        'products': products,
        'search_query': query,
        'colors': colors,
        'current_tag': tag,  # Pass the current tag to the template
        'current_color': color,  # Pass the current color to the template
        'current_min_price': min_price,  # Pass the current price range
        'current_max_price': max_price,
    })

def product_detail_view(request, product_id):
    """Renders the product-detail.html template for a single product."""
    product = get_object_or_404(Product, pk=product_id)
    # Fetch related products by category (excluding the current product)
    related_products = Product.objects.filter(category=product.category).exclude(pk=product_id)
    return render(request, 'app/product-detail.html', {
        'product': product,
        'related_products': related_products,
    })

def shopping_cart_view(request):
    import sys
    print("DEBUG: Entering shopping_cart_view", file=sys.stderr)
    
    # Get cart from session
    cart = request.session.get('cart', {})
    print(f"DEBUG: Current cart contents: {cart}", file=sys.stderr)
    
    # Handle POST requests (cart updates)
    if request.method == 'POST':
        try:
            if 'increase' in request.POST:
                key = request.POST['increase']
                cart[key] = cart.get(key, 0) + 1
            elif 'decrease' in request.POST:
                key = request.POST['decrease']
                if cart.get(key, 0) > 1:
                    cart[key] -= 1
                else:
                    cart.pop(key, None)
            elif 'remove' in request.POST:
                key = request.POST['remove']
                cart.pop(key, None)
            
            request.session['cart'] = cart
            request.session.modified = True
            return redirect('shopping_cart')
            
        except Exception as e:
            print(f"DEBUG: Error updating cart - {str(e)}", file=sys.stderr)
    
    # Process cart items for display
    cart_items = []
    subtotal = 0
    
    try:
        for key, quantity in cart.items():
            print(f"DEBUG: Processing cart item with key: {key}", file=sys.stderr)
            
            # Split the key to get product_id and color_id
            parts = key.split('|', 1)
            product_id = parts[0]
            color_id = parts[1] if len(parts) > 1 and parts[1] != "" else None
            
            try:
                # Get product
                product = Product.objects.get(pk=product_id)
                
                # Get color if specified
                color_obj = None
                if color_id:
                    try:
                        color_obj = Color.objects.get(pk=color_id)
                    except Color.DoesNotExist:
                        print(f"DEBUG: Color not found for id {color_id}", file=sys.stderr)
                
                print(f"DEBUG: key={key}, product_id={product_id}, color_id={color_id}, color_obj={color_obj}", file=sys.stderr)
                
                # Add item to cart_items list
                cart_items.append({
                    'product': product,
                    'color': color_obj,
                    'quantity': quantity,
                    'key': key,
                    'total': product.discounted_price * quantity if product.discounted_price else product.original_price * quantity
                })
                
                # Update subtotal
                subtotal += product.discounted_price * quantity if product.discounted_price else product.original_price * quantity
                
            except Product.DoesNotExist:
                print(f"DEBUG: Product not found for id {product_id}, removing from cart", file=sys.stderr)
                cart.pop(key, None)
                request.session.modified = True
                
    except Exception as e:
        print(f"DEBUG: Error processing cart items - {str(e)}", file=sys.stderr)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': subtotal,  # Add tax/shipping calculations here if needed
    }
    
    return render(request, 'app/shoping-cart.html', context)

from django.http import JsonResponse

def add_to_cart_view(request, product_id):
    import sys
    print(f"DEBUG: Received request to add_to_cart - Method: {request.method}", file=sys.stderr)
    print(f"DEBUG: POST data: {request.POST}", file=sys.stderr)
    print(f"DEBUG: Headers: {request.headers}", file=sys.stderr)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        product = get_object_or_404(Product, pk=product_id)
        
        # Get quantity, defaulting to 1 if not provided or invalid
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except ValueError:
            quantity = 1
            
        # Get and validate color selection
        has_colors = product.colors.exists()
        color_id = request.POST.get('color', '')
        print(f"DEBUG: Product has colors: {has_colors}, Received color_id: {color_id}", file=sys.stderr)
        
        if has_colors:
            if not color_id:
                print("DEBUG: Color required but not provided", file=sys.stderr)
                return JsonResponse({
                    'error': 'Please select a color before adding to cart'
                }, status=400)
                
            try:
                color = product.colors.get(pk=color_id)
                print(f"DEBUG: Found color: {color.name}", file=sys.stderr)
            except Color.DoesNotExist:
                print(f"DEBUG: Invalid color ID: {color_id}", file=sys.stderr)
                return JsonResponse({
                    'error': 'Please select a valid color'
                }, status=400)
        
        # Initialize session if needed
        if not request.session.session_key:
            request.session.create()
        
        # Get or create cart in session
        cart = request.session.get('cart', {})
        
        # Create cart key
        key = f"{product_id}|{color_id}" if color_id else str(product_id)
        print(f"DEBUG: Cart key created: {key}", file=sys.stderr)
        
        # Update cart
        if key in cart:
            cart[key] += quantity
        else:
            cart[key] = quantity
        
        # Save cart back to session
        request.session['cart'] = cart
        request.session.modified = True
        
        print(f"DEBUG: Cart after adding - {cart}", file=sys.stderr)
        print(f"DEBUG: Session ID: {request.session.session_key}", file=sys.stderr)
        
        # Return success response
        response_data = {
            'status': 'success',
            'message': f'Added {quantity} item(s) to cart',
            'cart_count': sum(cart.values()),
            'redirect_url': request.build_absolute_uri(reverse('shopping_cart'))
        }
        print(f"DEBUG: Sending response - {response_data}", file=sys.stderr)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"DEBUG: Error adding to cart - {str(e)}", file=sys.stderr)
        return JsonResponse({
            'error': 'An error occurred while adding the item to cart. Please try again.'
        }, status=500)

def update_cart_view(request):
    cart = request.session.get('cart', {})
    if request.method == 'POST':
        if 'increase' in request.POST:
            product_id = request.POST['increase']
            cart[product_id] = cart.get(product_id, 0) + 1
        elif 'decrease' in request.POST:
            product_id = request.POST['decrease']
            if cart.get(product_id, 0) > 1:
                cart[product_id] -= 1
            else:
                cart.pop(product_id, None)
        elif 'remove' in request.POST:
            product_id = request.POST['remove']
            cart.pop(product_id, None)
        request.session['cart'] = cart
        return redirect('shopping_cart')
    products = Product.objects.filter(pk__in=cart.keys())
    subtotal = 0
    for product in products:
        quantity = cart.get(str(product.pk), 0)
        subtotal += product.original_price * quantity
    return render(request, 'app/cart.html', {'products': products, 'subtotal': subtotal, 'total': subtotal})

@register.filter
def split(value, key):
    return value.split(key)

def special_tags_view(request):
    tag = request.GET.get('tag', '').lower().replace(' ', '_')
    # Map possible tag values to model field values
    tag_map = {
        'offers': 'offers',
        'offer': 'offers',
        'new arrivals': 'new_arrivals',
        'new_arrivals': 'new_arrivals',
        'newarrival': 'new_arrivals',
        'best sellers': 'best_sellers',
        'best_sellers': 'best_sellers',
        'bestseller': 'best_sellers',
    }
    tag_value = tag_map.get(tag, None)
    if tag_value:
        products = Product.objects.filter(tags__contains=tag_value)
    else:
        products = Product.objects.filter(tags__in=['offers', 'new_arrivals', 'best_sellers'])
    return render(request, 'app/special_tags.html', {'products': products})