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


class PermissionAdditionalTests(TestCase):
    def setUp(self):
        # Groups
        self.admin_group, _ = Group.objects.get_or_create(name='Administrador')
        self.cond_group, _ = Group.objects.get_or_create(name='Conductor')
        self.apod_group, _ = Group.objects.get_or_create(name='Apoderado')

        # Users
        self.cond_user = User.objects.create_user('cond_extra', password='condpass')
        self.cond_user.groups.add(self.cond_group)

        self.cond_user2 = User.objects.create_user('cond_other', password='condpass')
        self.cond_user2.groups.add(self.cond_group)

        self.apod_user = User.objects.create_user('apod_extra', password='apodpass')
        self.apod_user.groups.add(self.apod_group)

        # Colegio
        self.colegio = Colegio.objects.create(nombre='Cole Extra')

        # Conductor profiles and furgones
        self.conductor = Conductor.objects.create(rut='91000000-0', nombre='Cond Extra', user=self.cond_user)
        self.conductor2 = Conductor.objects.create(rut='92000000-0', nombre='Cond Other', user=self.cond_user2)

        self.furgon_own = Furgon.objects.create(patente='OWN-1', modelo='M', capacidad_maxima=10, conductor=self.conductor, colegio=self.colegio)
        self.furgon_other = Furgon.objects.create(patente='OTH-1', modelo='M', capacidad_maxima=10, conductor=self.conductor2, colegio=self.colegio)

        # Student assigned to furgon_own
        self.student = Estudiante.objects.create(rut='83000000-3', nombre='Stud Extra', apoderado_user=self.apod_user, furgon=self.furgon_own)

        self.factory = APIRequestFactory()

    def test_in_group_with_anonymous(self):
        anon = AnonymousUser()
        self.assertFalse(in_group(anon, 'Apoderado'))

    def test_is_admin_or_readonly_allows_apoderado_for_write(self):
        perm = IsAdminOrReadOnly()
        request = self.factory.post('/fake/', {}, format='json')
        request.user = self.apod_user
        self.assertTrue(perm.has_permission(request, view=None))

    def test_is_admin_or_readonly_denies_anonymous_write(self):
        perm = IsAdminOrReadOnly()
        request = self.factory.post('/fake/', {}, format='json')
        request.user = AnonymousUser()
        self.assertFalse(perm.has_permission(request, view=None))

    def test_is_admin_or_conductor_object_permission_update_location_own(self):
        perm = IsAdminOrConductorOrReadOnly()
        request = self.factory.post('/fake/1/update_location/')
        request.user = self.cond_user
        # create a fake view with action attribute
        class V: action = 'update_location'

        self.assertTrue(perm.has_object_permission(request, V(), self.furgon_own))

    def test_is_admin_or_conductor_object_permission_update_location_not_owner(self):
        perm = IsAdminOrConductorOrReadOnly()
        request = self.factory.post('/fake/2/update_location/')
        request.user = self.cond_user

        class V: action = 'update_location'

        self.assertFalse(perm.has_object_permission(request, V(), self.furgon_other))

    def test_is_admin_or_apoderado_conductor_read_safe(self):
        perm = IsAdminOrApoderadoOrConductorOrReadOnly()
        request = self.factory.get(f'/api/estudiantes/{self.student.id}/')
        request.user = self.cond_user
        # conductor reading student assigned to his furgon should be allowed
        self.assertTrue(perm.has_object_permission(request, view=None, obj=self.student))

    def test_allow_authenticated_write_or_readonly(self):
        perm = AllowAuthenticatedWriteOrReadOnly()
        req_auth = self.factory.post('/fake/')
        req_auth.user = self.apod_user
        req_anon = self.factory.post('/fake/')
        req_anon.user = AnonymousUser()

        self.assertTrue(perm.has_permission(req_auth, view=None))
        self.assertFalse(perm.has_permission(req_anon, view=None))

    def test_is_admin_or_apoderado_allows_patch_when_owner(self):
        perm = IsAdminOrApoderadoOrConductorOrReadOnly()
        req = self.factory.patch(f'/api/estudiantes/{self.student.id}/')
        req.user = self.apod_user
        # apoderado owner should be allowed to write
        self.assertTrue(perm.has_object_permission(req, view=None, obj=self.student))

    def test_is_admin_or_apoderado_denies_patch_when_not_owner(self):
        perm = IsAdminOrApoderadoOrConductorOrReadOnly()
        other_student = Estudiante.objects.create(rut='84000000-4', nombre='Other', furgon=self.furgon_own)
        req = self.factory.patch(f'/api/estudiantes/{other_student.id}/')
        req.user = self.apod_user
        self.assertFalse(perm.has_object_permission(req, view=None, obj=other_student))
