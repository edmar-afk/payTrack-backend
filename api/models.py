from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    year_lvl = models.TextField(blank=True, null=True)
    course = models.TextField()

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Comittee(models.Model):
    name = models.TextField()
    details = models.TextField(blank=True, null=True)
    amount = models.TextField()
    deadline = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    proof = models.ImageField(
        upload_to='payment_proofs/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )
    payment = models.TextField()
    payment_type = models.ForeignKey(Comittee, on_delete=models.CASCADE)
    date_issued = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    payments = models.ForeignKey(Payment, on_delete=models.CASCADE)
    status = models.TextField()
    feedback = models.TextField()
    date_issued = models.DateTimeField(auto_now_add=True)