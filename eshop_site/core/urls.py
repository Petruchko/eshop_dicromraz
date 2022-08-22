from django.urls import path
from .views import HomeView, ItemDetailView, add_to_cart, remove_from_cart, OrderSummaryView, add_quantity, minus_quantity, delete_from_order, CheckoutView, PaymentView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('add-quantity/<slug>/', add_quantity, name='add-quantity'),
    path('minus-quantity/<slug>/', minus_quantity, name='minus-quantity'),
    path('delete-from-order/<slug>/', delete_from_order, name='delete-from-order'),
    path('payment/', PaymentView.as_view(), name='payment')
]