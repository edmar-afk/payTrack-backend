from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Payment, PaymentProof
from django.db.models import Sum

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']

    def get_profile(self, obj):
        try:
            profile = obj.profile
            return {
                "id": profile.id,
                "year_lvl": profile.year_lvl,
                "course": profile.course
            }
        except Profile.DoesNotExist:
            return None



class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "username", "email", "year_lvl", "course"]


class RegisterSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "password", "profile"]

    def create(self, validated_data):
        profile_data = validated_data.pop("profile")
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user, **profile_data)
        return user


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["id", "student", "date_issued", "payment_type"]

    def create(self, validated_data):
        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'student',       # full user + profile details
            'proof',
            'comittee_name',
            'amount',
            'semester',
            'status',
            'feedback',
            'payment',
            'date_issued',
            'school_year',
            'cf',
            'lac',
            'pta',
            'qaa',
            'rhc',
        ]
    

class PaymentEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['proof', 'comittee_name', 'amount', 'semester', 'status', 'feedback', 'payment']
        extra_kwargs = {
            'proof': {'required': False},
            'comittee_name': {'required': False},
            'amount': {'required': False},
            'semester': {'required': False},
            'status': {'required': False},
            'feedback': {'required': False},
            'payment': {'required': False},
        }
        
        
class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'status',
            'feedback',
            'payment',
            'amount',
            'proof',
            'date_issued',
            'school_year',
            'cf',
            'lac',
            'pta',
            'qaa',
            'rhc',
        ]
        
        
class PaymentDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        
        
class PaymentSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['proof', 'payment', 'semester', 'school_year',
            'cf',
            'lac',
            'pta',
            'qaa',
            'rhc',]
        


class PaymentTypeSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        
        
class CommitteePaymentTotalSerializer(serializers.Serializer):
    comittee_name = serializers.CharField()
    total_amount = serializers.FloatField()
    count = serializers.IntegerField()

    def get_total_amount(self, obj):
        comittee_name = self.context.get('comittee_name')
        payments = Payment.objects.filter(comittee_name=comittee_name)
        total = 0
        for p in payments:
            try:
                total += float(p.amount or 0)
            except ValueError:
                continue
        return total

    def get_count(self, obj):
        comittee_name = self.context.get('comittee_name')
        payments = Payment.objects.filter(comittee_name=comittee_name)
        return payments.count()



class PaymentProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProof
        fields = ['id', 'payment', 'proof', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at', 'payment']
        
        

class CommitteeTotalsSerializer(serializers.Serializer):
    cf_total = serializers.FloatField()
    lac_total = serializers.FloatField()
    pta_total = serializers.FloatField()
    qaa_total = serializers.FloatField()
    rhc_total = serializers.FloatField()