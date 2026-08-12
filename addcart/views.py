from django.shortcuts import render, get_object_or_404
from .addcart import Cart
from myApp.models import Product
from django.http import JsonResponse
from django.contrib import messages


def addcart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    return render(request, "addcart_summary.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
    })


def addcart_add(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        quantity = int(request.POST.get('quantity', 1))
        get_object_or_404(Product, id=product_id)
        cart.add(product_id, quantity)
        cart_quantity = cart.total_quantity()
        messages.success(request, 'Product added to cart!')
        return JsonResponse({'qty': cart_quantity})


def addcart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        cart.delete(product=product_id)
        cart_quantity = cart.total_quantity()
        messages.success(request, 'Product removed from cart.')
        return JsonResponse({'qty': cart_quantity})


def addcart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty', 1))
        cart.update(product=product_id, quantity=product_qty)
        cart_quantity = cart.total_quantity()
        messages.success(request, 'Cart updated!')
        return JsonResponse({'qty': cart_quantity})
