from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save

#customer profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(User, auto_now=True)
    phone = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    old_carty = models.CharField(max_length=200, blank=True,null=True)
    
    
    def __str__(self):
        return self.user.username
    
    #create user profile by defaulf
    
    def create_profile(sender, instance, created, **kwargs):
        if created:
            user_profile = Profile(user=instance)
            user_profile.save()
    post_save.connect(create_profile,sender=User)        



class Category(models.Model): 
    name = models.CharField(max_length=50)  # Corrected max_Length to max_length
    
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'catergories'

class Customer(models.Model):
    first_name = models.CharField(max_length=50)  # Corrected max_Length to max_length
    last_name = models.CharField(max_length=50)   # Corrected max_Length to max_length
    phone = models.CharField(max_length=50)       # Corrected max_Length to max_length
    email = models.EmailField(max_length=50)      # Corrected max_Length to max_length
    password = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Product(models.Model):
    name = models.CharField(max_length=100)  # Corrected max_Length to max_length
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=250, default='', blank=True)
    image = models.ImageField(upload_to='uploads/product/')
#add sale
is_sale = models.BooleanField(default=False)
sale_price = models.DecimalField(default=0, decimal_places=2,max_digits=6)

def __str__(self):
        return self.name


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, default=1)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=100, default='', blank=True)  # Corrected max_Length to max_length
    phone = models.CharField(max_length=20, default='', blank=True)     # Corrected max_Length to max_length
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name
