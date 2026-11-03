from django.shortcuts import render, redirect, get_object_or_404
from addcart.addcart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from myApp.models import Product, Profile
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import datetime
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY or None


# ─── Customer: track your order ───────────────────────────────────────────────

def track_order(request):
    order = None
    error = None
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number', '').strip()
        email = request.POST.get('email', '').strip()
        try:
            order = Order.objects.get(tracking_number=tracking_number, email=email)
            items = OrderItem.objects.filter(order=order).select_related('product')
            steps = [
                ('pending', 'Ordered', 'bag-check'),
                ('processing', 'Processing', 'gear'),
                ('shipped', 'Shipped', 'truck'),
                ('delivered', 'Delivered', 'house-check'),
            ]
            status_order = ['pending', 'processing', 'shipped', 'delivered']
            step_index = status_order.index(order.status) if order.status in status_order else 0
            return render(request, 'payment/track_order.html', {
                'order': order,
                'items': items,
                'found': True,
                'steps': steps,
                'step_index': step_index,
            })
        except Order.DoesNotExist:
            error = "No order found with that tracking number and email. Please check and try again."
    return render(request, 'payment/track_order.html', {'error': error, 'found': False})


# ─── Customer: my orders (logged in) ─────────────────────────────────────────

def my_orders(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to view your orders.")
        return redirect('login')
    orders = Order.objects.filter(user=request.user).order_by('-date_ordered')
    return render(request, 'payment/my_orders.html', {'orders': orders})


def my_order_detail(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    order = get_object_or_404(Order, pk=pk, user=request.user)
    items = OrderItem.objects.filter(order=order).select_related('product')
    order_flow = ['pending', 'processing', 'shipped', 'delivered']
    idx = order_flow.index(order.status) if order.status in order_flow else 0
    progress = [(label, '#6f42c1' if i <= idx else '#e9ecef')
                for i, label in enumerate(['Ordered', 'Processing', 'Shipped', 'Delivered'])]
    return render(request, 'payment/my_order_detail.html', {'order': order, 'items': items, 'progress': progress})


# ─── Admin dashboards ─────────────────────────────────────────────────────────

def orders(request, pk):
    if not (request.user.is_authenticated and request.user.is_superuser):
        messages.error(request, "Access Denied!")
        return redirect('home')
    order = get_object_or_404(Order, id=pk)
    items = OrderItem.objects.filter(order=pk)
    if request.POST:
        new_status = request.POST.get('order_status')
        if not new_status:
            new_status = 'shipped' if request.POST.get('shipping_status') == 'true' else 'processing'
        order.status = new_status
        order.shipped = new_status in ('shipped', 'delivered')
        order.save()
        messages.success(request, "Order updated successfully.")
        return redirect('orders', pk=pk)
    return render(request, "payment/orders.html", {"order": order, "items": items})


def not_shipped_dash(request):
    if not (request.user.is_authenticated and request.user.is_superuser):
        messages.error(request, "Access Denied!")
        return redirect('home')
    orders = Order.objects.filter(shipped=False).order_by('-date_ordered')
    if request.POST:
        num = request.POST.get('num')
        o = get_object_or_404(Order, id=num)
        o.shipped, o.status = True, Order.STATUS_SHIPPED
        o.save()
        messages.success(request, "Marked as shipped.")
        return redirect('not_shipped_dash')
    return render(request, "payment/not_shipped_dash.html", {"orders": orders})


def shipped_dash(request):
    if not (request.user.is_authenticated and request.user.is_superuser):
        messages.error(request, "Access Denied!")
        return redirect('home')
    orders = Order.objects.filter(shipped=True).order_by('-date_shipped')
    if request.POST:
        num = request.POST.get('num')
        o = get_object_or_404(Order, id=num)
        o.shipped, o.status = False, Order.STATUS_PROCESSING
        o.save()
        messages.success(request, "Marked as not shipped.")
        return redirect('shipped_dash')
    return render(request, "payment/shipped_dash.html", {"orders": orders})


# ─── Checkout flow ────────────────────────────────────────────────────────────

def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    if not cart.cart:
        messages.error(request, "Your cart is empty.")
        return redirect('home')

    if request.user.is_authenticated:
        try:
            shipping_user = ShippingAddress.objects.get(user_id=request.user.id)
            shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        except ShippingAddress.DoesNotExist:
            shipping_form = ShippingForm(request.POST or None)
    else:
        shipping_form = ShippingForm(request.POST or None)

    return render(request, "payment/checkout.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "shippping_form": shipping_form,
    })


def billing_info(request):
    if not request.POST:
        messages.error(request, "Access denied.")
        return redirect('home')

    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    request.session['my_shipping'] = dict(request.POST)

    client_secret = ''
    if settings.STRIPE_ENABLED:
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(round(float(totals) * 100)),  # cents
                currency='zar',
                automatic_payment_methods={'enabled': True, 'allow_redirects': 'never'},
            )
            client_secret = intent.client_secret
            request.session['payment_intent_id'] = intent.id
        except stripe.StripeError as e:
            messages.error(request, f"Payment setup failed: {getattr(e, 'user_message', None) or str(e)}")
            return redirect('checkout')

    return render(request, "payment/billing_info.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "shippping_info": request.POST,
        "stripe_enabled": settings.STRIPE_ENABLED,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "client_secret": client_secret,
    })


