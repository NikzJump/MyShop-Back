from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login),
    path('signup', views.signup),
    path('logout', views.logout),
    path('prods', views.get_prod),
    path('prod', views.add_prod),
    path('prod/<int:pk>', views.UD_prod),
    path('cart', views.get_cart),
    path('cart/<int:pk>', views.add_cart),
    path('order', views.get_order),
]
