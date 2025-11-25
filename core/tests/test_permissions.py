from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User, Group
from core.models import Conductor, Furgon, Estudiante, Colegio


class PermissionTests(TestCase):
    def setUp(self):
        # Groups
        self.admin_group, _ = Group.objects.get_or_create(name='Administrador')
        self.cond_group, _ = Group.objects.get_or_create(name='Conductor')
        self.apod_group, _ = Group.objects.get_or_create(name='Apoderado')

        # Users
        self.admin = User.objects.create_user('admin_test', password='adminpass')
        self.admin.is_staff = True
        self.admin.save()

        self.cond_user = User.objects.create_user('cond_test', password='condpass')
        self.cond_user.groups.add(self.cond_group)

        self.apod_user = User.objects.create_user('apod_test', password='apodpass')
        self.apod_user.groups.add(self.apod_group)

        # Colegio
        self.colegio = Colegio.objects.create(nombre='Cole Test')

        # Conductor profile and furgon
        self.conductor = Conductor.objects.create(rut='90000000-9', nombre='Cond Test', user=self.cond_user)
        self.furgon = Furgon.objects.create(
            patente='TEST-1',
            modelo='Model',
            capacidad_maxima=10,
            conductor=self.conductor,
            colegio=self.colegio,
        )

        # Students
        self.student_owned = Estudiante.objects.create(
            rut='80000000-8',
            nombre='Stud One',
            apoderado_user=self.apod_user,
            furgon=self.furgon,
        )
        self.student_other = Estudiante.objects.create(rut='70000000-7', nombre='Stud Two')

        self.client = APIClient()

    def test_conductor_can_update_location(self):
        self.client.force_authenticate(user=self.cond_user)
        url = f'/api/furgones/{self.furgon.id}/update_location/'
        resp = self.client.post(url, {'latitude': -33.45, 'longitude': -70.66}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.furgon.refresh_from_db()
        self.assertIsNotNone(self.furgon.last_latitude)

    def test_conductor_cannot_patch_other_fields(self):
        self.client.force_authenticate(user=self.cond_user)
        url = f'/api/furgones/{self.furgon.id}/'
        resp = self.client.patch(url, {'capacidad_actual': 5}, format='json')
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_patch_furgon(self):
        self.client.force_authenticate(user=self.admin)
        url = f'/api/furgones/{self.furgon.id}/'
        resp = self.client.patch(url, {'capacidad_actual': 5}, format='json')
        self.assertIn(resp.status_code, (200, 202))

    def test_apoderado_can_view_and_update_own_student(self):
        self.client.force_authenticate(user=self.apod_user)
        url = f'/api/estudiantes/{self.student_owned.id}/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        resp2 = self.client.patch(url, {'telefono_apoderado': '56900000000'}, format='json')
        self.assertIn(resp2.status_code, (200, 202))

    def test_apoderado_cannot_modify_other_student(self):
        self.client.force_authenticate(user=self.apod_user)
        url = f'/api/estudiantes/{self.student_other.id}/'
        resp = self.client.patch(url, {'telefono_apoderado': '56911111111'}, format='json')
        self.assertEqual(resp.status_code, 403)
