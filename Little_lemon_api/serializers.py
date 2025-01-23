from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework.validators import UniqueTogetherValidator

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title'] # por que no se incluye slug? porque no se necesita en la respuesta

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']

class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    username = serializers.CharField(source='user.username', read_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'username', 'menuitem', 'quantity', 'menuitem_id']
        
