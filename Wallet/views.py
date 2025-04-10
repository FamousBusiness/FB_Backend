from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import MatureWallet, ImmatureWallet, Transaction, UserBankAccount, Withdrawals, PhonpeWalletOrder, AddMoneyFee, TransferMoneyFee
from users.models import User
from .serializers import UserAccountBalance, UserImmatureSerializer, UserMatureSerializer, AllUserTransactionSerializer, UserBankAccountSerializer, WithDrawalSerializer
from Razorpay.serializer import RazorpayorderSerializer, RazorPayOrderCompletionSerializer
from .pagination import AllUserTransactionsPagination, CustomPagination
from django.core.cache import cache
from Razorpay.views import rz_client
from uuid import uuid4
from django.utils.timezone import now
from datetime import timedelta, datetime
from Phonepe.payment import AddMoneyPhonepayPayment
from django.views.decorators.csrf import csrf_exempt
from Phonepe.encoded import base64_decode




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
        
        ### Get all the withdrawal requests of the user
        try:
            user_withdrawal_requests = Withdrawals.objects.filter(
                                                        user         = user, 
                                                        is_completed = True
                                                    )
        except Exception as e:
            return Response({'message': 'Unable to get withdrawals of user'}, status=status.HTTP_400_BAD_REQUEST)
        
        all_withdrawal_amount = sum(withdrawal_requests.amount for withdrawal_requests in user_withdrawal_requests)

        user_mature_serializer   = UserMatureSerializer(user_mature_wallet)
        user_immature_serializer = UserImmatureSerializer(user_immature_wallet)
        
        return Response({
            'message': 'Wallet data fetched Successfully',
            'user_mature_wallet': user_mature_serializer.data,
            'user_immature_serializer': user_immature_serializer.data,
            'withdrawal_amount': all_withdrawal_amount

        }, status=status.HTTP_200_OK)




