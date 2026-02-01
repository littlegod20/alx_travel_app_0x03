from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Payment


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (used in nested relationships).
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for Listing model.
    """
    host = UserSerializer(read_only=True)
    host_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='host',
        write_only=True
    )
    amenities_list = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'description',
            'address',
            'city',
            'state',
            'country',
            'zip_code',
            'property_type',
            'price_per_night',
            'max_guests',
            'bedrooms',
            'bathrooms',
            'amenities',
            'amenities_list',
            'host',
            'host_id',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_amenities_list(self, obj):
        """
        Convert comma-separated amenities string to a list.
        """
        if obj.amenities:
            return [amenity.strip() for amenity in obj.amenities.split(',') if amenity.strip()]
        return []

    def validate_price_per_night(self, value):
        """
        Validate that price per night is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Price per night must be greater than zero.")
        return value

    def validate_max_guests(self, value):
        """
        Validate that max guests is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Maximum guests must be greater than zero.")
        return value


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model.
    """
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.filter(is_active=True),
        source='listing',
        write_only=True
    )
    guest = UserSerializer(read_only=True)
    guest_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='guest',
        write_only=True
    )
    duration_nights = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id',
            'listing',
            'listing_id',
            'guest',
            'guest_id',
            'check_in_date',
            'check_out_date',
            'number_of_guests',
            'total_price',
            'status',
            'special_requests',
            'duration_nights',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_duration_nights(self, obj):
        """
        Calculate the number of nights for the booking.
        """
        if obj.check_in_date and obj.check_out_date:
            return (obj.check_out_date - obj.check_in_date).days
        return None

    def validate(self, data):
        """
        Validate booking data.
        """
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        listing = data.get('listing')
        number_of_guests = data.get('number_of_guests')

        # Validate check-in and check-out dates
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError({
                    'check_out_date': 'Check-out date must be after check-in date.'
                })

        # Validate number of guests
        if listing and number_of_guests:
            if number_of_guests > listing.max_guests:
                raise serializers.ValidationError({
                    'number_of_guests': f'Number of guests cannot exceed {listing.max_guests} (maximum for this listing).'
                })

        # Calculate total price if listing and dates are provided
        if listing and check_in and check_out:
            nights = (check_out - check_in).days
            if nights > 0:
                calculated_total = listing.price_per_night * nights
                if 'total_price' not in data or data['total_price'] != calculated_total:
                    data['total_price'] = calculated_total

        return data

    def validate_total_price(self, value):
        """
        Validate that total price is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Total price must be greater than zero.")
        return value


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for Payment model.
    """
    booking = BookingSerializer(read_only=True)
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(),
        source='booking',
        write_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'booking',
            'booking_id',
            'transaction_id',
            'amount',
            'status',
            'payment_reference',
            'chapa_response',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'payment_reference', 'created_at', 'updated_at', 'transaction_id']

    def validate_amount(self, value):
        """
        Validate that payment amount is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than zero.")
        return value

