from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UserSerializer, CommitteeTotalsSerializer, PaymentProofSerializer, CommitteePaymentTotalSerializer, PaymentTypeSerializer, PaymentSubmitSerializer,PaymentEditSerializer, RegisterSerializer, ProfileSerializer, PaymentSerializer, PaymentDetailSerializer, PaymentDeleteSerializer
from .models import Profile, Payment, PaymentProof
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import NotFound
from django.db.models import Sum

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

        serializer = PaymentSerializer(data=request.data)
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
        school_year = request.GET.get('school_year')
        semester = request.GET.get('semester')
        is_walk_in = request.GET.get('is_walk_in')

        payments = Payment.objects.filter(student_id=student_id)

        if school_year:
            payments = payments.filter(school_year=school_year)

        if semester:
            payments = payments.filter(semester=semester)

        # FIXED WALK-IN FILTER
        if is_walk_in in ["true", "false"]:
            payments = payments.filter(is_walk_in=(is_walk_in == "true"))

        payments = payments.order_by("-date_issued")

        serializer = PaymentTypeSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



    
class UpdatePaymentView(APIView):
    def put(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response({"message": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "cf": float(payment.cf or 0) + float(request.data.get("cf", 0)),
            "lac": float(payment.lac or 0) + float(request.data.get("lac", 0)),
            "pta": float(payment.pta or 0) + float(request.data.get("pta", 0)),
            "qaa": float(payment.qaa or 0) + float(request.data.get("qaa", 0)),
            "rhc": float(payment.rhc or 0) + float(request.data.get("rhc", 0)),
        }




        serializer = PaymentDetailSerializer(payment, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UploadPaymentProofView(APIView):
    def post(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)

        files = request.FILES.getlist('proofs')
        if not files:
            return Response({"error": "No files uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        proofs = []
        for file in files:
            proof_instance = PaymentProof(payment=payment, proof=file)
            proof_instance.save()
            proofs.append(proof_instance)

        serializer = PaymentProofSerializer(proofs, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
class PaymentProofByPaymentIdView(ListAPIView):
    serializer_class = PaymentProofSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        payment_id = self.kwargs.get('payment_id')
        return PaymentProof.objects.filter(payment_id=payment_id).order_by('-uploaded_at')
    
class UploadPaymentProofView(generics.CreateAPIView):
    serializer_class = PaymentProofSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_payment(self):
        payment_id = self.kwargs.get("paymentId")
        try:
            return Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            raise NotFound("Payment not found")

    def perform_create(self, serializer):
        payment = self.get_payment()
        serializer.save(payment=payment)
        
        
class CommitteeTotalsView(APIView):
    def get(self, request):
        totals = {"cf": 0, "lac": 0, "pta": 0, "qaa": 0, "rhc": 0}
        counts = {"cf": 0, "lac": 0, "pta": 0, "qaa": 0, "rhc": 0}

        payments = Payment.objects.all()

        for payment in payments:
            for key in totals.keys():
                value = getattr(payment, key)
                try:
                    value_float = float(value)
                    totals[key] += value_float
                    counts[key] += 1
                except (TypeError, ValueError):
                    continue

        # Return totals and counts
        data = {**totals, **{f"{k}_count": counts[k] for k in counts}}
        return Response(data)
    
class NonSuperUserListView(APIView):
    def get(self, request):
        users = User.objects.filter(is_superuser=False)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