def process_order(request):
    if not request.POST:
        messages.error(request, "Access denied.")
        return redirect('home')

    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    my_shipping_raw = request.session.get('my_shipping', {})
    # Session stores lists for each value when saving POST dict
    def get_val(d, key):
        v = d.get(key, [''])
        return v[0] if isinstance(v, list) else v

    full_name = get_val(my_shipping_raw, 'shipping_full_name')
    email = get_val(my_shipping_raw, 'shipping_email')
    shipping_address = (
        f"{get_val(my_shipping_raw, 'shipping_address1')}\n"
        f"{get_val(my_shipping_raw, 'shipping_address2')}\n"
        f"{get_val(my_shipping_raw, 'shipping_city')}\n"
        f"{get_val(my_shipping_raw, 'shipping_state')}\n"
        f"{get_val(my_shipping_raw, 'shipping_zipcode')}\n"
        f"{get_val(my_shipping_raw, 'shipping_country')}"
    )

    payment_intent_id = request.session.get('payment_intent_id', '')
    paid = False
    if settings.STRIPE_ENABLED:
        # Never trust the browser: ask Stripe whether this intent really succeeded
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            paid = intent.status == 'succeeded'
        except Exception:
            paid = False
    else:
        # Test mode (no Stripe keys): only the standard Stripe test card is accepted
        card = request.POST.get('test_card_number', '').replace(' ', '')
        paid = card == '4242424242424242'
        payment_intent_id = 'TEST-MODE'

    if not paid:
        messages.error(request, "Payment was not completed. Please try again.")
        return redirect('checkout')

    if request.user.is_authenticated:
        create_order = Order(
            user=request.user,
            full_name=full_name,
            email=email,
            shipping_address=shipping_address,
            amount_paid=totals,
            stripe_payment_intent=payment_intent_id,
            status=Order.STATUS_PROCESSING,
        )
    else:
        create_order = Order(
            full_name=full_name,
            email=email,
            shipping_address=shipping_address,
            amount_paid=totals,
            stripe_payment_intent=payment_intent_id,
            status=Order.STATUS_PROCESSING,
        )

    create_order.save()
    order_id = create_order.pk

    for product in cart_products():
        qty = quantities().get(str(product.id), 1)
        OrderItem.objects.create(
            order_id=order_id,
            product=product,
            user=request.user if request.user.is_authenticated else None,
            quantity=qty,
            price=product.price,
        )

    # Clear cart from session
    if 'cart' in request.session:
        del request.session['cart']
    if 'my_shipping' in request.session:
        del request.session['my_shipping']
    if 'payment_intent_id' in request.session:
        del request.session['payment_intent_id']
    request.session.modified = True

    # Clear saved cart from profile
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            profile.old_carty = ""
            profile.save()
        except Profile.DoesNotExist:
            pass

    messages.success(request, f"Order placed! Your tracking number is {create_order.tracking_number}.")
    return redirect('payment_success', pk=order_id)


def payment_success(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = OrderItem.objects.filter(order=order).select_related('product')
    return render(request, "payment/payment_success.html", {'order': order, 'items': items})
