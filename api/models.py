from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    year_lvl = models.TextField(blank=True, null=True)
    course = models.TextField()

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Payment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    proof = models.ImageField(
        upload_to='payment_proofs/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )
    comittee_name = models.TextField(blank=True, null=True)
    amount = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    semester = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True, default="Pending")
    feedback = models.TextField(blank=True, null=True)
    payment = models.TextField(blank=True, null=True)
    date_issued = models.DateTimeField(auto_now_add=True)
    
    cf = models.TextField(blank=True, null=True)
    lac = models.TextField(blank=True, null=True)
    pta = models.TextField(blank=True, null=True)
    qaa = models.TextField(blank=True, null=True)
    rhc = models.TextField(blank=True, null=True)

