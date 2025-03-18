from django.urls import path
from .views import StudentListCreateView, StudentRetrieveUpdateDestroyView, create_order, payment_success

urlpatterns = [
    # List all students & Create a new student
    path('students/', StudentListCreateView.as_view(), name='student-list-create'),

    # Retrieve, Update, Delete a specific student by ID
    path('students/<int:pk>/', StudentRetrieveUpdateDestroyView.as_view(), name='student-retrieve-update-destroy'),
    path('create-order/', create_order, name='create_order'),
    path('payment-success/', payment_success, name='payment_success'),
]
