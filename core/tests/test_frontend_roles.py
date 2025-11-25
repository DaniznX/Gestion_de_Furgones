from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from core.models import Colegio, Conductor, Furgon, Estudiante, Notificacion


class FrontendRoleTests(TestCase):
    def setUp(self):
        # groups
        self.admin_group, _ = Group.objects.get_or_create(name='Administrador')
        self.cond_group, _ = Group.objects.get_or_create(name='Conductor')
        self.apod_group, _ = Group.objects.get_or_create(name='Apoderado')

        # users
        self.cond_user1 = User.objects.create_user('cond1', password='p')
        self.cond_user1.groups.add(self.cond_group)
        self.cond_user2 = User.objects.create_user('cond2', password='p')
        self.cond_user2.groups.add(self.cond_group)

        self.apod_user = User.objects.create_user('apod1', password='p')
        self.apod_user.groups.add(self.apod_group)
        self.apod_user2 = User.objects.create_user('apod2', password='p')
        self.apod_user2.groups.add(self.apod_group)

        self.admin = User.objects.create_user('adm', password='p')
        self.admin.is_staff = True
        self.admin.save()

        self.cole = Colegio.objects.create(nombre='C-Rol')

        # conductors/profiles
        self.conductor1 = Conductor.objects.create(rut='111', nombre='C1', user=self.cond_user1)
        self.conductor2 = Conductor.objects.create(rut='222', nombre='C2', user=self.cond_user2)

        self.f1 = Furgon.objects.create(patente='FC1', conductor=self.conductor1, colegio=self.cole)
        self.f2 = Furgon.objects.create(patente='FC2', conductor=self.conductor2, colegio=self.cole)

        # students
        self.s1 = Estudiante.objects.create(rut='s1', nombre='S1', apoderado_user=self.apod_user, furgon=self.f1)
        self.s2 = Estudiante.objects.create(rut='s2', nombre='S2', apoderado_user=self.apod_user2, furgon=self.f2)

        # notifications
        self.n1 = Notificacion.objects.create(tipo='info', mensaje='for s1', estudiante=self.s1)
        self.n2 = Notificacion.objects.create(tipo='info', mensaje='for s2', estudiante=self.s2)

        self.client = Client()

    def test_conductor_sees_own_furgon_only(self):
        self.client.login(username='cond1', password='p')
        r = self.client.get('/furgones/')
        content = r.content.decode()
        self.assertIn('FC1', content)
        self.assertNotIn('FC2', content)

    def test_apoderado_sees_only_own_students(self):
        self.client.login(username='apod1', password='p')
        r = self.client.get('/estudiantes/')
        content = r.content.decode()
        self.assertIn('S1', content)
        self.assertNotIn('S2', content)

    def test_apoderado_cannot_mark_other_notification(self):
        self.client.login(username='apod1', password='p')
        # try to mark n2 (not own) as read
        r = self.client.post(f'/notificaciones/{self.n2.pk}/marcar_leida/')
        # should be redirected back to notificacion list and not allowed
        self.assertIn(r.status_code, (302, 302))
        self.n2.refresh_from_db()
        self.assertFalse(self.n2.leido)

    def test_apoderado_can_mark_own_notification(self):
        self.client.login(username='apod1', password='p')
        r = self.client.post(f'/notificaciones/{self.n1.pk}/marcar_leida/')
        self.assertIn(r.status_code, (302, 302))
        self.n1.refresh_from_db()
        self.assertTrue(self.n1.leido)
