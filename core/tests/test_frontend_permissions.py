from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from core.models import Colegio, Conductor, Furgon, Estudiante


class FrontendPermissionsTests(TestCase):
    def setUp(self):
        self.client = Client()
        admin = User.objects.create_user('adminp', password='p')
        admin.is_staff = True
        admin.save()

        cond_group, _ = Group.objects.get_or_create(name='Conductor')
        apod_group, _ = Group.objects.get_or_create(name='Apoderado')

        self.cond1 = User.objects.create_user('condp1', password='p')
        self.cond1.groups.add(cond_group)
        self.cond2 = User.objects.create_user('condp2', password='p')
        self.cond2.groups.add(cond_group)

        self.apod = User.objects.create_user('apodp', password='p')
        self.apod.groups.add(apod_group)

        self.cole = Colegio.objects.create(nombre='Cole P2')
        self.c1 = Conductor.objects.create(rut='c1', nombre='C1', user=self.cond1)
        self.c2 = Conductor.objects.create(rut='c2', nombre='C2', user=self.cond2)
        self.f1 = Furgon.objects.create(patente='FP1', conductor=self.c1, colegio=self.cole)
        self.f2 = Furgon.objects.create(patente='FP2', conductor=self.c2, colegio=self.cole)

        self.s1 = Estudiante.objects.create(rut='se1', nombre='S1', apoderado_user=self.apod, furgon=self.f1)

    def test_non_admin_cannot_access_admin_create(self):
        self.client.login(username='condp1', password='p')
        r = self.client.get('/colegios/new/')
        self.assertEqual(r.status_code, 403)

    def test_conductor_can_edit_own_furgon_but_not_other(self):
        self.client.login(username='condp1', password='p')
        r_ok = self.client.get(f'/furgones/{self.f1.pk}/edit/')
        self.assertEqual(r_ok.status_code, 200)
        r_no = self.client.get(f'/furgones/{self.f2.pk}/edit/')
        self.assertEqual(r_no.status_code, 403)

    def test_apoderado_cannot_create_student(self):
        self.client.login(username='apodp', password='p')
        r = self.client.get('/estudiantes/new/')
        self.assertEqual(r.status_code, 403)

    def test_apoderado_can_access_edit_own_student(self):
        self.client.login(username='apodp', password='p')
        r = self.client.get(f'/estudiantes/{self.s1.pk}/edit/')
        self.assertEqual(r.status_code, 200)
