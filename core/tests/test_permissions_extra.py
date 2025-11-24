from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User, Group, AnonymousUser

from core.permissions import (
    IsAdminOrReadOnly,
    IsAdminOrConductorOrReadOnly,
    IsAdminOrApoderadoOrConductorOrReadOnly,
)
from core.models import Conductor, Furgon, Estudiante, Colegio


class PermissionsExtraTests(TestCase):
    def setUp(self):
        self.cond_group, _ = Group.objects.get_or_create(name='Conductor')
        self.apod_group, _ = Group.objects.get_or_create(name='Apoderado')

        self.cond_user = User.objects.create_user('cond_ex', password='c')
        self.cond_user.groups.add(self.cond_group)

        self.apod_user = User.objects.create_user('apod_ex', password='p')
        self.apod_user.groups.add(self.apod_group)

        self.cole = Colegio.objects.create(nombre='Cole X')
        self.conductor = Conductor.objects.create(rut='940', nombre='CondX', user=self.cond_user)
        self.furgon = Furgon.objects.create(patente='X-1', conductor=self.conductor, colegio=self.cole)
        self.student = Estudiante.objects.create(rut='600', nombre='EstX', apoderado_user=self.apod_user, furgon=self.furgon)

        self.factory = APIRequestFactory()

    def test_is_admin_or_readonly_allows_conductor_write(self):
        perm = IsAdminOrReadOnly()
        req = self.factory.post('/x')
        req.user = self.cond_user
        self.assertTrue(perm.has_permission(req, view=None))

    def test_is_admin_or_conductor_has_permission_action_allowed(self):
        perm = IsAdminOrConductorOrReadOnly()
        req = self.factory.post('/x')
        req.user = self.cond_user
        class V: action = 'update_location'
        self.assertTrue(perm.has_permission(req, V()))

    def test_is_admin_or_conductor_has_permission_action_not_allowed(self):
        perm = IsAdminOrConductorOrReadOnly()
        req = self.factory.post('/x')
        req.user = self.cond_user
        class V: action = 'patch'
        self.assertFalse(perm.has_permission(req, V()))

    def test_is_admin_or_conductor_object_permission_allows_safe_methods(self):
        perm = IsAdminOrConductorOrReadOnly()
        req = self.factory.get('/x')
        req.user = AnonymousUser()
        self.assertTrue(perm.has_object_permission(req, view=None, obj=self.furgon))

    def test_is_admin_or_apoderado_safe_get_allows_anonymous(self):
        perm = IsAdminOrApoderadoOrConductorOrReadOnly()
        req = self.factory.get(f'/api/estudiantes/{self.student.id}/')
        req.user = AnonymousUser()
        self.assertTrue(perm.has_object_permission(req, view=None, obj=self.student))
