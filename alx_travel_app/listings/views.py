from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.db import transaction
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from .chapa_service import initiate_payment, verify_payment
import logging

logger = logging.getLogger(__name__)


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing listings.
    
    Provides CRUD operations:
    - GET /api/listings/ - List all listings
    - GET /api/listings/{id}/ - Retrieve a specific listing
    - POST /api/listings/ - Create a new listing
    - PUT /api/listings/{id}/ - Update a listing (full update)
    - PATCH /api/listings/{id}/ - Update a listing (partial update)
    - DELETE /api/listings/{id}/ - Delete a listing
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]  # Adjust permissions as needed
    
    def get_queryset(self):
        """
        Optionally filter listings by query parameters.
        """
        queryset = Listing.objects.all()
        
        # Filter by city
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filter by country
        country = self.request.query_params.get('country', None)
        if country:
            queryset = queryset.filter(country__icontains=country)
        
        # Filter by property type
        property_type = self.request.query_params.get('property_type', None)
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        
        # Filter by max price
        max_price = self.request.query_params.get('max_price', None)
        if max_price:
            try:
                queryset = queryset.filter(price_per_night__lte=float(max_price))
            except ValueError:
                pass
        
        # Filter by active status (default to active only)
        is_active = self.request.query_params.get('is_active', 'true')
        if is_active.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active.lower() == 'false':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """
        Custom action to get all bookings for a specific listing.
        GET /api/listings/{id}/bookings/
        """
        listing = self.get_object()
        bookings = Booking.objects.filter(listing=listing)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    
    Provides CRUD operations:
    - GET /api/bookings/ - List all bookings
    - GET /api/bookings/{id}/ - Retrieve a specific booking
    - POST /api/bookings/ - Create a new booking
    - PUT /api/bookings/{id}/ - Update a booking (full update)
    - PATCH /api/bookings/{id}/ - Update a booking (partial update)
    - DELETE /api/bookings/{id}/ - Delete a booking
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.AllowAny]  # Adjust permissions as needed
    
    def get_queryset(self):
        """
        Optionally filter bookings by query parameters.
        """
        queryset = Booking.objects.all()
        
        # Filter by guest
        guest_id = self.request.query_params.get('guest', None)
        if guest_id:
            queryset = queryset.filter(guest_id=guest_id)
        
        # Filter by listing
        listing_id = self.request.query_params.get('listing', None)
        if listing_id:
            queryset = queryset.filter(listing_id=listing_id)
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by check-in date (after)
        check_in_after = self.request.query_params.get('check_in_after', None)
        if check_in_after:
            queryset = queryset.filter(check_in_date__gte=check_in_after)
        
        # Filter by check-out date (before)
        check_out_before = self.request.query_params.get('check_out_before', None)
        if check_out_before:
            queryset = queryset.filter(check_out_date__lte=check_out_before)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Create a booking and automatically initiate payment process.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create booking with pending status
        booking = serializer.save(status='pending')
        
        # Trigger email notification task asynchronously
        try:
            from .tasks import send_booking_confirmation_email
            send_booking_confirmation_email.delay(booking.id)
        except Exception as e:
            logger.error(f"Failed to trigger email task: {str(e)}")
        
        # Get customer information
        guest = booking.guest
        email = guest.email or request.data.get('email', '')
        first_name = guest.first_name or request.data.get('first_name', 'Guest')
        last_name = guest.last_name or request.data.get('last_name', 'User')
        phone = request.data.get('phone', '')
        
        if not email:
            # Return booking without payment initiation if no email
            response_serializer = self.get_serializer(booking)
            return Response({
                **response_serializer.data,
                'message': 'Booking created. Please provide email to initiate payment.'
            }, status=status.HTTP_201_CREATED)
        
        # Create payment record
        from .models import Payment
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            status='pending'
        )
        
        # Initiate payment with Chapa
        chapa_response = initiate_payment(
            amount=float(booking.total_price),
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            tx_ref=payment.payment_reference,
            callback_url=request.build_absolute_uri(f'/api/payments/{payment.id}/verify/'),
            return_url=request.data.get('return_url', '')
        )
        
        if chapa_response and chapa_response.get('status') == 'success':
            # Update payment with transaction ID and response
            payment.transaction_id = chapa_response.get('transaction_id', payment.payment_reference)
            payment.chapa_response = chapa_response.get('full_response')
            payment.save()
            
            response_serializer = self.get_serializer(booking)
            return Response({
                **response_serializer.data,
                'payment': {
                    'id': payment.id,
                    'payment_reference': payment.payment_reference,
                    'status': payment.status,
                    'checkout_url': chapa_response.get('checkout_url')
                },
                'message': 'Booking created. Use the checkout_url to complete payment.'
            }, status=status.HTTP_201_CREATED)
        else:
            # Payment initiation failed, but booking is created
            payment.status = 'failed'
            payment.chapa_response = chapa_response
            payment.save()
            
            response_serializer = self.get_serializer(booking)
            return Response({
                **response_serializer.data,
                'payment': {
                    'id': payment.id,
                    'payment_reference': payment.payment_reference,
                    'status': payment.status,
                    'error': chapa_response.get('message', 'Failed to initiate payment') if chapa_response else 'Failed to initiate payment'
                },
                'message': 'Booking created but payment initiation failed. Please try again.'
            }, status=status.HTTP_201_CREATED)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payments.
    
    Provides CRUD operations:
    - GET /api/payments/ - List all payments
    - GET /api/payments/{id}/ - Retrieve a specific payment
    - POST /api/payments/ - Create a new payment (initiate payment)
    - GET /api/payments/{id}/verify/ - Verify payment status
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.AllowAny]  # Adjust permissions as needed
    
    def get_queryset(self):
        """
        Optionally filter payments by query parameters.
        """
        queryset = Payment.objects.all()
        
        # Filter by booking
        booking_id = self.request.query_params.get('booking', None)
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
        
        # Filter by status
        payment_status = self.request.query_params.get('status', None)
        if payment_status:
            queryset = queryset.filter(status=payment_status)
        
        # Filter by transaction_id
        transaction_id = self.request.query_params.get('transaction_id', None)
        if transaction_id:
            queryset = queryset.filter(transaction_id=transaction_id)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Create a payment and initiate it with Chapa API.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        booking = serializer.validated_data['booking']
        amount = serializer.validated_data['amount']
        
        # Get customer information from booking
        guest = booking.guest
        email = guest.email or request.data.get('email', '')
        first_name = guest.first_name or request.data.get('first_name', 'Guest')
        last_name = guest.last_name or request.data.get('last_name', 'User')
        phone = request.data.get('phone', '')
        
        if not email:
            return Response(
                {"error": "Email is required for payment processing"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payment record with pending status
        payment = serializer.save(status='pending')
        
        # Generate transaction reference from payment reference
        tx_ref = payment.payment_reference
        
        # Initiate payment with Chapa
        chapa_response = initiate_payment(
            amount=float(amount),
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            tx_ref=tx_ref,
            callback_url=request.build_absolute_uri(f'/api/payments/{payment.id}/verify/'),
            return_url=request.data.get('return_url', '')
        )
        
        if chapa_response and chapa_response.get('status') == 'success':
            # Update payment with transaction ID and response
            payment.transaction_id = chapa_response.get('transaction_id', tx_ref)
            payment.chapa_response = chapa_response.get('full_response')
            payment.save()
            
            response_serializer = self.get_serializer(payment)
            return Response({
                **response_serializer.data,
                'checkout_url': chapa_response.get('checkout_url'),
                'message': 'Payment initiated successfully. Use the checkout_url to complete payment.'
            }, status=status.HTTP_201_CREATED)
        else:
            # Update payment status to failed
            payment.status = 'failed'
            payment.chapa_response = chapa_response
            payment.save()
            
            error_message = chapa_response.get('message', 'Failed to initiate payment') if chapa_response else 'Failed to initiate payment'
            return Response(
                {"error": error_message, "details": chapa_response},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get', 'post'])
    def verify(self, request, pk=None):
        """
        Verify payment status with Chapa API.
        GET/POST /api/payments/{id}/verify/
        """
        payment = self.get_object()
        
        if not payment.transaction_id:
            return Response(
                {"error": "Transaction ID not found. Payment may not have been initiated."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify payment with Chapa
        verification_response = verify_payment(payment.transaction_id)
        
        if verification_response and verification_response.get('status') == 'success':
            payment_status = verification_response.get('payment_status', '').lower()
            
            # Update payment status
            if payment_status == 'success' or payment_status == 'successful':
                payment.status = 'completed'
                # Update booking status to confirmed
                payment.booking.status = 'confirmed'
                payment.booking.save()
                
                # Trigger email confirmation task
                try:
                    from .tasks import send_booking_confirmation_email
                    send_booking_confirmation_email.delay(payment.booking.id)
                except Exception as e:
                    logger.error(f"Failed to trigger email task: {str(e)}")
            
            elif payment_status == 'failed' or payment_status == 'cancelled':
                payment.status = 'failed'
            
            payment.chapa_response = verification_response.get('full_response')
            payment.save()
            
            response_serializer = self.get_serializer(payment)
            return Response({
                **response_serializer.data,
                'verification_message': verification_response.get('message'),
                'payment_status': payment_status
            })
        else:
            error_message = verification_response.get('message', 'Failed to verify payment') if verification_response else 'Failed to verify payment'
            return Response(
                {"error": error_message, "details": verification_response},
                status=status.HTTP_400_BAD_REQUEST
            )

