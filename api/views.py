from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import CommitteePaymentTotalSerializer, PaymentTypeSerializer, PaymentSubmitSerializer,PaymentEditSerializer, RegisterSerializer, ProfileSerializer, PaymentSerializer, PaymentDetailSerializer, PaymentDeleteSerializer
from .models import Profile, Payment
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import UpdateAPIView, GenericAPIView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser

        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class ProfileDetailView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    lookup_field = "user_id"  # use user_id instead of profile id

    def get_queryset(self):
        return Profile.objects.select_related("user")



class DeletePaymentView(APIView):
    def delete(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)
        payment.delete()
        return Response({"detail": "Payment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    
class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.select_related('student', 'student__profile').order_by('-date_issued')
    serializer_class = PaymentSerializer
    
    
class PaymentEditView(generics.RetrieveUpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentEditSerializer
    lookup_field = "id"
    
class PaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentDetailSerializer
    lookup_field = "id"
    
    
class PaymentDeleteView(generics.DestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentDeleteSerializer
    lookup_field = 'id'               # field in the model
    lookup_url_kwarg = 'payment_id'   # kwarg in the URL

    def delete(self, request, *args, **kwargs):
        payment = self.get_object()
        payment.delete()
        return Response({"message": "Payment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class UserPaymentsList(generics.ListAPIView):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Payment.objects.filter(student_id=user_id).order_by('-date_issued')
    


class PaymentSubmitView(APIView):
    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentSubmitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=user)
            return Response({"success": "Payment submitted successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PaymentByCommitteeView(APIView):
    def get(self, request, comittee_name):
        payments = Payment.objects.filter(comittee_name=comittee_name)
        serializer = PaymentTypeSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class CommitteeTotalAmountView(APIView):
    def get(self, request, comittee_name):
        payments = Payment.objects.filter(comittee_name=comittee_name)
        total = sum([p.amount or 0 for p in payments])
        count = payments.count()
        data = {
            "comittee_name": comittee_name,
            "total_amount": total,
            "count": count
        }
        return Response(data)
    
    
class StudentPaymentsView(APIView):
    def get(self, request, student_id):
        school_year = request.GET.get('school_year', '2025-2026')
        semester = request.GET.get('semester', 'First Semester')


        payments = Payment.objects.filter(
            student_id=student_id,
            school_year=school_year,
            semester=semester
        ).order_by('-date_issued')

        serializer = PaymentTypeSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)