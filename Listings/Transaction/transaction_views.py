from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from Listings.models import Business, ClientOrder, Order, Wallet
from .transaction_serializers import BusinessTransactionSerializer, ClientTransactionSerializer, WalletSerializer




class GetAllTransactionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            business_page = Business.objects.get(owner=user)
            if business_page:
                order = Order.objects.filter(user=user)
                order_serializer = BusinessTransactionSerializer(order, many=True)
        except Business.DoesNotExist:
            order = ClientOrder.objects.filter(user=user)
            order_serializer = ClientTransactionSerializer(order, many=True)

        return Response({'msg': 'All Transaction Details', 'all_transaction_data': order_serializer.data}, status=status.HTTP_200_OK)




class UserWalletAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def get(self, request):
        user = request.user
        user_wallet = Wallet.objects.filter(user=user)
        if user_wallet:
            serializer = WalletSerializer(user_wallet, many=True)
            return Response({'msg': 'Your Wallet balance fetched Successfully', 'data': serializer.data})
        return Response({'msg': 'You have not yet purchased any plan yet'})