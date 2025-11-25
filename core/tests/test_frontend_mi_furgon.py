from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from core.models import Conductor, Furgon, Colegio


class MiFurgonTests(TestCase):
    def setUp(self):
        self.client = Client()
        cond_group, _ = Group.objects.get_or_create(name='Conductor')
        self.user = User.objects.create_user('condui2', password='p')
        self.user.groups.add(cond_group)
        self.cole = Colegio.objects.create(nombre='Cole MF')
        self.cond = Conductor.objects.create(rut='200', nombre='Cond MF', user=self.user)
        self.f = Furgon.objects.create(patente='MF-1', conductor=self.cond, colegio=self.cole)

    def test_conductor_can_view_mi_furgon(self):
        self.client.login(username='condui2', password='p')
        r = self.client.get('/mi-furgon/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'MF-1')

    def test_non_conductor_sees_nothing(self):
        # regular user not in conductor group
        User.objects.create_user('other', password='p')
        self.client.login(username='other', password='p')
        r = self.client.get('/mi-furgon/')
        # Should return page but with message that there are no furgones
        self.assertContains(r, 'No hay furgones')
