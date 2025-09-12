from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("register/", views.RegisterView.as_view(), name="register"),

    path("profiles/<int:user_id>/", views.ProfileDetailView.as_view(), name="profile-detail"),

    path('payments/', views.PaymentListView.as_view(), name='payment-list'),
    path('payments/<int:id>/edit/', views.PaymentEditView.as_view(), name='payment-edit'),
    path('payments/<int:id>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/delete/<int:payment_id>/', views.PaymentDeleteView.as_view(), name='payment-delete'),
    path('payments/user/<int:user_id>/', views.UserPaymentsList.as_view(), name='user-payments'),
    path('submit-payment/<int:user_id>/', views.PaymentSubmitView.as_view(), name='submit-payment'),
    path('payment-type/<str:comittee_name>/', views.PaymentByCommitteeView.as_view(), name='payment-by-committee'),
    path('total-amount/<str:comittee_name>/', views.CommitteeTotalAmountView.as_view()),
]
