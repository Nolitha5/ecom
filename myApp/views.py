from django.shortcuts import render , redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
import json
from addcart.addcart import Cart


def search(request):
    if request.method == 'POST':
        searched_query = request.POST.get('searched', '').strip()
        if not searched_query:
            messages.error(request, "Please enter a search term.")
            return render(request, 'myApp/search.html', {})
        
        searched = Product.objects.filter(Q(name__icontains=searched_query) | Q(description__icontains=searched_query))
        if not searched.exists():
            messages.success(request, "That product does not exist, please try again.")
            return render(request, 'myApp/search.html', {})
        
        return render(request, 'myApp/search.html', {'searched': searched})
    
    return render(request, 'myApp/search.html', {})

def update_info(request):
    if request.user.is_authenticated:
        #get current user
        current_user = Profile.objects.get(user__id=request.user.id)
        #current user's shipping info
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        #original user form
        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        if form.is_valid() or shipping_form.is_valid():
            #save org form
            form.save()
            #save shipping form
            shipping_form.save()
            messages.success(request, "Your info has been updated")
            return redirect('home')
        
        return render(request, 'myApp/update_info.html', {'form': form,'shipping_form':shipping_form})
    else:
        messages.success(request, "You must be logged in to access the page")
        return redirect('home')


 

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been updated,please log in again")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                 messages.error(request, error)   
                 return redirect('update_password') 

        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'myApp/update_password.html', {'form': form})
    else:
        messages.success(request, "You must be logged in View the page!")
    return redirect('home') 
    

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None,instance=current_user)
        
        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, "User has been updated")
            return redirect('home')
        return render(request,'myApp/update_user.html',{'user_form':user_form})
    else:
        messages.success(request, "You must be logged in to access the page")
        return redirect('home')
    

 

def category_summary(request):
    categories = Category.objects.all()
    
    return render(request,'myApp/category_summary.html',{"categories":categories})


def category(request, clothes):
    #Replace hyphens with spaces
    clothes = clothes.replace('-', ' ')
    #Grabbing the category from the url
    try:
         #Look up the category
         category = Category.objects.get(name=clothes)
         products = Product.objects.filter(category=category)
         return render(request,'myApp/category.html', {'products':products, 'category':category})
    except:
        messages.success(request,("This category doesn’t exist."))
        return redirect('home')

def product(request,pk):
    product = Product.objects.get(id=pk)
    return render(request, 'myApp/product.html', {'product': product})

def home(request):
    products = Product.objects.all()
    return render(request, 'myApp/home.html', {'products': products})


def about(request):
    return render(request, 'myApp/about.html', {})


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Make sure this line is properly indented
        password = request.POST.get('password')

        # Check if username and password are not None or empty
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'myApp/login.html', {})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            #do shopping 
            current_user = Profile.objects.get(user__id=request.user.id)
            #get saved cart from db
            saved_cart = current_user.old_carty
            if saved_cart:
                converted_cart = json.loads(saved_cart)
                cart = Cart(request)
                for key,value in converted_cart.items():
                    cart.db_add(product=key,quantity=value)
            
            
            messages.success(request, 'Logged in successfully!')
            return redirect('home')  
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'myApp/login.html')

def logout_user(request):
   logout(request)
   messages.success(request, 'Logged out successfully')
   return redirect('home')

#def base(request):
    #return render(request, 'myApp/base.html')

#def navbar(request):
    #return render(request, 'myApp/navbar.html')
    
def register_user(request):  
    form = SignUpForm()
    if request.method == "POST":
     form = SignUpForm(request.POST)
     if form.is_valid():
         form.save()
         username = form.cleaned_data['username']
         password = form.cleaned_data['password1']
         #log in user
         user = authenticate(username=username, password=password)
         login(request, user)
         messages.success(request, 'username created,please fill your info below')
         return redirect('update_info')
     else:
         messages.success(request, 'error please register again')
         return redirect('register')
    else:
      return render(request, 'myApp/register.html',{'form':form})