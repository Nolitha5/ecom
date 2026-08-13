from django.urls import path
from . import views

urlpatterns = [
    path("checkout", views.checkout, name="checkout"),
    path("billing_info", views.billing_info, name="billing_info"),
    path("process_order", views.process_order, name="process_order"),
    path("payment_success/<int:pk>", views.payment_success, name="payment_success"),
    path("shipped_dash", views.shipped_dash, name="shipped_dash"),
    path("not_shipped_dash", views.not_shipped_dash, name="not_shipped_dash"),
    path("orders/<int:pk>", views.orders, name="orders"),
    # Customer
    path("my-orders", views.my_orders, name="my_orders"),
    path("my-orders/<int:pk>", views.my_order_detail, name="my_order_detail"),
    path("track", views.track_order, name="track_order"),
]
