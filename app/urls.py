from django.urls import path

from . import views

urlpatterns = [
    path('contact/', views.contact_view, name='contact'),
    path('', views.index_view, name='index'), 
    path('product/', views.product_list_view, name='product'),
    path('product-detail/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('shoping-cart/', views.shopping_cart_view, name='shopping_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('special-tags/', views.special_tags_view, name='special_tags'),
]
