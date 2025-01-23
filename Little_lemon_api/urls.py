from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from .views import CategoriesView, MenuItemsView, CartView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'categories', CategoriesView, basename='categories')
router.register(r'menu-items', MenuItemsView, basename='menu-items')
router.register(r'cart', CartView, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    #path('is_manager/', is_manager, name='is_manager'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]

"""[
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),  # Ruta para generar token de usuario registrado
    #path('categories/', CategoryList.as_view(), name='category-list'),
    #path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'), 
    path('is_manager/', is_manager, name='is_manager'),
]"""