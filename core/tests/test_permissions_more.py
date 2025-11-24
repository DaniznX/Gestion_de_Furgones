from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User, Group, AnonymousUser

from core.permissions import (
    in_group,
    IsAdminOrReadOnly,
    IsAdminOrConductorOrReadOnly,
    IsAdminOrApoderadoOrConductorOrReadOnly,
    AllowAuthenticatedWriteOrReadOnly,
)
from core.models import Conductor, Furgon, Estudiante, Colegio


class PermissionsMoreTests(TestCase):
    def setUp(self):
        self.admin_group, _ = Group.objects.get_or_create(name='Administrador')
        self.cond_group, _ = Group.objects.get_or_create(name='Conductor')
        self.apod_group, _ = Group.objects.get_or_create(name='Apoderado')

        self.admin = User.objects.create_user('admin_more', password='a')
        self.admin.is_staff = True
        self.admin.save()

        self.cond_user = User.objects.create_user('cond_more', password='c')
        self.cond_user.groups.add(self.cond_group)

        self.cond_user_no_profile = User.objects.create_user('cond_nop', password='c')
        # note: no Conductor profile attached

        self.apod_user = User.objects.create_user('apod_more', password='p')
        self.apod_user.groups.add(self.apod_group)

        self.cole = Colegio.objects.create(nombre='Cole P')
        self.conductor = Conductor.objects.create(rut='930', nombre='CondP', user=self.cond_user)
        self.furgon = Furgon.objects.create(patente='P-1', conductor=self.conductor, colegio=self.cole)
        self.student = Estudiante.objects.create(rut='700', nombre='Est P', apoderado_user=self.apod_user, furgon=self.furgon)

        self.factory = APIRequestFactory()

    def test_in_group_true(self):
        self.assertTrue(in_group(self.apod_user, 'Apoderado'))

    def test_is_admin_or_readonly_get_allows_anonymous(self):
        perm = IsAdminOrReadOnly()
        req = self.factory.get('/x')
        req.user = AnonymousUser()
        self.assertTrue(perm.has_permission(req, view=None))

    def test_is_admin_or_readonly_post_admin_allowed(self):
        perm = IsAdminOrReadOnly()
        req = self.factory.post('/x')
        req.user = self.admin
        self.assertTrue(perm.has_permission(req, view=None))

    def test_is_admin_or_conductor_has_permission_action_missing_denied(self):
        perm = IsAdminOrConductorOrReadOnly()
        req = self.factory.post('/x')
        req.user = self.cond_user
        # view without action attribute should deny write
        class V: pass
        self.assertFalse(perm.has_permission(req, V()))

    def test_is_admin_or_conductor_object_permission_no_profile(self):
        perm = IsAdminOrConductorOrReadOnly()
        req = self.factory.post('/x/update_location/')
        req.user = self.cond_user_no_profile
        class V: action = 'update_location'
        # user has no conductor_profile, should return False without exception
        self.assertFalse(perm.has_object_permission(req, V(), self.furgon))

    def test_is_admin_or_apoderado_write_denied_at_view_level(self):
        perm = IsAdminOrApoderadoOrConductorOrReadOnly()
        req = self.factory.post('/api/estudiantes/')
        req.user = self.apod_user
        self.assertFalse(perm.has_permission(req, view=None))

    def test_is_admin_or_apoderado_write_denied_for_conductor(self):
        perm = IsAdminOrApoderadoOrConductorOrReadOnly()
        req = self.factory.patch(f'/api/estudiantes/{self.student.id}/')
        req.user = self.cond_user
        # conductor should not be allowed to write student objects
        self.assertFalse(perm.has_object_permission(req, view=None, obj=self.student))

    def test_allow_authenticated_object_permission_behaviour(self):
        perm = AllowAuthenticatedWriteOrReadOnly()
        req = self.factory.patch('/x')
        req.user = self.apod_user
        self.assertTrue(perm.has_object_permission(req, view=None, obj=self.student))
        req2 = self.factory.patch('/x')
        req2.user = AnonymousUser()
        self.assertFalse(perm.has_object_permission(req2, view=None, obj=self.student))
