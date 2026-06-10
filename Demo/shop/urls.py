from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('guest/', views.guest_products_view, name='guest_products'),
    path('products/', views.product_list_view, name='product_list'),
    path('products/add/', views.product_add_view, name='product_add'),
    path('products/<int:pk>/edit/', views.product_edit_view, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete_view, name='product_delete'),
    path('products/<int:pk>/cancel/', views.product_cancel_edit_view, name='product_cancel_edit'),
    path('orders/', views.order_list_view, name='order_list'),
    path('orders/add/', views.order_add_view, name='order_add'),
    path('orders/<int:pk>/edit/', views.order_edit_view, name='order_edit'),
    path('orders/<int:pk>/delete/', views.order_delete_view, name='order_delete'),
]
