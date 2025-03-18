from rest_framework import generics
from .models import Student
from .serializer import StudentSerializer

# List & Create Students
class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

# Retrieve, Update, Delete a Student
class StudentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
import razorpay
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment  # Ensure you have this model

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@csrf_exempt
def create_order(request):
    if request.method == "POST":
        try:
            # Validate amount field
            amount = request.POST.get("amount")
            if not amount:
                return JsonResponse({"error": "Amount is required"}, status=400)

            amount = int(amount) * 100  # Convert to paise (1 INR = 100 paise)
            currency = "INR"

            # Create order
            order_data = {
                "amount": amount,
                "currency": currency,
                "payment_capture": 1,  # Auto-capture
            }

            order = razorpay_client.order.create(order_data)

            # Save payment details (optional)
            Payment.objects.create(
                order_id=order["id"],
                amount=amount / 100,
                currency=currency,
                status="created"
            )

            return JsonResponse(order)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return HttpResponse("This endpoint only supports POST requests.", status=400)


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            razorpay_payment_id = data.get("razorpay_payment_id")
            razorpay_order_id = data.get("razorpay_order_id")
            razorpay_signature = data.get("razorpay_signature")

            if not (razorpay_payment_id and razorpay_order_id and razorpay_signature):
                return JsonResponse({"error": "Missing payment parameters"}, status=400)

            # Verify payment signature
            params = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }

            razorpay_client.utility.verify_payment_signature(params)

            # Update Payment in Database
            payment = Payment.objects.get(order_id=razorpay_order_id)
            payment.payment_id = razorpay_payment_id
            payment.status = "paid"
            payment.save()

            return JsonResponse({"status": "Payment Successful"})

        except Payment.DoesNotExist:
            return JsonResponse({"error": "Invalid order ID"}, status=400)
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"error": "Payment verification failed"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return HttpResponse("This endpoint only supports POST requests.", status=400)
