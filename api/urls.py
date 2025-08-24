from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("register/", views.RegisterView.as_view(), name="register"),

    path("profiles/<int:user_id>/", views.ProfileDetailView.as_view(), name="profile-detail"),
    
    path("payments/upload/", views.PaymentUploadView.as_view(), name="payment-upload"),

    # feedback route must be before the generic user_id/committee_name route
    path("payments/<int:pk>/feedback/", views.PaymentFeedbackView.as_view(), name="payment-feedback"),
    path("payments/<int:payment_id>/latest-feedback/", views.LatestFeedbackView.as_view(), name="latest-feedback"),
    path('payments/<int:payment_id>/delete/', views.DeletePaymentView.as_view(), name='delete-payment'),
    
    path("committees/post/", views.ComitteePostView.as_view(), name="committee-post"),
    path("payments/list/<str:name>/", views.ComitteeListView.as_view(), name="comittee-list"),
    path("committee/update/<int:id>/", views.ComitteeUpdateView.as_view(), name="committee-update"),
    path("committee/delete/<int:id>/", views.ComitteeDeleteView.as_view(), name="committee-delete"),
    path("committee/latest/<str:name>/", views.LatestComitteeView.as_view(), name="latest-committee"),

    path("payments/<int:user_id>/<str:committee_name>/", views.LatestCommitteePaymentsView.as_view(), name="latest-committee-payments"),
    
    path('payment/<int:studentid>/<str:name>/', views.PaymentCreateView.as_view(), name='payment-create'),
    path("check-payment/<int:userid>/<str:name>/", views.CheckPaymentView.as_view(), name="check-payment"),
    path("committee/<int:id>/<str:name>/payments/", views.CommitteePaymentsView.as_view(), name="committee-payments"),
]
