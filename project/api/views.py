from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authentication import authenticate
from rest_framework.authtoken.models import Token
from .models import Cart, Order, Products, User
from .serializer import CartSerializer, OrderSerializer, ProductsSerializer, UserSerializer


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if email is None or password is None:
        return Response({"error": {'message': "Validation error", 'code': 422}})

    user = authenticate(email=email, password=password)

    if not user:
        return Response({'error': {'message': "Authentication failed", 'code': 401}})

    token, _ = Token.objects.get_or_create(user=user)

    return Response({'data': {'user_token': token.key}})


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response({'data': {'user_token': token.key, 'code': 201}})
    return Response({'error': serializer.errors})


@api_view(['GET'])
def logout(request):
    request.user.auth_token.delete()

    return Response({'data': {'message': 'logout', 'code': 200}})


@api_view(['GET'])
def get_prod(request):
    products = Products.objects.all()
    serializer = ProductsSerializer(products, many=True)

    return Response({'data': serializer.data, 'code': 200})


@api_view(['POST'])
def add_prod(request):
    if request.user.is_staff:
        serializer = ProductsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response({'data': {'message': "product added", 'code': 201}})
        return Response({'error': serializer.errors})
    return Response({'“error”: {“code”: 403,“message”: “Forbidden for you”}'})


@api_view(['PATCH', 'DELETE'])
def UD_prod(request, pk):
    if request.user.is_staff:
        try:
            product = Products.objects.get(pk=pk)
        except:
            return Response({'error': {'message': 'not found', 'code': 404}})
        if request.method == 'PATCH':
            serializer = ProductsSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                return Response({'data': serializer.data, 'code': 200})
            return Response({'error': serializer.errors})
        elif request.method == 'DELETE':
            product.delete()

            return Response({'data': {'message': 'product removed', 'code': 200}})
    return Response({'“error”: {“code”: 403,“message”: “Forbidden for you”}'})


@api_view(['GET'])
def get_cart(request):
    if request.user.is_active:
        if not request.user.is_staff:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            serializer = CartSerializer(cart)
            data = []
            cnt = 0
            for i in serializer.data['products']:
                cnt += 1
                data.append({
                    'id': cnt,
                    'product_id': i['id'],
                    'name': i['name'],
                    'description': i['description'],
                    'price': i['price'],
                })

            return Response({'data': data, 'code': 200})
        return Response({'“error”: {“code”: 403,“message”: “Forbidden for you”}'})
    return Response({'“error”: {“code”: 403,“message”: “Forbidden for you”}'})


@api_view(['POST', 'DELETE'])
def add_cart(request, pk):
    if request.user.is_active:
        if not request.user.is_staff:
            try:
                product = Products.objects.get(pk=pk)
            except:
                return Response({'error': {
                    'message': 'not found',
                    'code': 40000000000000000000000004}})
            if request.method == 'POST':
                cart, _ = Cart.objects.get_or_create(user=request.user)
                cart.products.add(product)

                return Response({'message': 'product added to cart', "code": 201})
            elif request.method == 'DELETE':
                cart, _ = Cart.objects.get_or_create(user=request.user)
                cart.products.remove(product)

                return Response({'message': 'product removed from cart', "code": 200})
        return Response({'“error”: {“code”: 403,“message”: “Forbidden for you”}'})
    return Response({'“error”: {“code”: 403,“message”: “Forbidden for you”}'})


@api_view(['POST', 'GET'])
def get_order(request):
    if request.user.is_active:
        if not request.user.is_staff:
            if request.method == 'GET':
                order = Order.objects.filter(user=request.user)
                serializer = OrderSerializer(order, many=True)

                return Response({'data': serializer.data, 'code': 200})
            elif request.method == 'POST':
                order = Order.objects.create(user=request.user)
                cart, _ = Cart.objects.get_or_create(user=request.user)
                price = 0
                for product in cart.products.all():
                    price += product.price
                    order.products.add(product)
                data = order.save()
                cart.delete()

        return Response({'“error”: {“code”: 403,“message”: “Forbidden for you”}'})
    return Response({'“error”: {“code”: 403,“message”: “Forbidden for you”}'})
