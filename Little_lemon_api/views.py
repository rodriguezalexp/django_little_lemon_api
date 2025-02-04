from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http import request
from rest_framework.decorators import permission_classes, api_view
from rest_framework import permissions, generics # this is a decorator that takes a function and turns it into an API view
from django.contrib.auth.models import User, Group
from rest_framework import status, generics
from rest_framework.viewsets import ModelViewSet
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .permissions import IsManager, IsDeliveryCrew

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated | IsManager]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated | IsManager]
        else:
            permission_classes = [IsManager]
        return [perm() for perm in permission_classes]

class MenuItemViewSet(ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated | IsDeliveryCrew | IsManager]
        else:
            permission_classes = [IsManager]
        return [perm() for perm in permission_classes]

@api_view(['GET', 'POST'])
@permission_classes([IsManager])
def manager_users(request):
    if request.method == 'GET':
        managers = User.objects.filter(groups__name='Manager')
        return Response({'managers': [user.username for user in managers]})
    
    elif request.method == 'POST':
        username = request.data.get('username')
        user = User.objects.get(username=username)
        manager_group = Group.objects.get(name='Manager')
        user.groups.add(manager_group)
        return Response({'message': 'User added to Manager group'}, status=201)

@api_view(['DELETE'])
@permission_classes([IsManager])
def manager_user_detail(request, userId):
    user = User.objects.get(id=userId)
    manager_group = Group.objects.get(name='Manager')
    user.groups.remove(manager_group)
    return Response({'message': 'User removed from Manager group'})

class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=204)
# Repite lo mismo para Delivery Crew cambiando el nombre del grupo

class CartListAdminView(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAdminUser]  # Solo accesible por administradores

class CartDetailAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAdminUser]  # Solo accesible por administradores

class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated | IsManager | IsDeliveryCrew]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=user)
        else:
            return Order.objects.filter(user=user)

    def create(self, request):
        # Lógica para crear una orden desde el carrito
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items:
            return Response({'error': 'Cart is empty'}, status=400)
        
        order = Order.objects.create(
            user=request.user,
            total=sum(item.price for item in cart_items)
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                price=item.price
            )
        
        cart_items.delete()
        return Response(OrderSerializer(order).data, status=201)

    def partial_update(self, request, pk=None):
        order = self.get_object()
        if request.user.groups.filter(name='Delivery Crew').exists():
            if 'status' in request.data and len(request.data) == 1:
                order.status = request.data['status']
                order.save()
                return Response({'message': 'Status updated'})
            else:
                return Response({'error': 'Solo puede actualizar el estado'}, status=403)
        elif request.user.groups.filter(name='Manager').exists():
            # Lógica para actualizar delivery_crew y status
            return super().partial_update(request, pk)
        else:
            return Response({'error': 'No tienes permiso'}, status=403)
    
# ruta http://localhost:8000/api/api-token-auth/
# http://localhost:8000/api/groups/manager/users/
