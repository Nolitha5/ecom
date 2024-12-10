from django.urls import path
from . import views  # Import views from the current directory

urlpatterns = [
 path('',views.addcart_summary,name="addcart_summary"),  
 path('add/',views.addcart_add,name="addcart_add"),  
 path('delete/',views.addcart_delete,name="addcart_delete"), 
 path('update/',views.addcart_update,name="addcart_update"), 
]
