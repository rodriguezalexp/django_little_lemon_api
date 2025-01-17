from requests import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view # this is a decorator that takes a function and turns it into an API view

@api_view()
@permission_classes([IsAuthenticated])
def secret_page(request):
    return Response({"message": "This is a secret message!"})