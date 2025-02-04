from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User, Group
from django.db import transaction

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title'] # por que no se incluye slug? porque no se necesita en la respuesta
# como se relacionan esos datos? se relacionan por el id de la categoria
class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True) # se pone write_only porque no se necesita en la respuesta
    category = CategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id'] # fields son los campos que se van a serializar

        
class CartSerializer(serializers.ModelSerializer):
    
    #definicion de los campos que se van a serializar
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    ) # por que user? porque es el usuario que esta logueado
    username = serializers.CharField(source='user.username', read_only=True)
    menuitem = MenuItemSerializer(read_only=True)  # Para detalles del menú
    menuitem_id = serializers.IntegerField(write_only=True)  # Solo escritura para el ID del menú
    unit_price = serializers.SerializerMethodField(read_only=True)  # Calculado dinámicamente
    price = serializers.SerializerMethodField(read_only=True)  # Calculado dinámicamente

    #metaclase para definir el modelo y los campos que se van a serializar
    class Meta:
        model = Cart
        fields = ['id', 'user', 'username', 'menuitem', 'quantity', 'menuitem_id', 'unit_price', 'price']

    # obtiene el precio del menu relacionado
    def get_unit_price(self, obj):
        # Obtiene el precio del menú relacionado
        return obj.menuitem.price
    
    def get_price(self, obj):
        # Obtiene el precio total del ítem en el carrito
        return obj.quantity * obj.menuitem.price

    # valida si el menuitem_id existe, se ejecuta antes de crear el objeto
    def validate(self, attrs):
        # Valida si el `menuitem_id` existe
        menuitem_id = attrs.get('menuitem_id')
        if not MenuItem.objects.filter(id=menuitem_id).exists():
            raise serializers.ValidationError({"menuitem_id": "El ítem del menú no existe."})
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user # context es un diccionario que se pasa al serializador
        menuitem_id = validated_data.pop('menuitem_id') # Elimina el campo menuitem_id del diccionario
        quantity = validated_data.get('quantity', 1) # Si no se especifica la cantidad, se asume 1
        menuitem = MenuItem.objects.get(id=menuitem_id)
        
        # validated_data es un diccionario con los datos validados del objeto a crear

        # Verificar si el ítem ya existe en el carrito del usuario
        cart_item, created = Cart.objects.get_or_create( # get or create devuelve una tupla
            user=user,
            menuitem_id=menuitem_id, # condiciones de busqueda
            defaults={'quantity': quantity,
                      'unit_price': menuitem.price,
                      'price': menuitem.price * quantity} # si no existe, crea un nuevo item con la cantidad
        )
        if not created: # si created esta en false es porque ya existe el item en el carrito
            # Si ya existe, actualiza la cantidad
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem_name = serializers.CharField(source='menuitem.title', read_only=True)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'menuitem',
            'menuitem_name',
            'quantity',
            'unit_price',
            'price'
        ]
        extra_kwargs = {
            'menuitem': {'read_only': True}
        }

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        source='orderitem_set',
        read_only=True
    )
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, 
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'delivery_crew',
            'status',
            'total', # de donde sale este total? se calcula en el metodo create
            'date',
            'items'
        ]
        read_only_fields = [
            'user',
            'total',
            'date',
            'items'
        ]

    def validate(self, attrs):
        """Validación adicional para asegurar que el carrito no esté vacío"""
        user = self.context['request'].user
        if not Cart.objects.filter(user=user).exists():
            raise serializers.ValidationError("No se puede crear una orden: El carrito está vacío.")
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user

        with transaction.atomic():
            # Bloquear los items del carrito para evitar modificaciones concurrentes
            cart_items = Cart.objects.select_for_update().filter(user=user)

            # Crear la orden
            order = Order.objects.create(
                user=user,
                total=sum(item.price for item in cart_items),
                status=False
            )

            # Crear items de la orden
            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    menuitem=item.menuitem,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    price=item.price
                ) for item in cart_items
            ])

            # Vaciar carrito
            cart_items.delete()

        return order
