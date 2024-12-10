from myApp.models import Product, Profile



class Cart:
  """
    def __init__(self, request):
        self.session = request.session
        
        # Get current session 
        cart = self.session.get('session_key')

        # If user is new, no session key...must create one
        if 'session_key' not in self.session:
            cart = self.session['session_key'] = {}
            
            
            #make cart available on all pages
            self.cart = cart
                 
    def __len__(self):
       return len(self.cart) 
   
   
           
         # addcart.py
 """

class Cart:
    """
    def __init__(self, request):
        
        self.session = request.session
        self.request = request
        cart = self.session.get('session_key')
        self.cart = self.session.get('cart',{})
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
            self.cart = cart
        
     """   
    
    
    
    def __init__(self, request):
     #self.cart = {}
     self.session = request.session
     self.request = request
     self.cart = self.session.get('cart', {})
     
     if 'cart' not in self.session:
         
        self.session['cart'] = self.cart
    
    
     """
    def db_add(self, product, quantity):   
        product_id = str(product)
        product_qty = str(quantity)                                  
        if product_id in self.cart:
         pass
        else:
        # self.cart[product_id] = {'price':str(product.price)}
         self.cart[product_id] = int(product_qty)
         self.session.modified = True
          #deal with logged in users
         if self.request.user.is_authenticated:
             current_user = Profile.objects.filter(user__id=self.request.user.id)
         self.session.modified = True 
        # convert '' to "" 
        carty = str(self.cart)
        carty = carty.replace("\'","\"")
         #save carty
        current_user.update(old_carty=str(carty))
        """
    def db_add(self, product, quantity=1):   
     product_id = str(product)
     product_qty = int(quantity)

    # Add product to cart
     if product_id not in self.cart:
        self.cart[product_id] = product_qty

    # Save cart to session
     self.session['cart'] = self.cart
     self.session.modified = True

    # Update logged-in user's profile
     if self.request.user.is_authenticated:
        try:
            current_user = Profile.objects.get(user=self.request.user)
            carty = str(self.cart).replace("'", "\"")
            current_user.old_carty = carty
            current_user.save()
        except Profile.DoesNotExist:
            pass
      
        
    """
    def add(self, product, quantity):
        product_id = str(product)
        product_qty = str(quantity)                                  
        if product_id in self.cart:
         pass
     
        else:
         #self.cart[product_id] = {'price':str(product.price)}
         self.cart[product_id] = int(product_qty)
         self.session.modified = True
          #deal with logged in users
         if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            self.session.modified = True 
        # convert '' to "" 
            carty = str(self.cart)
            carty = carty.replace("\'","\"")
         #save carty
            current_user.update(old_carty=str(carty))
         
         # Save the cart in the session
        #self.save()
    #def save(self):
        # Update the session cart
    """
    def add(self, product, quantity=1):
        product_id = str(product)
        product_qty = int(quantity)

        if product_id in self.cart:
            self.cart[product_id] += product_qty  # Increment quantity if exists
        else:
            self.cart[product_id] = product_qty  # Add new item

        # Save cart to session
        self.session['cart'] = self.cart
        self.session.modified = True

        # Handle logged-in users
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart).replace("'", "\"")
            current_user.update(old_carty=carty)
 
        
        
        
           
    """def cart_total(self):
     product_ids = self.cart.keys()
     products = Product.objects.filter(id__in=product_ids)
     quantities = self.cart
     total = 0
     for key, value in quantities.items():
        key = int(key)  # Ensure the key is an integer
        for product in products:
            if product.id == key:
                # Assuming value is a dictionary, get the quantity key
                quant = value.get('quant', 1)  # Default to 1 if 'quantity' is missing
                total += product.price* quant
     return total

         """     
    def cart_total(self):
     product_ids = self.cart.keys()
     products = Product.objects.filter(id__in=product_ids)
     quantities = self.cart
     total = 0

     for key, value in quantities.items():
        key = int(key)  # Ensure the key is an integer

        # Ensure `value` is a dictionary before accessing `.get()`
        if isinstance(value, dict):
            quant = value.get('quant', 1)  # Default to 1 if 'quant' is missing
        elif isinstance(value, int):  # If it's an integer, treat it as the quantity
            quant = value
        else:
            raise ValueError(f"Unexpected value type in cart: {type(value)}")

        # Match product IDs and calculate the total
        for product in products:
            if product.id == key:
                total += product.price * quant

     return total






    def __len__(self):
        # Count the total quantity of items in the cart
        return len(self.cart) 

    def get_prods(self):
        product_ids = self.cart.keys()
        products =Product.objects.filter(id__in=product_ids)
        # Return the products in the cart
        
        return products
           
    def get_quants(self):
        quantities = self.cart  
        return quantities
        #return {product_id: item['quantity'] for product_id, item in self.cart.items()}
       
    
    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)
        #get cart 
        ourcart = self.cart 
        ourcart[product_id] = product_qty
        self.session.modified = True
        
        if self.request.user.is_authenticated:
             current_user = Profile.objects.filter(user__id=self.request.user.id)
             self.session.modified = True 
        # cnvert '' to "" 
             carty = str(self.cart)
             carty = carty.replace("\'","\"")
         #save carty
             current_user.update(old_carty=str(carty))
         
        thing=self.cart 
        return thing
    
    def delete(self,product):
        product_id = str(product)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True
            if self.request.user.is_authenticated:
             current_user = Profile.objects.filter(user__id=self.request.user.id)
            self.session.modified = True 
        # cnvert '' to "" 
            carty = str(self.cart)
            carty = carty.replace("\'","\"")
         #save carty
            current_user.update(old_carty=str(carty))
         