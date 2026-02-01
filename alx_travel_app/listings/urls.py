"""
URL configuration for listings API endpoints.

This module configures RESTful API endpoints for listings and bookings
using Django REST framework's router.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, PaymentViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payments', PaymentViewSet, basename='payment')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
