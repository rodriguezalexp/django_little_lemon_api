from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from .views import (
    CartDetailAdminView,
    CartListAdminView,
    MenuItemViewSet,
    CartViewSet,
    OrderViewSet,
    CategoryViewSet,
    #manager_users,
    #manager_user_detail,
    #delivery_crew_users,
    #delivery_crew_user_detail,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'menu-items', MenuItemViewSet, basename='menu-item')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    #path('is_manager/', is_manager, name='is_manager'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('admin/carts/', CartListAdminView.as_view(), name='cart-list-admin'),
    path('admin/carts/<int:pk>/', CartDetailAdminView.as_view(), name='cart-detail-admin'),
]
