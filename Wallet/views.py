from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import MatureWallet, ImmatureWallet, Transaction, UserBankAccount, Withdrawals
from users.models import User
from .serializers import UserAccountBalance, UserImmatureSerializer, UserMatureSerializer, AllUserTransactionSerializer, UserBankAccountSerializer, WithDrawalSerializer
from Razorpay.serializer import RazorpayorderSerializer, RazorPayOrderCompletionSerializer
from .pagination import AllUserTransactionsPagination, CustomPagination
from django.core.cache import cache
from Razorpay.views import rz_client
from uuid import uuid4




### User Wallet Balance
class UserWalletBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request): 
        user = request.user


        try:
            mature_wallet, created = MatureWallet.objects.get_or_create(user = user)
        except Exception as e:
            return Response({'message': 'User wallet not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            immature_wallet, created = ImmatureWallet.objects.get_or_create(user = user)
        except Exception as e:
            return Response({'message': 'User wallet not found'}, status=status.HTTP_404_NOT_FOUND)
        
        total_availabe_user_balance = mature_wallet.balance + immature_wallet.balance
        
        serializer = UserAccountBalance({
            'balance': total_availabe_user_balance,
            'mature_balance': mature_wallet.balance,
            'immature_wallet': immature_wallet.balance
        })

        return Response({
            'message': 'Wallet data fetched Successfully',
            'user_wallet_balance': serializer.data
            
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

        user_mature_serializer   = UserMatureSerializer(user_mature_wallet)
        user_immature_serializer = UserImmatureSerializer(user_immature_wallet)
        
        return Response({
            'message': 'Wallet data fetched Successfully',
            'user_mature_wallet': user_mature_serializer.data,
            'user_immature_serializer': user_immature_serializer.data

        }, status=status.HTTP_200_OK)




### Update Wallet Balance of the User and Create a Transaction
class UpdateWalletBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    
    def post(self, request):
        razorpay_order_serializer = RazorpayorderSerializer(data = request.data)

        if razorpay_order_serializer.is_valid():
            amount = razorpay_order_serializer.validated_data.get('amount')
            
            order_response = rz_client.create_order(
                amount = amount
            )

            response = {
                'status': status.HTTP_201_CREATED,
                'message': 'Order Created',
                'data': order_response
            }

            return Response(response, status=status.HTTP_201_CREATED)

        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "bad request",
                "error": razorpay_order_serializer.errors
            }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
    

    def put(self, request):
        user   = request.user
        amount = request.data.get('amount')
        order_serializer = RazorPayOrderCompletionSerializer(data = request.data)

        if not amount:
            return Response({'message': 'Please provide amount'}, status=status.HTTP_400_BAD_REQUEST)

        order_serializer.is_valid(raise_exception=True)

        order_id     = order_serializer.validated_data.get('provider_order_id')
        payment_id   = order_serializer.validated_data.get('payment_id')
        signature_id = order_serializer.validated_data.get('signature_id')
        
        
        ### Razorpay payment Varification
        try:
            rz_client.verify_payment_signature(
                razorpay_order_id   = order_id,
                razorpay_payment_id = payment_id,
                razorpay_signature  = signature_id
            )

        except Exception as e:
            response_data = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Payment signature verification failed",
                "error": str(e) 
            }

            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        response = {
            "status_code": status.HTTP_201_CREATED,
            "message": "transaction created"
        }


        ### Get The wallet of the 
        try:
            user_wallet = MatureWallet.objects.get(user = user)
        except Exception as e:
            return Response({'message': 'Unable to get the User Wallet'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user_wallet:
            user_wallet.balance += int(amount)
            user_wallet.save()

        # Unique Transaction ID
        transaction_ID = f'TR_{str(uuid4())[:28]}'

        ## Create a Transactio for the user
        try:
            create_transaction = Transaction.objects.create(
                user           = user,
                transaction_id = transaction_ID,
                amount         = amount,
                status         = 'Success',
                mode           = 'Add'
            )

            create_transaction.save()

        except Exception as e:
            return Response({'error': f"{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(response, status=status.HTTP_200_OK)
        



#### Get all Transactions of the User
class AllUserTransactionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = AllUserTransactionsPagination


    def get(self, request):
        user = request.user

        # page = request.query_params.get('page', 1)
        # cache_key = f"user_wallet_transactions_{user.id}_page_{page}"

        # cached_data = cache.get(cache_key)

        # if cached_data:
        #     return Response(cached_data, status=status.HTTP_200_OK)

        ### Get all the transactions of the user
        try:
            user_transactions = Transaction.objects.filter(
                user = user
            ).order_by('-date_created')
        except Exception as e:
            return Response({
                'message': 'Unable to get user transactions',
                'error': f'{str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        
        paginator              = self.pagination_class()
        paginated_transactions = paginator.paginate_queryset(user_transactions, request)

        serializer = AllUserTransactionSerializer(paginated_transactions, many=True)

        response_data = paginator.get_paginated_response({
            'success': True,
            'all_user_transactions': serializer.data
        }).data

        # Store the response in Redis cache for 5 Minute
        # cache.set(cache_key, response_data, timeout=60 * 5)

        return Response(response_data, status=status.HTTP_200_OK)
    



### Back Account View
class UserBankAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]


    ### Get all users Bank Account
    def get(self, request):
        user = request.user
        
        ### Get all available bank accounts of the user
        try:
            user_bank_account = UserBankAccount.objects.filter(
                user = user
            )
        except Exception as e:
            return Response({
                'message': 'Unable to get the transactions',
                'error': f'{str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serilizer = UserBankAccountSerializer(user_bank_account, many=True)


        return Response({
            'message': 'Bank account fetched successfully',
            'user_bank_account': serilizer.data

        }, status=status.HTTP_200_OK)
    

    ### Create new bank account
    def post(self, request): 
        user = request.user

        serializer = UserBankAccountSerializer(data = request.data, context={"user": user})

        serializer.is_valid(raise_exception=True)

        ##### Bank Account
        try:
            existing_bank = UserBankAccount.objects.get(acc_number = serializer.validated_data.get('acc_number'))

            #### If Bank account exists
            if existing_bank:
                return Response({
                    'message': 'Bank Account already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            pass

        
        ### Create New Bank Account of user
        try:
            serializer.save()

        except Exception as e:
            return Response({
                'error': f'{str(e)}',
                'message': 'Unable to save the users bank account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        
        return Response({
            'message': 'Bank Account Created Successfully'
        }, status=status.HTTP_200_OK)
    
    

    #### Update Bank Account
    def put(self, request): 
        user = request.user

        bank_id  = request.data.get('bank_id')
        bank_doc = request.FILES.get('doc')

        if not bank_id:
            return Response({'message': 'bank_id not present'}, status=status.HTTP_400_BAD_REQUEST)
        
        ### Get the users Bank account
        try:
            user_bank = UserBankAccount.objects.get(id = int(bank_id))
        except Exception as e:
            return Response({'message': 'Unable to get bank account', 'error': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        updated_data = request.data.copy()

        if not bank_doc:
            updated_data['doc'] = user_bank.doc

        serializer = UserBankAccountSerializer(user_bank, data = updated_data, context={"user": user}, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({
            'message': 'Bank Account Updated Successfully'
        }, status=status.HTTP_200_OK)
    
    

    #### Delete bank account by the user
    def delete(self, request):
        user    = request.user
        bank_id = request.query_params.get('bank_id')

        if not bank_id:
            return Response({'message': 'bank_id field required'}, status=status.HTTP_400_BAD_REQUEST)
        
        ### Get the bank account of the user
        try:
            user_bank = UserBankAccount.objects.get(id = int(bank_id))

        except Exception as e:
            return Response({
                'message': 'Unable to get Bank account'
            }, status=status.HTTP_400_BAD_REQUEST)
        

        if user_bank.user == user:
            user_bank.delete()

        else:
            return Response({'message': 'Unauthenticated Access'}, status=status.HTTP_400_BAD_REQUEST)
        

        return Response({"message": "Bank account deleted successfully"}, status=status.HTTP_200_OK)

        


#### User Withdrawal API VIEW
class UserWithdrawalAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = WithDrawalSerializer
    pagination_class   = CustomPagination


    ### Get all Withdrawal requests of user
    def get(self, request):
        user = request.user
        
        try:
            user_withdrawals = Withdrawals.objects.filter(user = user)
        except Exception as e:
            return Response({'message': 'Unable to get users withdrawal data'}, status=status.HTTP_400_BAD_REQUEST)

        paginator = self.pagination_class()
        paginated_withdrawals = paginator.paginate_queryset(user_withdrawals, request)

        serializer = self.serializer_class(paginated_withdrawals, many=True)

        return paginator.get_paginated_response(serializer.data)
    

    
    #### Create new withdrawal request for the user
    def post(self, request):
        user = request.user

        amount = request.data.get('amount')
        bank_id = request.data.get('bank_id')

        reference_id = str(uuid4())[:30]

        if not amount or not bank_id:
            return Response({'message': 'Missing payload fields'}, status.HTTP_400_BAD_REQUEST)
        
        ### Get user bank account
        try:
            user_bank_account = UserBankAccount.objects.get(id = int(bank_id), user = user)
        except Exception as e:
            return Response({'message': 'Invalid bank ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_mature_wallet = MatureWallet.objects.get(user=user)

            if int(amount) > user_mature_wallet.balance:
                return Response({'message': 'Insufficient funds in Wallet'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'message':'Unable to locate user Wallet'}, status=status.HTTP_404_NOT_FOUND)
        

        try:
            create_withdrawal_request = Withdrawals.objects.create(
                user         = user,
                amount       = int(amount),
                reference_id = reference_id,
                bank         = user_bank_account,
                status       = 'Pending',
                is_completed = False
            )

            create_withdrawal_request.save()

        except Exception as e:
            return Response({'message': 'Unable to create withdrawal Request'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': 'Withdrawal Request raised successfully',
            'success': True
        }, status=status.HTTP_200_OK)




#### Transafer Money
class TransferMoneyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    
    def post(self, request):
        user     = request.user
        amount   = request.data.get('amount')
        receiver = request.data.get('receiver_id')

        if not amount or not receiver:
            return Response({
                'message': 'missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #### Get the receiver
        try:
            receiver_user = User.objects.get(id = int(receiver))
        except Exception as e:
            return Response({'message': 'Invalid Receiver'}, status=status.HTTP_404_NOT_FOUND)
        
        unique_id = f'TR_{str(uuid4())[:28]}'

        if receiver_user.pk == user.pk:
            return Response({'message': 'Can not transfer to self'}, status=status.HTTP_400_BAD_REQUEST)
        
        #### Fetch user mature wallet
        try:
            user_mature_balance = MatureWallet.objects.get(user = user)
        except Exception as e:
            return Response({
                'message': 'Invalid Wallet of user'
            }, status=status.HTTP_404_NOT_FOUND)
        

        #### Fetch Receiver Wallet Balance
        try:
            receiver_wallet, created = MatureWallet.objects.get_or_create(user = receiver_user)
        except Exception as e:
            return Response({
                'message': 'Reciver Wallet not found',
                'error': f'{str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        
        #### Insufficient balance in wallet
        if user_mature_balance.balance < int(amount):
            return Response({'message': 'Insufficient funds in Account'}, status=status.HTTP_400_BAD_REQUEST)
        
        #### Deduct amount from 
        if user_mature_balance.balance >= int(amount):
            user_mature_balance.balance -= int(amount)
            receiver_wallet.balance += int(amount)

            user_mature_balance.save()
            receiver_wallet.save()
        
        else:
            return Response({'message': 'Unable to deduct amount'}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            #### Create a Transfer Transaction
            transaction = Transaction.objects.create(
                user           = user,
                transaction_id = unique_id,
                amount         = int(amount),
                status         = 'Success',
                is_completed   = True,
                mode           = 'Transfer',
                receiver       = receiver_user
            )
            transaction.save()

        except Exception as e:
            return Response({
                'message': 'Unable to create Transaction'
            }, status=status.HTTP_400_BAD_REQUEST)


        return Response({
            'message': 'Amount successfullt transferred'
        }, status=status.HTTP_200_OK)



        





    


    

        
    
    


        



