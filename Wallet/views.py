from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from .models import Wallet, MatureWallet, ImmatureWallet
from .serializers import UserWalletSerializer, UserImmatureSerializer, UserMatureSerializer




### User Wallet Balance
class UserWalletBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request): 
        user = request.user

        #### Get the available balance of the user
        try:
            user_wallet, created = Wallet.objects.get_or_create(user = user)
        except Exception as e:
            return Response({'message': 'User wallet not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserWalletSerializer(user_wallet)

        return Response({
            'message': 'Wallet data fetched Successfully',
            'user_wallet': serializer.data
            
        }, status=status.HTTP_200_OK)
    



#### Get users mature and Immature balance
class UserMatureImmatureWallet(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user

        try:
            user_mature_wallet, created = MatureWallet.objects.get_or_create(user = user)
        except Exception as e:
            return Response({'message': 'Not able to get user Mature Wallet'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_immature_wallet, created = ImmatureWallet.objects.get_or_create(user = user)
        except Exception as e:
            return Response({'message': 'Not able to get the user Immature Wallet'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_mature_serializer = UserMatureSerializer(user_mature_wallet)
        user_immature_serializer = UserImmatureSerializer(user_immature_wallet)
        
        return Response({
            'message': 'Wallet data fetched Successfully',
            'user_mature_wallet': user_mature_serializer.data,
            'user_immature_serializer': user_immature_serializer.data

        }, status=status.HTTP_200_OK)

        



