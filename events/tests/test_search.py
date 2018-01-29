from django.test import TestCase
from django.urls.base import reverse
from events.models.profiles import Team
from django.contrib.auth.models import User
from events.models.locale import Country, City, SPR
from django.utils import timezone
from events.models.events import Place, Event
from django.utils.formats import date_format

class SearchableTestCase(TestCase):
    """
    Tests of Searchable model and integrations with other models.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.country = Country.objects.create(name='Testland', code='TS')
        cls.spr = SPR.objects.create(name='Teststate', country=cls.country)
        cls.city = City.objects.create(name='Testville', spr=cls.spr)
        cls.place = Place.objects.create(name='Testplace', city=cls.city)
        cls.user = User(username='testuser', email='testuser@testserver')
        cls.user.set_password('test_password')
        cls.user.save()
        cls.team = Team.objects.create(name='Test Team', owner_profile=cls.user.profile, country=cls.country)

        cls.create_event_url = reverse('create-event', kwargs={'team_id': cls.team.pk})

    def _make_datetime_fields(self, name, datetime):
        """
        Make POSTable datetime fields, prefixed with 'name', suitable for use
        with DateTimeWidget
        """
        ret = {}
        ret['%s_0' % name] = date_format(datetime, 'Y-m-d')  # Year-Month-Daty
        ret['%s_1_0' % name] = datetime.strftime('%I')  # Hour
        ret['%s_1_1' % name] = datetime.strftime('%M')  # Minute
        ret['%s_1_2' % name] = datetime.strftime('%p')  # am/pm
        return ret

    def test_event_creation(self):
        """
        Creating an event creates a Searchable for that event.
        """
        self.client.login(username=self.user.username, password='test_password')
        now = timezone.now()
        start_time = now + timezone.timedelta(hours=6)
        end_time = now + timezone.timedelta(hours=6)
        event_data = {'name': 'Test Event 1',
                      'place': self.place.pk,
                      'summary': "Test Event 1"
                      }
        event_data.update(self._make_datetime_fields('start_time', start_time))
        event_data.update(self._make_datetime_fields('end_time', end_time))

        res = self.client.post(self.create_event_url, event_data)
        # We expect to be redirected to the new event's url
        self.assertEqual(res.status_code, 302)

        new_event = Event.objects.get(name=event_data['name'])
        
        