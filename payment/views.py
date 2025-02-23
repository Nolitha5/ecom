from django.shortcuts import render, redirect
from addcart.addcart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from myApp.models import Product, Profile
import datetime


def orders(request,pk):
    if request.user.is_authenticated and request.user.is_superuser:
        #get order
     order = Order.objects.get(id=pk)
     #order items
     items = OrderItem.objects.filter(order=pk)
     if request.POST:
          status = request.POST['shipping_status']
          #check if true or false
          if status == "true":
              order = Order.objects.filter(id=pk)
              now = datetime.datetime.now()
              order.update(shipped=True,date_shipped = now)
          else:
              order = Order.objects.filter(id=pk)
              order.update(shipped=False)
          messages.success(request,"Shipping status updated")
          return redirect('home')
     return render(request,"payment/orders.html",{"order":order,"items":items})
    else:
     messages.success(request,"Access Denied!")
     return redirect('home')
 
def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)  
        if request.POST:
          status = request.POST['shipping_status']
          num = request.POST['num']
          order = Order.objects.filter(id=num)
          now = datetime.datetime.now()
          order.update(shipped=True,date_shipped = now)
          messages.success(request,"Shipping status updated")
          return redirect('home')  
        return render(request, "payment/not_shipped_dash.html", {"orders":orders}) 
    else:
     messages.success(request,"Access Denied!")
     return redirect('home')

def shipped_dash(request):
   if request.user.is_authenticated and request.user.is_superuser:
     orders = Order.objects.filter(shipped=True) 
     if request.POST:
          status = request.POST['shipping_status']
          num = request.POST['num']
          order = Order.objects.filter(id=num)
          now = datetime.datetime.now()
          order.update(shipped=False)
          messages.success(request,"Shipping status updated")
          return redirect('home')  
     return render(request, "payment/shipped_dash.html", {"orders":orders}) 
   else:
     messages.success(request,"Access Denied!")
     return redirect('home')

def process_order(request):
    if request.GET:
       cart = Cart(request)
       cart_products = cart.get_prods
       quantities = cart.get_quants
       totals = cart.cart_total()
      
     #get shipping data
       payment_form =PaymentForm(request.POST or None)
       my_shipping = request.session.get('my_shipping')
       #my_shippnig = request.cart.get('my_shipping')
       
        #gather order info
       #full_name = my_shipping['shipping_full_name']
       full_name = request.POST['shipping_full_name']
       email = my_shipping['shipping_email']
      
       #create shipping address
       shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}" 
       #shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}" 
       """
       full_name = my_shipping.get('shipping_full_name', '')
       email = my_shipping.get('shipping_email', '')
       shipping_address = f"{my_shipping.get('shipping_address1', '')}\n" \
                           f"{my_shipping.get('shipping_address2', '')}\n" \
                           f"{my_shipping.get('shipping_city', '')}\n" \
                           f"{my_shipping.get('shipping_state', '')}\n" \
                           f"{my_shipping.get('shipping_zipcode', '')}\n" \
                           f"{my_shipping.get('shipping_country', '')}"

       """
       amount_paid = totals
       

       if request.user.is_authenticated:
            #logged in
            user =request.user
            create_order = Order(user=user,full_name=full_name,email=email,shipping_address=shipping_address,amount_paid=amount_paid)
            create_order.save()
            #add order item
            order_id = create_order.pk
            #get product id
            for product in cart_products():
               product_id = product.id
               price = product.price
               for key,value in quantities().items():
                if int(key) == product.id:
                    create_order_item = OrderItem(order_id=order_id,product=product_id,user=user,quantity=value,price=price)
                    create_order_item.save() 
            #delete our cart
            for key in list(request.session.key()):
                if key == "session_key":
                    del request.session[key]
        

            messages.success(request, "Order placed")
            return redirect('home')
    
            
       else:
            #not logged in
            create_order = Order(full_name=full_name,email=email,shipping_address=shipping_address,amount_paid=amount_paid)
            create_order.save()
            
            #add order item
            order_id = create_order.pk
            #get product id
            for product in cart_products():
               product_id = product.id
               price = product.price
               for key,value in quantities().items():
                if int(key) == product.id:
                    create_order_item = OrderItem(order_id=order_id,product=product_id,quantity=value,price=price)
                    create_order_item.save() 
                
            #delete our cart
            for key in list(request.session.key()):
                if key == "session_key":
                    del request.session[key]
            
            #del cart from db(old cart field)
            current_user = Profile.objects.filter(user__id=request.user.id)
            #de shopping cart
            current_user.update(old_carty="")
            messages.success(request, "Order placed")
            return redirect('home')
    else:
        messages.success(request, "Access denied")
        return redirect('home') 
      
def billing_info(request):
 if request.POST:
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    
    #create a session with shipping info
    my_shipping =request.POST
    request.session['my_shipping'] = my_shipping
   
    #check if user is logged in
    if request.user.is_authenticated:
        billing_form =PaymentForm() 
        return render(request, "payment/billing_info.html", {"cart_products": cart_products, "quantities":quantities,"totals":totals,"shipping_info":request.POST,"billing_form":billing_form})  
    else:
     billing_form =PaymentForm() 
    return render(request, "payment/billing_info.html", {"cart_products": cart_products, "quantities":quantities,"totals":totals,"shipping_info":request.POST,"billing_form":billing_form}) 
    #return render(request, "payment/billing_info.html", {"cart_products": cart_products, "quantities":quantities,"totals":totals,"shipping_form":shipping_form})
 else:
     messages.success(request, "Access denied")
     return redirect('home') 
    
     
def checkout(request):
    
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    
    if request.user.is_authenticated:
        #checkout as logged in user
      
       shipping_user = ShippingAddress.objects.get(user_id=request.user.id)
       shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
       
       return render(request, "payment/checkout.html", {"cart_products": cart_products, "quantities":quantities,"totals":totals,"shipping_form":shipping_form})
  
    else: 
        #checkout as guest
        shipping_form = ShippingForm(request.POST or None)
    return render(request, "payment/checkout.html", {"cart_products": cart_products, "quantities":quantities,"totals":totals,"shipping_form":shipping_form})

  

def payment_success(request):
    return render(request, "payment/payment_success.html", {})

      
