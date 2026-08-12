from myApp.models import Product, Profile
import json


class Cart:

    def __init__(self, request):
        self.session = request.session
        self.request = request
        self.cart = self.session.get('cart', {})
        if 'cart' not in self.session:
            self.session['cart'] = self.cart

    def __len__(self):
        # Total number of distinct products
        return len(self.cart)

    def total_quantity(self):
        # Sum of all item quantities — used for navbar badge
        return sum(self.cart.values())

    def get_prods(self):
        product_ids = self.cart.keys()
        return Product.objects.filter(id__in=product_ids)

    def get_quants(self):
        return self.cart

    def add(self, product, quantity=1):
        product_id = str(product)
        quantity = int(quantity)
        if product_id in self.cart:
            self.cart[product_id] += quantity
        else:
            self.cart[product_id] = quantity
        self._save()

    def db_add(self, product, quantity=1):
        product_id = str(product)
        quantity = int(quantity)
        if product_id not in self.cart:
            self.cart[product_id] = quantity
        self._save()

    def update(self, product, quantity):
        product_id = str(product)
        quantity = int(quantity)
        if quantity <= 0:
            self.delete(product)
            return
        self.cart[product_id] = quantity
        self._save()

    def delete(self, product):
        product_id = str(product)
        if product_id in self.cart:
            del self.cart[product_id]
            self._save()

    def cart_total(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        total = 0
        for product in products:
            qty = self.cart.get(str(product.id), 0)
            total += product.price * qty
        return total

    def _save(self):
        self.session['cart'] = self.cart
        self.session.modified = True
        if self.request.user.is_authenticated:
            try:
                current_user = Profile.objects.get(user=self.request.user)
                carty = json.dumps(self.cart)
                current_user.old_carty = carty
                current_user.save()
            except Profile.DoesNotExist:
                pass