### Update Wallet Balance of the User and Create a Transaction
class UpdateWalletBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    
    def post(self, request):
        user = request.user
        amount = request.data.get('amount')

        if not amount:
            return Response({'message': 'Amount field is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        unique_id = str(uuid4())[:35]

        #### Create phonepe order to save all the data
        try:
            phonepe_order = PhonpeWalletOrder.objects.create(
                user           = user,
                amount         = int(amount),
                transaction_id = unique_id,
                purpose        = 'Add Money'
            )

            phonepe_order.save()

        except Exception as e:
            return Response({'message':'Unable to create phonepe order'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment  = AddMoneyPhonepayPayment(amount, unique_id)
        except Exception as e:
            return Response({'message': 'Unable to raise payment request', 'error': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        

        return Response({
            'message': 'Payment request raised successfully',
            'url': payment
        }, status=status.HTTP_200_OK)
        

    
    ### Currenctly not in use right Now(Only for Razorpay payment)
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
                status         = 'Pending',
                mode           = 'Add'
            )

            create_transaction.save()

        except Exception as e:
            return Response({'error': f"{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(response, status=status.HTTP_200_OK)
        


#### Phonepe payment Response
class AddMoneyPhonepePaymentResponseView(APIView):
    permission_classes = [permissions.AllowAny]
    
    
    @csrf_exempt
    def post(self, request):
        response_data = request.data.get('response')
        decoded_data  = base64_decode(response_data)
        
        
        if (
            decoded_data['success'] == True and 
            decoded_data['code'] == 'PAYMENT_SUCCESS' and 
            decoded_data['message'] == 'Your request has been successfully completed.'
            ):

            #### Get the transaction ID from response
            transaction_id = decoded_data['data']['merchantTransactionId']

            #### Get the phonepe order
            try:
                phonepe_order                 = PhonpeWalletOrder.objects.get(transaction_id = transaction_id)
                phonepe_order.phoepe_response = str(decoded_data)

                phonepe_order.save()

            except Exception as e:
                return Response({'message': 'Unable to get transaction Id'}, status=status.HTTP_400_BAD_REQUEST)
            
            ### Get The wallet of the 
            try:
                user_wallet = MatureWallet.objects.get(user = phonepe_order.user)

                if user_wallet:
                    user_wallet.balance += int(phonepe_order.amount)
                    user_wallet.save()

            except Exception as e:
                return Response({'message': 'Unable to get the User Wallet'}, status=status.HTTP_400_BAD_REQUEST)
            

            # Unique Transaction ID
            transaction_ID = f'TR_{str(uuid4())[:28]}'

            ## Create a Transactio for the user
            try:
                create_transaction = Transaction.objects.create(
                    user           = phonepe_order.user,
                    transaction_id = transaction_ID,
                    amount         = phonepe_order.amount,
                    status         = 'Success',
                    mode           = 'Add'
                )

                #### Get all the Add money Fees
                try:
                    add_money_fees = AddMoneyFee.objects.all()

                    if add_money_fees:
                        create_transaction.ad_money_fee.set(add_money_fees)

                except Exception as e:
                    pass

                create_transaction.save()

            except Exception as e:
                return Response({'error': f"{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            
            return Response({'success': True}, status=status.HTTP_200_OK)




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
            user_transactions = Transaction.objects.filter(user=user).prefetch_related(
                'ad_money_fee', 'transfer_fee', 'cod_fee', 'prepaid_fee'
            ).select_related('user', 'receiver').order_by('-date_created')

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
        
        #### Deduct amount
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

            try:
                transfer_money = TransferMoneyFee.objects.all()

                if transfer_money:
                    transaction.transfer_fee.set(transfer_money)

            except Exception as e:
                pass

            transaction.save()

        except Exception as e:
            return Response({
                'message': 'Unable to create Transaction'
            }, status=status.HTTP_400_BAD_REQUEST)


        return Response({
            'message': 'Amount successfullt transferred'
        }, status=status.HTTP_200_OK)
    




##### Recent Transaction View
class RecentTransactions(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    
    def get(self, request):
        user = request.user

        ### Get 10 transactions of the user
        try:
            all_user_transactions = Transaction.objects.filter(user = user)[:8]
        except Exception as e:
            return Response({'message': 'All user transactions'}, status=status.HTTP_400_BAD_REQUEST)
        
        serilizer = AllUserTransactionSerializer(all_user_transactions, many=True)

        return Response({
            'message': 'Recent Transacion fetched successfully',
            'recent_transaction': serilizer.data

        }, status=status.HTTP_200_OK)
    


#### Export all users Transactions
class ExportTransactionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]


    def get(self, request):
        user = request.user

        ### Get all the Transactions of the user
        try:
            user_transactions = Transaction.objects.filter(user = user)
        except Exception as e:
            return Response({'message': 'Unable to get user transactions'}, status=status.HTTP_400_BAD_REQUEST)
        
        response_data = [{
            'Transaction ID': transaction.transaction_id,
            'Date': transaction.date_created,
            'amount': transaction.amount,
            'Mode': transaction.mode,
            'Status': transaction.status,
            'Receiver': transaction.receiver.name if transaction.receiver else None

        } for transaction in user_transactions] 


        return Response({
            'message': 'All transaction data exported successfully',
            'export_transactions': response_data

        }, status=status.HTTP_200_OK)
    



#### Filter user transactions
class FilterUserTransactionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = AllUserTransactionsPagination


    def post(self, request):
        user = request.user

        date               = request.data.get('date')
        transaction_id     = request.data.get('transaction_id')
        transaction_mode   = request.data.get('mode')
        transaction_status = request.data.get('status')
        start_date         = request.data.get('start_date')
        end_date           = request.data.get('end_date')

        transactions = Transaction.objects.all()

        if date:
            today = now().date()

            if date == 'Today':
                transactions = transactions.filter(date_created__date=today, user = user)

            elif date == 'Yesterday':
                yesterday = today - timedelta(days=1)
                transactions = transactions.filter(date_created__date=yesterday, user = user)

            elif date == 'ThisWeek':
                start_of_week = today - timedelta(days=today.weekday())
                transactions  = transactions.filter(date_created__date__gte=start_of_week, user = user)

            elif date == 'ThisMonth':
                transactions = transactions.filter(
                        date_created__month=today.month, 
                        date_created__year=today.year,
                        user = user
                    )

            elif date == "PreviousMonth":
                first_day_of_current_month = today.replace(day=1)
                last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)

                transactions = transactions.filter(
                        date_created__month = last_day_of_previous_month.month,
                        date_created__year  = last_day_of_previous_month.year,
                        user = user
                    )
            
            elif date == 'CustomRange':
                if start_date and end_date:
                    try:
                        start_date   = datetime.strptime(start_date, "%Y-%m-%d").date()
                        end_date     = datetime.strptime(end_date, "%Y-%m-%d").date()
                        transactions = transactions.filter(
                                date_created__date__range = (start_date, end_date),
                                user = user
                            )
                    except ValueError:
                        pass

        
        if transaction_id:
            transactions = transactions.filter(transaction_id__icontains=transaction_id)

        if transaction_mode:
            transactions = transactions.filter(mode=transaction_mode)

        if transaction_status:
            transactions = transactions.filter(status=transaction_status)

        paginator = self.pagination_class()
        paginated_transaction = paginator.paginate_queryset(transactions, request)

        serializer = AllUserTransactionSerializer(paginated_transaction, many=True)

        response_data = paginator.get_paginated_response({
            'success': True,
            'filtered_data': serializer.data
        }).data

        return Response(response_data, status=status.HTTP_200_OK)




#### Filter Withdrawal Requests
class FilterWithDrawalView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = WithDrawalSerializer
    pagination_class   = CustomPagination


    def post(self, request):
        user = request.user

        date               = request.data.get('date')
        bank_name          = request.data.get('bank_name')
        amount             = request.data.get('amount')
        transaction_status = request.data.get('status')
        start_date         = request.data.get('start_date')
        end_date           = request.data.get('end_date')

        all_withdrawals = Withdrawals.objects.all()
    
        #### Date wise filter
        if date:
            today = now().date()

            if date == 'Today':
                all_withdrawals = all_withdrawals.filter(date_created__date=today, user = user)

            elif date == 'Yesterday':
                yesterday = today - timedelta(days=1)
                all_withdrawals = all_withdrawals.filter(date_created__date=yesterday, user = user)

            elif date == 'ThisWeek':
                start_of_week = today - timedelta(days=today.weekday())
                all_withdrawals  = all_withdrawals.filter(date_created__date__gte=start_of_week, user = user)

            elif date == 'ThisMonth':
                all_withdrawals = all_withdrawals.filter(
                        date_created__month=today.month, 
                        date_created__year=today.year,
                        user = user
                    )

            elif date == "PreviousMonth":
                first_day_of_current_month = today.replace(day=1)
                last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)

                all_withdrawals = all_withdrawals.filter(
                        date_created__month = last_day_of_previous_month.month,
                        date_created__year  = last_day_of_previous_month.year,
                        user = user
                    )
            
            elif date == 'CustomRange':
                if start_date and end_date:
                    try:
                        start_date   = datetime.strptime(start_date, "%Y-%m-%d").date()
                        end_date     = datetime.strptime(end_date, "%Y-%m-%d").date()
                        all_withdrawals = all_withdrawals.filter(
                                date_created__date__range = (start_date, end_date),
                                user = user
                            )
                    except ValueError:
                        pass
        
        #### Bank name wise filter
        if bank_name:
            try:
                
                all_withdrawals = all_withdrawals.filter(
                    user = user,
                    bank__bank_name = bank_name
                )
            except Exception as e:
                return Response({'error': f'{str(e)}'})

        
        ##### Status wise filter
        if transaction_status:
            try:
                all_withdrawals = all_withdrawals.filter(status = transaction_status)
            except Exception as e:
                pass
        
        
        #### Amount wise filter
        if amount:
            try:
                all_withdrawals = all_withdrawals.filter(amount = amount)
            except Exception as e:
                pass

        paginator             = self.pagination_class()
        paginated_withdrawals = paginator.paginate_queryset(all_withdrawals, request)

        serializer            = self.serializer_class(paginated_withdrawals, many=True)

        return paginator.get_paginated_response(serializer.data)
    



#### Export all Withdrawal Requests
class ExportWithdrawalView(APIView):
    permission_classes = [permissions.IsAuthenticated]


    def get(self, request):
        user = request.user

        try:
            user_withdrawals = Withdrawals.objects.filter(
                user = user
            )
        except Exception as e:
            return Response({'message': 'Withdrawal requests not found'}, status=status.HTTP_400_BAD_REQUEST)

        response_data = [{
            'Bank Name': withdrawal.bank.bank_name,
            'Account Number': withdrawal.bank.acc_number,
            'IFSC Code': withdrawal.bank.ifsc_code,
            'Withdrawal Amount': withdrawal.amount,
            'Date': withdrawal.date_created,
            'Status': withdrawal.status

        } for withdrawal in user_withdrawals]

        
        return Response(response_data, status=status.HTTP_200_OK)

        


    




    





        





    


    

        
    
    


        



