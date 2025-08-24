from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import RegisterSerializer, ProfileSerializer, PaymentSerializer, ComitteeSerializer, LatestFeedbackSerializer, StudentPaymentSerializer, FeedbackSerializer
from .models import Profile, Payment, Comittee, Feedback
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


class PaymentUploadView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class ComitteePostView(APIView):
    def post(self, request):
        serializer = ComitteeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComitteeListView(APIView):
    def get(self, request, name=None):
        committees = Comittee.objects.filter(
            name=name).order_by('-date_posted')
        serializer = ComitteeSerializer(committees, many=True)
        return Response(serializer.data)


class ComitteeUpdateView(APIView):
    def put(self, request, id):
        committee = get_object_or_404(Comittee, id=id)
        serializer = ComitteeSerializer(committee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        committee = get_object_or_404(Comittee, id=id)
        serializer = ComitteeSerializer(
            committee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComitteeDeleteView(APIView):
    def delete(self, request, id):
        committee = get_object_or_404(Comittee, id=id)
        committee.delete()
        return Response({"message": "Committee deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class LatestComitteeView(APIView):
    def get(self, request, name):
        comittee = Comittee.objects.filter(
            name=name).order_by('-date_posted').first()
        if comittee:
            serializer = ComitteeSerializer(comittee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "No committee found"}, status=status.HTTP_404_NOT_FOUND)


class LatestCommitteePaymentsView(APIView):
    def get(self, request, user_id, committee_name):
        latest_committee = (
            Comittee.objects.filter(name=committee_name)
            .order_by("-date_posted")
            .first()
        )

        if not latest_committee:
            return Response(
                {"detail": "Committee not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        payments = Payment.objects.filter(
            student_id=user_id,
            payment_type=latest_committee
        )

        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentCreateView(APIView):
    def post(self, request, studentid, name):
        committee = Comittee.objects.filter(
            name=name).order_by('-date_posted').first()
        if not committee:
            return Response({"error": "Committee not found"}, status=status.HTTP_404_NOT_FOUND)

        student = get_object_or_404(User, id=studentid)

        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save(
                student=student,
                payment_type=committee,

            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print("serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckPaymentView(APIView):
    def get(self, request, userid, name):
        # Get the latest committee by name
        committee = (
            Comittee.objects.filter(name=name)
            .order_by("-date_posted")
            .first()
        )

        if not committee:
            return Response({"message": "No committee found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if a payment exists for this student and committee
        payment = Payment.objects.filter(
            student_id=userid, payment_type=committee).first()

        if payment:
            serializer = PaymentSerializer(payment)
            return Response({
                "submitted": True,
                "payment": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "submitted": False,
                "payment": None
            }, status=status.HTTP_200_OK)


class CommitteePaymentsView(APIView):
    def get(self, request, id, name):
        committee = get_object_or_404(Comittee, id=id, name=name)
        payments = Payment.objects.filter(payment_type=committee)

        committee_data = ComitteeSerializer(committee).data
        payments_data = StudentPaymentSerializer(payments, many=True).data

        return Response({
            "committee": committee_data,
            "payments": payments_data
        }, status=status.HTTP_200_OK)


class PaymentFeedbackView(APIView):
    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        serializer = FeedbackSerializer(
            data=request.data,
            context={"request": request, "payment": payment}  # <-- add this
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LatestFeedbackView(APIView):
    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)
        latest_feedback = Feedback.objects.filter(
            payments=payment).order_by("-date_issued").first()

        if not latest_feedback:
            return Response({"detail": "No feedback found for this payment."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LatestFeedbackSerializer(latest_feedback)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeletePaymentView(APIView):
    def delete(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)
        payment.delete()
        return Response({"detail": "Payment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
