from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Event, Location, JoinRequest
from django.utils import timezone
from datetime import timedelta

class EventBasicTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        
        self.location = Location.objects.create(
            name="Student Union", 
            latitude=35.3, 
            longitude=-80.7
        )

        self.start_time = timezone.now() + timedelta(hours=1)
        self.end_time = self.start_time + timedelta(hours=2)

        self.event_data = {
            "name": "Study Group",
            "details": "Math 101",
            "location_id": self.location.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "max_capacity": 5,
            "is_public": True
        }

    def test_create_event_authenticated(self):
        """Ensure logged-in user can create an event."""
        response = self.client.post(reverse('event-list'), self.event_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().host, self.user)

    def test_create_event_unauthenticated(self):
        """Ensure unauthenticated user CANNOT create an event."""
        self.client.logout()
        response = self.client.post(reverse('event-list'), self.event_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_event_capacity_logic(self):
        """Test the custom is_full() method in models.py."""
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=1)

        event = Event.objects.create(
            host=self.user, 
            location=self.location, 
            max_capacity=1, 
            name="Tiny Event",
            details="Tiny details", 
            start_time=start,
            end_time=end          
        )
        
        other_user = User.objects.create_user(username='other', password='pw')
        
        self.assertFalse(event.is_full())
        
        event.participant_list.add(other_user)
        
        self.assertTrue(event.is_full())

    def test_location_filtering(self):
        """Test filtering events by location ID."""
        Event.objects.create(host=self.user, location=self.location, **self.event_data)
        
        library = Location.objects.create(name="Library", latitude=0, longitude=0)
        
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=1)
        
        Event.objects.create(
            host=self.user, 
            location=library, 
            name="Library Event",
            details="Read books",
            start_time=start,
            end_time=end          
        )

        response = self.client.get(f'/api/events/?location={self.location.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class EventPermissionTests(APITestCase):
    def setUp(self):
        self.host = User.objects.create_user(username='host', password='password')
        self.attacker = User.objects.create_user(username='attacker', password='password')
        self.location = Location.objects.create(name="Gym", latitude=10, longitude=10)
        
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=2)

        self.event = Event.objects.create(
            name="Host's Event",
            details="Host details", 
            host=self.host,
            location=self.location,
            start_time=start,
            end_time=end  
        )

    def test_delete_event_as_host(self):
        """Host should be able to delete their own event."""
        self.client.force_authenticate(user=self.host)
        url = reverse('delete-event', args=[self.event.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())

    def test_delete_event_as_attacker(self):
        """Another user should NOT be able to delete the host's event."""
        self.client.force_authenticate(user=self.attacker)
        url = reverse('delete-event', args=[self.event.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Event.objects.filter(id=self.event.id).exists())

class JoinPublicEventTests(APITestCase):
    def setUp(self):
        self.host = User.objects.create_user(username='host', password='password')
        self.guest = User.objects.create_user(username='guest', password='password')
        self.location = Location.objects.create(name="Park", latitude=0, longitude=0)
        
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=2)

        self.event = Event.objects.create(
            name="Picnic",
            details="Fun in the sun", 
            host=self.host,
            location=self.location,
            is_public=True,
            max_capacity=2,
            start_time=start,
            end_time=end 
        )

    def test_guest_join_success(self):
        self.client.force_authenticate(user=self.guest)
        url = reverse('join-event', args=[self.event.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.event.participant_list.filter(id=self.guest.id).exists())

    def test_host_cannot_join_own_event(self):
        """The view explicitly forbids the host from joining as a participant."""
        self.client.force_authenticate(user=self.host)
        url = reverse('join-event', args=[self.event.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_double_join(self):
        """User cannot join the same event twice."""
        self.event.participant_list.add(self.guest) 
        
        self.client.force_authenticate(user=self.guest)
        url = reverse('join-event', args=[self.event.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class PrivateEventWorkflowTests(APITestCase):
    def setUp(self):
        self.host = User.objects.create_user(username='host', password='pw')
        self.requester = User.objects.create_user(username='requester', password='pw')
        self.location = Location.objects.create(name="Home", latitude=1, longitude=1)
        
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=2)

        self.private_event = Event.objects.create(
            name="Secret Party",
            details="Shhh", 
            host=self.host,
            location=self.location,
            is_public=False, 
            start_time=start,
            end_time=end 
        )

    def test_request_join_private_event(self):
        """Test creating a join request."""
        self.client.force_authenticate(user=self.requester)
        url = reverse('request-join-event', args=[self.private_event.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(JoinRequest.objects.filter(
            user=self.requester, 
            event=self.private_event, 
            status='pending'
        ).exists())

    def test_approve_join_request(self):
        """Test host approving a request."""
        join_req = JoinRequest.objects.create(user=self.requester, event=self.private_event)
        
        self.client.force_authenticate(user=self.host)
        url = reverse('approve-join-request', args=[join_req.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        join_req.refresh_from_db()
        self.assertEqual(join_req.status, 'approved')
        self.assertTrue(self.private_event.participant_list.filter(id=self.requester.id).exists())

    def test_deny_join_request(self):
        """Test host denying a request."""
        join_req = JoinRequest.objects.create(user=self.requester, event=self.private_event)
        
        self.client.force_authenticate(user=self.host)
        url = reverse('deny-join-request', args=[join_req.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        join_req.refresh_from_db()
        self.assertEqual(join_req.status, 'denied')
        self.assertFalse(self.private_event.participant_list.filter(id=self.requester.id).exists())

    def test_stranger_cannot_approve_request(self):
        """A random user cannot approve a request for someone else's event."""
        stranger = User.objects.create_user(username='stranger', password='pw')
        join_req = JoinRequest.objects.create(user=self.requester, event=self.private_event)
        
        self.client.force_authenticate(user=stranger)
        url = reverse('approve-join-request', args=[join_req.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class ValidationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', password='p')
        self.location = Location.objects.create(name="L", latitude=0, longitude=0)
        self.client.force_authenticate(user=self.user)

    def test_end_time_before_start_time(self):
        """Should fail if end time is before start time."""
        future = timezone.now() + timedelta(hours=2)
        past_relative = future - timedelta(hours=1)
        
        data = {
            "name": "Bad Time Event",
            "details": "Testing",
            "location_id": self.location.id,
            "start_time": future,
            "end_time": past_relative,
            "max_capacity": 5
        }
        
        response = self.client.post(reverse('event-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('non_field_errors' in response.data or 'end_time' in response.data)

    def test_start_time_in_past(self):
        """Should fail if start time is in the past."""
        past = timezone.now() - timedelta(hours=1)
        end = timezone.now() + timedelta(hours=1)
        
        data = {
            "name": "Past Event",
            "details": "Testing",
            "location_id": self.location.id,
            "start_time": past, 
            "end_time": end,
            "max_capacity": 5
        }
        
        response = self.client.post(reverse('event-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='original_name', password='old_password')
        self.client.force_authenticate(user=self.user)

    def test_update_profile_and_username(self):
        """Test updating bio (Profile model) and username (User model) simultaneously."""
        url = reverse('profile')
        data = {
            "bio": "New Bio",
            "user": {
                "username": "new_name"
            }
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.bio, "New Bio")
        self.assertEqual(self.user.username, "new_name")

class AdditionalViewsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')
        self.client.force_authenticate(user=self.user)
        self.location = Location.objects.create(name="Gym", latitude=10, longitude=10)
        
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=2)

        self.event = Event.objects.create(
            name="My Event",
            details="Details",
            host=self.user,
            location=self.location,
            start_time=start,
            end_time=end
        )

    def test_update_event(self):
        """Test editing an event (PUT/PATCH)."""
        url = reverse('edit-event', args=[self.event.id])
        data = {
            "name": "Updated Name",
            "details": "Updated Details",
            "location_id": self.location.id,
            "start_time": self.event.start_time,
            "end_time": self.event.end_time,
            "max_capacity": 10
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.event.refresh_from_db()
        self.assertEqual(self.event.name, "Updated Name")

    def test_leave_event(self):
        """Test leaving an event."""
        self.event.participant_list.add(self.user)
        
        url = reverse('leave-event', args=[self.event.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertFalse(self.event.participant_list.filter(id=self.user.id).exists())

    def test_hosted_and_joined_lists(self):
        """Test the endpoints that list my events."""
        self.event.participant_list.add(self.user)
        response = self.client.get(reverse('joined-events'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(reverse('hosted-events'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_location_endpoint(self):
        """Test the standalone create location endpoint."""
        url = reverse('create-location')
        data = {
            "name": "New Place",
            "latitude": 50.0,
            "longitude": 50.0
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Location.objects.filter(name="New Place").exists())

    def test_comments(self):
        """Test creating and listing comments."""
        url = reverse('event-comments', kwargs={'event_id': self.event.id})
        
        response = self.client.post(url, {"text": "Nice event!"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], "Nice event!")

class coverage_boost_tests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password')
        self.location = Location.objects.create(name="Venue", latitude=10, longitude=10)

    def test_register_user(self):
        """Test the CreateUserView (Sign up)."""
        url = reverse('register')
        data = {"username": "newguy", "password": "securepassword123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newguy").exists())

    def test_get_user_by_id(self):
        """Test finding a user by ID and the 404 case."""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('get_user_by_id', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'tester')

        url = reverse('get_user_by_id', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_location_list(self):
        """Test listing all locations."""
        self.client.force_authenticate(user=self.user)
        url = reverse('location-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_host_inbox_view(self):
        """Test the ListJoinRequestsView (Host checking pending requests)."""
        self.client.force_authenticate(user=self.user)
        
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=1)
        
        event = Event.objects.create(
            name="My Private Event", details="Details", 
            host=self.user, location=self.location, is_public=False,
            start_time=start, end_time=end
        )
        other_user = User.objects.create_user(username='applicant', password='pw')
        JoinRequest.objects.create(event=event, user=other_user, status='pending')

        url = reverse('list-join-requests')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_resubmit_denied_request(self):
        """
        Complex Logic Test: 
        If a user was DENIED, and they request to join AGAIN, 
        it should reset status to 'pending' (not create a new row).
        """
        self.client.force_authenticate(user=self.user)
        
        host = User.objects.create_user(username='host2', password='pw')
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=1)
        
        event = Event.objects.create(
            name="Exclusive", details="Details", 
            host=host, location=self.location, is_public=False,
            start_time=start, end_time=end
        )
        JoinRequest.objects.create(event=event, user=self.user, status='denied')

        url = reverse('request-join-event', args=[event.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'pending')

    def test_public_feed_unauthenticated(self):
        """Test that anonymous users can see public events (get_queryset logic)."""
        self.client.logout()
        
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=1)
        
        Event.objects.create(
            name="Public", details="Details", 
            host=self.user, location=self.location, is_public=True,
            start_time=start, end_time=end
        )
        Event.objects.create(
            name="Hidden", details="Details", 
            host=self.user, location=self.location, is_public=False,
            start_time=start, end_time=end
        )

        url = reverse('event-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Public")

class EdgeCaseTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')
        self.client.force_authenticate(user=self.user)
        self.location = Location.objects.create(name="Gym", latitude=10, longitude=10)

    def test_create_location_missing_data(self):
        """Test validation in create_location view."""
        url = reverse('create-location')
        data = {"name": "Incomplete Place"} 
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_location_duplicate(self):
        """Test that creating an existing location returns 200 (not 201)."""
        url = reverse('create-location')
        data = {"name": "Gym", "latitude": 10, "longitude": 10}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_event_permission_denied(self):
        """Ensure a user cannot edit someone else's event."""
        other_host = User.objects.create_user(username='other', password='pw')
        
        event = Event.objects.create(
            name="Other's Event", details="Details",
            host=other_host, location=self.location,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        url = reverse('edit-event', args=[event.id])
        
        response = self.client.patch(url, {"name": "Hacked"}, format='json')
        
        self.assertTrue(response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_leave_event_not_participant(self):
        """Test leaving an event you are not part of."""
        event = Event.objects.create(
            name="Event", details="Details", host=self.user, location=self.location,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2)
        )
        url = reverse('leave-event', args=[event.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_join_public_event_error(self):
        """Test request-join endpoint fails for PUBLIC events (should use join-event)."""
        event = Event.objects.create(
            name="Public", details="Details", is_public=True,
            host=self.user, location=self.location,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2)
        )
        url = reverse('request-join-event', args=[event.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class JoinLogicTests(APITestCase):
    def setUp(self):
        self.host = User.objects.create_user(username='host', password='pw')
        self.applicant = User.objects.create_user(username='applicant', password='pw')
        self.location = Location.objects.create(name="Home", latitude=1, longitude=1)
        
        self.event = Event.objects.create(
            name="Private", details="Details", 
            host=self.host, location=self.location, is_public=False,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2),
            max_capacity=5
        )

    def test_host_cannot_request_join_own_event(self):
        """Host cannot create a join request for their own event."""
        self.client.force_authenticate(user=self.host)
        url = reverse('request-join-event', args=[self.event.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_already_approved_request(self):
        """Error when approving a request that is already approved."""
        req = JoinRequest.objects.create(event=self.event, user=self.applicant, status='approved')
        
        self.client.force_authenticate(user=self.host)
        url = reverse('approve-join-request', args=[req.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deny_already_denied_request(self):
        """Error when denying a request that is already denied."""
        req = JoinRequest.objects.create(event=self.event, user=self.applicant, status='denied')
        
        self.client.force_authenticate(user=self.host)
        url = reverse('deny-join-request', args=[req.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_request_event_full(self):
        """Cannot approve a request if the event is full."""
        self.event.max_capacity = 0
        self.event.save()
        
        req = JoinRequest.objects.create(event=self.event, user=self.applicant, status='pending')
        
        self.client.force_authenticate(user=self.host)
        url = reverse('approve-join-request', args=[req.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)