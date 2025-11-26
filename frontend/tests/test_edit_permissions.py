from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Colegio, Conductor, Furgon, Ruta


User = get_user_model()


class EditPermissionsTests(TestCase):
    def setUp(self):
        # admin
        self.admin = User.objects.create_user('admin', 'admin@example.com', 'pass')
        self.admin.is_staff = True
        self.admin.save()

        # conductor user
        self.cond_user = User.objects.create_user('driver', 'driver@example.com', 'pass')
        self.other_user = User.objects.create_user('other', 'other@example.com', 'pass')

        # create conductor objects
        self.cond = Conductor.objects.create(rut='11111111-1', nombre='Driver One', telefono='123', user=self.cond_user)
        self.other_cond = Conductor.objects.create(rut='22222222-2', nombre='Driver Two', telefono='456', user=self.other_user)

        # colegio
        self.cole = Colegio.objects.create(nombre='Colegio Test', direccion='Calle 1')

        # furgon assigned to cond
        self.furgon = Furgon.objects.create(patente='ABC123', modelo='Model', conductor=self.cond)

        # ruta assigned to furgon
        self.ruta = Ruta.objects.create(furgon=self.furgon, tipo_ruta='ida', localidades='A,B', hora_inicio='08:00')

        self.client = Client()

    def test_admin_can_edit_colegio(self):
        self.client.login(username='admin', password='pass')
        url = reverse('frontend:colegio_edit', args=[self.cole.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(url, {'nombre': 'Colegio Changed', 'direccion': 'Calle X'})
        self.assertEqual(resp.status_code, 302)
        self.cole.refresh_from_db()
        self.assertEqual(self.cole.nombre, 'Colegio Changed')

    def test_conductor_can_edit_own_profile(self):
        self.client.login(username='driver', password='pass')
        url = reverse('frontend:conductor_edit', args=[self.cond.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(url, {'rut': self.cond.rut, 'nombre': 'Driver Changed', 'telefono': '999'})
        self.assertEqual(resp.status_code, 302)
        self.cond.refresh_from_db()
        self.assertEqual(self.cond.nombre, 'Driver Changed')

    def test_conductor_cannot_edit_other_conductor(self):
        self.client.login(username='driver', password='pass')
        url = reverse('frontend:conductor_edit', args=[self.other_cond.pk])
        resp = self.client.get(url)
        # should be forbidden (403) or redirected
        self.assertIn(resp.status_code, (302, 403))

    def test_conductor_can_edit_own_route(self):
        self.client.login(username='driver', password='pass')
        url = reverse('frontend:ruta_edit', args=[self.ruta.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(url, {'furgon': self.furgon.pk, 'tipo_ruta': 'vuelta', 'localidades': 'A,B,C', 'hora_inicio': '09:00'})
        self.assertEqual(resp.status_code, 302)
        self.ruta.refresh_from_db()
        self.assertEqual(self.ruta.tipo_ruta, 'vuelta')

    def test_other_user_cannot_edit_route(self):
        self.client.login(username='other', password='pass')
        url = reverse('frontend:ruta_edit', args=[self.ruta.pk])
        # other user is conductor of that route's furgon? no (other is not owner), expect forbidden or redirect
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (302, 403))
