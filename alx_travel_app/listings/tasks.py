"""
Celery tasks for the listings app.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Booking
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_booking_confirmation_email(booking_id):
    """
    Send booking confirmation email to the guest.
    
    Args:
        booking_id: ID of the booking to send confirmation for
    """
    try:
        booking = Booking.objects.get(id=booking_id)
        guest = booking.guest
        listing = booking.listing
        
        # Get payment information if available
        payment = booking.payments.first()
        payment_reference = payment.payment_reference if payment else "N/A"
        
        # Prepare email content
        subject = f"Booking Confirmation - {listing.title}"
        
        # Create email message
        message = f"""
Dear {guest.get_full_name() or guest.username},

Thank you for your booking! Your reservation has been confirmed.

Booking Details:
-----------------
Booking ID: #{booking.id}
Payment Reference: {payment_reference}
Listing: {listing.title}
Location: {listing.city}, {listing.country}
Check-in: {booking.check_in_date}
Check-out: {booking.check_out_date}
Number of Guests: {booking.number_of_guests}
Total Price: ${booking.total_price}

Special Requests: {booking.special_requests or 'None'}

We look forward to hosting you!

Best regards,
ALX Travel App Team
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[guest.email],
            fail_silently=False,
        )
        
        logger.info(f"Confirmation email sent successfully to {guest.email} for booking #{booking.id}")
        return f"Email sent successfully to {guest.email}"
    
    except Booking.DoesNotExist:
        logger.error(f"Booking with id {booking_id} does not exist")
        return f"Booking with id {booking_id} does not exist"
    
    except Exception as e:
        logger.error(f"Failed to send confirmation email for booking #{booking_id}: {str(e)}")
        return f"Failed to send email: {str(e)}"
