from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Payment, Comittee, Feedback


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


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
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["student"] = request.user
        return super().create(validated_data)


class ComitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comittee
        fields = ["id", "name", "details", "amount", "deadline", "date_posted"]


class StudentPaymentSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    payment_type = ComitteeSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "student",
            "proof",
            "payment",
            "payment_type",

            "date_issued",
        ]

    def get_student(self, obj):
        profile = getattr(obj.student, "profile", None)
        if profile:
            return {
                "username": obj.student.username,
                "first_name": obj.student.first_name,
                "last_name": obj.student.last_name,
                "year_lvl": profile.year_lvl,
                "course": profile.course,
            }
        return {
            "username": obj.student.username,
            "first_name": obj.student.first_name,
            "last_name": obj.student.last_name,
            "year_lvl": "",
            "course": "",
        }



class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "payments", "status", "feedback", "date_issued"]
        read_only_fields = ["id", "date_issued", "payments"]  # <-- add payments here

    def create(self, validated_data):
        payment = self.context.get("payment")
        if payment:
            validated_data["payments"] = payment
        return super().create(validated_data)
    
    
class LatestFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "status", "feedback", "date_issued"]