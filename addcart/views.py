
from django.shortcuts import render,get_object_or_404
from .addcart import Cart
from myApp.models import Product
from django .http import  JsonResponse
from django .contrib import  messages

def addcart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    return render(request, "addcart_summary.html", {"cart_products": cart_products, "quantities":quantities,"totals":totals})

def addcart_add(request):
 cart = Cart(request)    
 if request.POST.get('action') == 'post':
     product_id = int(request.POST.get('product_id'))
     quantity = int(request.POST.get('quantity', 1))
     product = get_object_or_404(Product, id=product_id)
     #save session
     #cart.add(product=product)
     cart.add(product_id, quantity)
     #cart_quantity = cart.__len__()
     cart_quantity = sum(cart.cart.values())
     response = JsonResponse({'qty:': cart_quantity})
     messages.success(request, 'Product has been added to cart!')
     #response = JsonResponse({'Product Name:': product.name})
     
     return response
         
         
def addcart_delete(request):
   cart = Cart(request)
   if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        cart.delete(product=product_id)
        response = JsonResponse({'product': product_id})
        messages.success(request, 'Product has been deleted from cart')
        return response

def addcart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        #get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty',1))

        cart.update(product=product_id, quantity=product_qty)
        
        response = JsonResponse({'qty': product_qty})
        messages.success(request, 'Your cart has been updated!')
        return response
    #return redirect('addcart_summary')
    

""" cart = Cart(request) 
    product_id = request.POST.get('product_id')
    product_qty = request.POST.get('product_qty')
    try:
        product = get_object_or_404(Product, id=product_id)
        product_qty = int(product_qty)
    except (ValueError, Product.DoesNotExist):
        return JsonResponse({'error': 'Invalid product ID or quantity'}, status=400)
    cart.update(product=product_id,quantity=product_qty)
    response = JsonResponse({'qty':product_qty})
    return response
    #return redirect('addcart_summary')"""
    
    
