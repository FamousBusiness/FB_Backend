from rest_framework import serializers
from .models import MatureWallet, ImmatureWallet, Transaction, UserBankAccount, Withdrawals
from users.models import User



#### User Wallet Balance Serializer
class UserAccountBalance(serializers.Serializer):
    balance         = serializers.IntegerField()
    mature_balance  = serializers.IntegerField()
    immature_wallet = serializers.IntegerField()



#### User Mature Wallet Balance Serializer
class UserMatureSerializer(serializers.ModelSerializer):

    class Meta:
        model  = MatureWallet
        fields = '__all__'



### User Immature Wallet Balance Serializer
class UserImmatureSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ImmatureWallet
        fields = '__all__'


class UserNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['name']


#### All user transactions
class AllUserTransactionSerializer(serializers.ModelSerializer):
    receiver = UserNameSerializer()
    user     = UserNameSerializer()

    class Meta:
        model = Transaction
        fields = ['id', 'user', 'transaction_id', 'date_created', 'amount', 'currency', 'status', 'is_completed', 'mode', 'receiver']




class UserBankAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserBankAccount
        fields = "__all__"
        read_only_fields = ["user"]


    def validate_doc(self, value):
        if value.size > 1 * 1024 * 1024:
            raise serializers.ValidationError("The file size must not exceed 1 MB.")
        if not value.name.lower().endswith(('.pdf', '.doc', '.docx')):
            raise serializers.ValidationError("Only PDF and Word documents are allowed.")
        return value


    def create(self, validated_data):
        user = self.context.get("user")
        validated_data["user"] = user
        return super().create(validated_data)



#### Serializer to show bank details in withrawal section
class UserWithDrawalBankAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserBankAccount
        fields = ['id', 'bank_name', 'acc_number', 'ifsc_code']
         


#### All withdrawal Serializer
class WithDrawalSerializer(serializers.ModelSerializer):
    bank = UserWithDrawalBankAccountSerializer(read_only=True)

    class Meta:
        model = Withdrawals
        fields = '__all__'



class CreateWithdrawalRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Withdrawals
        fields = ['amount', 'bank']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value
   

    
    


