from django.contrib import admin
from .models import Listing, Booking, Review, Payment


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'host', 'city', 'country', 'property_type', 'price_per_night', 'is_active', 'created_at']
    list_filter = ['property_type', 'is_active', 'city', 'country', 'created_at']
    search_fields = ['title', 'description', 'address', 'city', 'country']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['host']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'listing', 'guest', 'check_in_date', 'check_out_date', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'check_in_date', 'check_out_date', 'created_at']
    search_fields = ['listing__title', 'guest__username', 'guest__email']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['listing', 'guest']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['listing', 'reviewer', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['listing__title', 'reviewer__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['listing', 'reviewer']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_reference', 'booking', 'amount', 'status', 'transaction_id', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['payment_reference', 'transaction_id', 'booking__guest__username', 'booking__guest__email']
    readonly_fields = ['payment_reference', 'created_at', 'updated_at']
    raw_id_fields = ['booking']

