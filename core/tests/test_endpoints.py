from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User, Group
from core.models import Conductor, Furgon, Estudiante, Colegio, Notificacion
# no timezone required here


class EndpointTests(TestCase):
    def setUp(self):
        # Groups
        admin_group, _ = Group.objects.get_or_create(name='Administrador')
        cond_group, _ = Group.objects.get_or_create(name='Conductor')
        apod_group, _ = Group.objects.get_or_create(name='Apoderado')

        # Users
        self.admin = User.objects.create_user('admin_e', password='adminpass')
        self.admin.is_staff = True
        self.admin.save()

        self.cond_user = User.objects.create_user('cond_e', password='condpass')
        self.cond_user.groups.add(cond_group)

        self.apod_user = User.objects.create_user('apod_e', password='apodpass')
        self.apod_user.groups.add(apod_group)

        # Colegio
        self.colegio = Colegio.objects.create(nombre='Cole Test E')

        # Conductor and furgon
        self.conductor = Conductor.objects.create(rut='91000000-9', nombre='Cond E', user=self.cond_user)
        self.furgon = Furgon.objects.create(
            patente='END-1',
            modelo='ModelE',
            capacidad_maxima=10,
            conductor=self.conductor,
            colegio=self.colegio,
        )

        # Student
        self.student = Estudiante.objects.create(
            rut='81000000-8',
            nombre='Stud E',
            apoderado_user=self.apod_user,
            furgon=self.furgon,
        )

        self.client = APIClient()

    def test_update_location_endpoint(self):
        self.client.force_authenticate(user=self.cond_user)
        url = f'/api/furgones/{self.furgon.id}/update_location/'
        resp = self.client.post(url, {'latitude': -33.5, 'longitude': -70.6}, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('last_latitude', data)

    def test_notifications_flow(self):
        # Admin creates a notification for the student's furgon
        self.client.force_authenticate(user=self.admin)
        url = '/api/notificaciones/'
        payload = {'tipo': 'evento', 'mensaje': 'Prueba notif', 'furgon': self.furgon.id, 'estudiante': self.student.id}
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, 201)
        nid = resp.json().get('id')

        # Apoderado can list and mark as read
        self.client.force_authenticate(user=self.apod_user)
        list_resp = self.client.get('/api/notificaciones/')
        self.assertEqual(list_resp.status_code, 200)
        # mark as read
        mark_resp = self.client.post(f'/api/notificaciones/{nid}/marcar_leida/')
        self.assertEqual(mark_resp.status_code, 200)
        notif = Notificacion.objects.get(pk=nid)
        self.assertTrue(notif.leido)
