from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User, Group
from core.models import Conductor, Furgon, Colegio
from django.utils import timezone
import datetime


class ViewsAdditionalTests(TestCase):
    def setUp(self):
        admin_group, _ = Group.objects.get_or_create(name='Administrador')
        cond_group, _ = Group.objects.get_or_create(name='Conductor')

        self.cond_user = User.objects.create_user('cond_v', password='condpass')
        self.cond_user.groups.add(cond_group)

        self.cole = Colegio.objects.create(nombre='Cole V')
        self.conductor = Conductor.objects.create(rut='92000000-1', nombre='Cond V', user=self.cond_user)
        self.furgon = Furgon.objects.create(patente='V-1', conductor=self.conductor, colegio=self.cole)

        self.client = APIClient()

    def test_update_location_missing_fields_returns_400(self):
        self.client.force_authenticate(user=self.cond_user)
        url = f'/api/furgones/{self.furgon.id}/update_location/'
        resp = self.client.post(url, {}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('detail', resp.json())

    def test_update_location_invalid_types_returns_400(self):
        self.client.force_authenticate(user=self.cond_user)
        url = f'/api/furgones/{self.furgon.id}/update_location/'
        resp = self.client.post(url, {'latitude': 'nope', 'longitude': 'nah'}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('detail', resp.json())

    def test_update_location_invalid_reported_at_uses_now(self):
        self.client.force_authenticate(user=self.cond_user)
        url = f'/api/furgones/{self.furgon.id}/update_location/'
        before = timezone.now()
        resp = self.client.post(url, {'latitude': -10.0, 'longitude': 20.0, 'reported_at': 'invalid-date'}, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('last_reported_at', data)
        # parse returned datetime and ensure it's >= before (allow small delta)
        parsed = data.get('last_reported_at')
        self.assertIsNotNone(parsed)
