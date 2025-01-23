from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http import request
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view # this is a decorator that takes a function and turns it into an API view
from django.contrib.auth.models import User, Group
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import Category, MenuItem, Cart
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer


"""@api_view()
@permission_classes([IsAuthenticated])
def secret_page(request):
    return Response({"message": "This is a secret message!"})


# view for add user to group
@api_view()
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers.user_set.add(user)
        return Response({"message": "OK"})
    return Response({"message": "Error"}, status.HTTP_400_BAD_REQUEST) 

# get and post view for managers group    
@api_view()
@permission_classes([IsAuthenticated, IsAdminUser])
def manager_view(request):
    if request.method == 'GET':
        managers = Group.objects.get(name='managers')
        users = managers.user_set.all()
        return Response([{"username": user.username} for user in users])
    if request.method == 'POST':
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers.user_set.add(user)
            return Response({"message": "OK"})
        return Response({"message": "Error"}, status.HTTP_400_BAD_REQUEST)

# review if the user is in the group
@api_view()
@permission_classes([IsAuthenticated])
def is_manager(request):
    managers = Group.objects.get(name='Manager')
    if request.user in User.objects.filter(groups=managers):
        return Response({"message": "yes"})
    else:
        return Response({"message": "no"})"""

class CategoriesView(ModelViewSet):
    http_method_names = ['get', 'put', 'patch', 'head', 'options', 'trace', 'delete']
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    

class MenuItemsView(ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    #permission_classes = [IsAuthenticated]
    

class CartView(ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        if request.method == 'POST':
            menuitem_id = request.data['menuitem_id']
            quantity = request.data['quantity']
            menuitem = get_object_or_404(MenuItem, id=menuitem_id)
            cart, created = Cart.objects.get_or_create(user=request.user, menuitem=menuitem, defaults={'quantity': quantity, 'unit_price': menuitem.price, 'price': menuitem.price})
            if not created:
                cart.quantity += quantity
                cart.price += quantity * menuitem.price
                cart.save()
            return Response({"message": "OK"})
    

    


# ruta http://localhost:8000/api/api-token-auth/
# http://localhost:8000/api/groups/manager/users/
