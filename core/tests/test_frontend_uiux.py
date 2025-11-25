from django.test import TestCase, Client
from django.contrib.auth.models import User, Group


class FrontendUIUXTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user('adminui', password='p')
        self.admin.is_staff = True
        self.admin.save()

        self.cond = User.objects.create_user('condui', password='p')
        cond_group, _ = Group.objects.get_or_create(name='Conductor')
        self.cond.groups.add(cond_group)

        self.apod = User.objects.create_user('apodui', password='p')
        apod_group, _ = Group.objects.get_or_create(name='Apoderado')
        self.apod.groups.add(apod_group)

    def test_admin_sees_new_buttons(self):
        self.client.login(username='adminui', password='p')
        r = self.client.get('/colegios/')
        self.assertContains(r, 'Nuevo Colegio')
        r2 = self.client.get('/furgones/')
        self.assertContains(r2, 'Nuevo Furgón')

    def test_non_admin_cannot_see_new_buttons(self):
        self.client.login(username='condui', password='p')
        r = self.client.get('/colegios/')
        self.assertNotContains(r, 'Nuevo Colegio')
        r2 = self.client.get('/furgones/')
        self.assertNotContains(r2, 'Nuevo Furgón')

    def test_apoderado_ui_no_create(self):
        self.client.login(username='apodui', password='p')
        r = self.client.get('/estudiantes/')
        # apoderado should not see 'Nuevo Estudiante' (only admin)
        self.assertNotContains(r, 'Nuevo Estudiante')
