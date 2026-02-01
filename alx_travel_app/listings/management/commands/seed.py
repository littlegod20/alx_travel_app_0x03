from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from alx_travel_app.listings.models import Listing, Booking, Review


class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Review.objects.all().delete()
            Booking.objects.all().delete()
            Listing.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Create sample users (hosts and guests)
        self.stdout.write('Creating sample users...')
        hosts = []
        guests = []

        # Create hosts
        for i in range(1, 6):
            username = f'host{i}'
            email = f'host{i}@example.com'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Host{i}',
                    'last_name': 'Smith',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            hosts.append(user)
            self.stdout.write(f'  Created/Found host: {username}')

        # Create guests
        for i in range(1, 11):
            username = f'guest{i}'
            email = f'guest{i}@example.com'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Guest{i}',
                    'last_name': 'Johnson',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            guests.append(user)
            self.stdout.write(f'  Created/Found guest: {username}')

        # Create sample listings
        self.stdout.write('Creating sample listings...')
        listings_data = [
            {
                'title': 'Beautiful Beachfront Villa',
                'description': 'Stunning 3-bedroom villa with ocean views, private pool, and direct beach access. Perfect for families or groups.',
                'address': '123 Ocean Drive',
                'city': 'Miami',
                'state': 'Florida',
                'country': 'USA',
                'zip_code': '33139',
                'property_type': 'villa',
                'price_per_night': Decimal('350.00'),
                'max_guests': 8,
                'bedrooms': 3,
                'bathrooms': 2,
                'amenities': 'WiFi, Pool, Air Conditioning, Kitchen, Parking, Beach Access',
            },
            {
                'title': 'Cozy Downtown Apartment',
                'description': 'Modern 1-bedroom apartment in the heart of the city. Walking distance to restaurants and attractions.',
                'address': '456 Main Street',
                'city': 'New York',
                'state': 'New York',
                'country': 'USA',
                'zip_code': '10001',
                'property_type': 'apartment',
                'price_per_night': Decimal('120.00'),
                'max_guests': 2,
                'bedrooms': 1,
                'bathrooms': 1,
                'amenities': 'WiFi, Air Conditioning, Kitchen, Washer/Dryer',
            },
            {
                'title': 'Mountain Cabin Retreat',
                'description': 'Rustic 2-bedroom cabin surrounded by nature. Perfect for a peaceful getaway.',
                'address': '789 Mountain Road',
                'city': 'Aspen',
                'state': 'Colorado',
                'country': 'USA',
                'zip_code': '81611',
                'property_type': 'cabin',
                'price_per_night': Decimal('180.00'),
                'max_guests': 4,
                'bedrooms': 2,
                'bathrooms': 1,
                'amenities': 'Fireplace, Kitchen, Parking, Mountain Views, Hiking Trails',
            },
            {
                'title': 'Luxury Resort Suite',
                'description': 'Elegant suite in 5-star resort with spa access, fine dining, and concierge service.',
                'address': '321 Resort Boulevard',
                'city': 'Las Vegas',
                'state': 'Nevada',
                'country': 'USA',
                'zip_code': '89109',
                'property_type': 'resort',
                'price_per_night': Decimal('450.00'),
                'max_guests': 4,
                'bedrooms': 2,
                'bathrooms': 2,
                'amenities': 'WiFi, Pool, Spa, Gym, Room Service, Concierge, Valet Parking',
            },
            {
                'title': 'Family-Friendly House',
                'description': 'Spacious 4-bedroom house with large backyard, perfect for families with children.',
                'address': '654 Family Lane',
                'city': 'Orlando',
                'state': 'Florida',
                'country': 'USA',
                'zip_code': '32801',
                'property_type': 'house',
                'price_per_night': Decimal('220.00'),
                'max_guests': 10,
                'bedrooms': 4,
                'bathrooms': 3,
                'amenities': 'WiFi, Pool, Air Conditioning, Kitchen, Parking, Backyard, BBQ Grill',
            },
            {
                'title': 'Modern Condo with City Views',
                'description': 'Stylish 2-bedroom condo with panoramic city views and modern amenities.',
                'address': '987 Skyline Avenue',
                'city': 'San Francisco',
                'state': 'California',
                'country': 'USA',
                'zip_code': '94102',
                'property_type': 'condo',
                'price_per_night': Decimal('280.00'),
                'max_guests': 4,
                'bedrooms': 2,
                'bathrooms': 2,
                'amenities': 'WiFi, Air Conditioning, Kitchen, Balcony, City Views, Gym Access',
            },
            {
                'title': 'Boutique Hotel Room',
                'description': 'Charming hotel room in historic boutique hotel with character and modern comforts.',
                'address': '147 Historic Square',
                'city': 'Boston',
                'state': 'Massachusetts',
                'country': 'USA',
                'zip_code': '02108',
                'property_type': 'hotel',
                'price_per_night': Decimal('150.00'),
                'max_guests': 2,
                'bedrooms': 1,
                'bathrooms': 1,
                'amenities': 'WiFi, Air Conditioning, Room Service, Historic Building',
            },
            {
                'title': 'Seaside Apartment',
                'description': 'Bright and airy 2-bedroom apartment steps away from the beach.',
                'address': '258 Beach Walk',
                'city': 'San Diego',
                'state': 'California',
                'country': 'USA',
                'zip_code': '92101',
                'property_type': 'apartment',
                'price_per_night': Decimal('200.00'),
                'max_guests': 4,
                'bedrooms': 2,
                'bathrooms': 1,
                'amenities': 'WiFi, Air Conditioning, Kitchen, Beach Access, Parking',
            },
        ]

        listings = []
        for i, listing_data in enumerate(listings_data):
            listing_data['host'] = hosts[i % len(hosts)]
            listing, created = Listing.objects.get_or_create(
                title=listing_data['title'],
                defaults=listing_data
            )
            listings.append(listing)
            if created:
                self.stdout.write(f'  Created listing: {listing.title}')
            else:
                self.stdout.write(f'  Found existing listing: {listing.title}')

        # Create sample bookings
        self.stdout.write('Creating sample bookings...')
        today = timezone.now().date()
        booking_statuses = ['confirmed', 'completed', 'pending', 'cancelled']

        for i, listing in enumerate(listings[:5]):  # Create bookings for first 5 listings
            for j in range(2):  # 2 bookings per listing
                check_in = today + timedelta(days=10 + (i * 7) + (j * 3))
                check_out = check_in + timedelta(days=2 + j)
                nights = (check_out - check_in).days
                total_price = listing.price_per_night * nights

                booking = Booking.objects.create(
                    listing=listing,
                    guest=guests[(i * 2 + j) % len(guests)],
                    check_in_date=check_in,
                    check_out_date=check_out,
                    number_of_guests=min(2 + j, listing.max_guests),
                    total_price=total_price,
                    status=booking_statuses[(i + j) % len(booking_statuses)],
                    special_requests=f'Sample booking request {i * 2 + j + 1}' if j == 0 else '',
                )
                self.stdout.write(
                    f'  Created booking: {booking.guest.username} -> {listing.title} '
                    f'({check_in} to {check_out})'
                )

        # Create sample reviews
        self.stdout.write('Creating sample reviews...')
        review_comments = [
            'Great place! Very clean and comfortable.',
            'Amazing location and beautiful property.',
            'Had a wonderful stay, highly recommend!',
            'Perfect for our family vacation.',
            'Excellent host and great amenities.',
            'Beautiful views and peaceful atmosphere.',
            'Very convenient location, close to everything.',
            'Exceeded our expectations!',
            'Comfortable and well-maintained property.',
            'Great value for money.',
        ]

        for i, listing in enumerate(listings[:6]):  # Create reviews for first 6 listings
            for j in range(2):  # 2 reviews per listing
                reviewer = guests[(i * 2 + j + 1) % len(guests)]
                rating = 4 + (i + j) % 2  # Alternating between 4 and 5
                comment = review_comments[(i * 2 + j) % len(review_comments)]

                review, created = Review.objects.get_or_create(
                    listing=listing,
                    reviewer=reviewer,
                    defaults={
                        'rating': rating,
                        'comment': comment,
                    }
                )
                if created:
                    self.stdout.write(
                        f'  Created review: {reviewer.username} -> {listing.title} '
                        f'({rating}/5 stars)'
                    )
                else:
                    self.stdout.write(
                        f'  Review already exists: {reviewer.username} -> {listing.title}'
                    )

        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully seeded database:\n'
            f'  - {User.objects.filter(is_superuser=False).count()} users\n'
            f'  - {Listing.objects.count()} listings\n'
            f'  - {Booking.objects.count()} bookings\n'
            f'  - {Review.objects.count()} reviews'
        ))

