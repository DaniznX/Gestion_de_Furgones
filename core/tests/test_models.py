from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError

from core.models import (
    Colegio, Conductor, Furgon, Estudiante, Notificacion,
    Pago, Asistencia, Ruta
)
from django.contrib.auth.models import User


class ModelsTests(TestCase):
    def setUp(self):
        self.colegio = Colegio.objects.create(nombre='Cole Model')
        self.user = User.objects.create_user('u1', password='p')
        self.conductor = Conductor.objects.create(rut='123', nombre='Cond', user=self.user)

    def test_furgon_ocupacion_and_capacidad(self):
        f = Furgon.objects.create(
            patente='M1',
            capacidad_maxima=10,
            capacidad_actual=5,
            conductor=self.conductor,
            colegio=self.colegio,
        )
        self.assertEqual(f.calcular_ocupacion(), 50.0)
        self.assertTrue(f.verificar_capacidad_disponible())

        f.capacidad_actual = 10
        f.save()
        self.assertFalse(f.verificar_capacidad_disponible())

        f_zero = Furgon.objects.create(
            patente='ZERO',
            capacidad_maxima=0,
            capacidad_actual=5,
            conductor=self.conductor,
            colegio=self.colegio,
        )
        self.assertEqual(f_zero.calcular_ocupacion(), 0)

    def test_update_location_with_and_without_reported_at(self):
        f = Furgon.objects.create(
            patente='LOC1',
            conductor=self.conductor,
            colegio=self.colegio,
        )
        # without reported_at
        f.update_location(latitude=-33.45, longitude=-70.66)
        self.assertIsNotNone(f.last_latitude)
        self.assertIsNotNone(f.last_reported_at)

        # with reported_at
        now = timezone.now()
        f.update_location(latitude=1.23, longitude=4.56, reported_at=now)
        self.assertEqual(f.last_latitude, 1.23)
        # allow small delta or equality depending on timezone handling
        self.assertEqual(f.last_reported_at.replace(microsecond=0), now.replace(microsecond=0))

    def test_notificacion_str_and_mark_read(self):
        f = Furgon.objects.create(
            patente='NOTF',
            conductor=self.conductor,
            colegio=self.colegio,
        )
        student = Estudiante.objects.create(
            rut='900',
            nombre='Stud',
            apoderado_user=self.user,
            furgon=f,
        )
        n1 = Notificacion.objects.create(tipo='info', mensaje='Hello', estudiante=student)
        self.assertIn('Stud', str(n1))
        n1.marcar_como_leida()
        self.assertTrue(Notificacion.objects.get(pk=n1.pk).leido)

        n2 = Notificacion.objects.create(tipo='alert', mensaje='Furgon alert', furgon=f)
        self.assertIn('Furgon', str(n2))

        n3 = Notificacion.objects.create(tipo='evento', mensaje='General')
        self.assertIn('General', str(n3) or 'General')

    def test_pago_and_asistencia_and_strs(self):
        f = Furgon.objects.create(
            patente='PAYF',
            conductor=self.conductor,
            colegio=self.colegio,
        )
        student = Estudiante.objects.create(
            rut='910',
            nombre='Aluno',
            apoderado_user=self.user,
            furgon=f,
        )
        pago = Pago.objects.create(estudiante=student, monto='1500.00', estado='pendiente')
        self.assertIn('Pago', str(pago))

        # Asistencia unique constraint
        a1 = Asistencia.objects.create(estudiante=student, fecha=timezone.now().date(), estado='presente', furgon=f)
        self.assertIn('Asistencia', str(a1))
        with self.assertRaises(IntegrityError):
            # creating same estudiante+fecha should violate unique_together
            Asistencia.objects.create(estudiante=student, fecha=a1.fecha, estado='ausente', furgon=f)

    def test_simple_strs(self):
        c = Colegio.objects.get(pk=self.colegio.pk)
        self.assertIn('Cole', str(c))
        self.assertIn('Cond', str(self.conductor))
        inner_f = Furgon.objects.create(
            patente='R1',
            conductor=self.conductor,
            colegio=self.colegio,
        )
        r = Ruta.objects.create(furgon=inner_f, tipo_ruta='ida')
        self.assertIn('Ruta', str(r))
