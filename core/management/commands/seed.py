from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from core.models import Colegio, Conductor, Furgon, Estudiante, Ruta
from django.utils import timezone


def create_user_if_not_exists(username, email, password, groups=None):
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    if created:
        user.set_password(password)
        user.save()
    if groups:
        for g in groups:
            grp, _ = Group.objects.get_or_create(name=g)
            user.groups.add(grp)
    return user


class Command(BaseCommand):
    help = 'Crea datos de ejemplo y grupos/roles básicos'

    def handle(self, *args, **options):
        # Grupos
        for g in [
                'Administrador',
                'Conductor',
                'Apoderado',
        ]:
            group, created = Group.objects.get_or_create(name=g)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Grupo creado: {g}'))

        # Superusuario de ejemplo
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
            self.stdout.write(self.style.SUCCESS('Superusuario admin creado (usuario: admin, pass: adminpass)'))

        # Colegio
        colegio, _ = Colegio.objects.get_or_create(
            nombre='Colegio Ejemplo',
            defaults={
                'direccion': 'Calle Falsa 123',
                'telefono': '+56912345678',
            },
        )

        # Conductores
        cond1, _ = Conductor.objects.get_or_create(
            rut='11111111-1',
            defaults={
                'nombre': 'Juan Perez',
                'telefono': '+56911111111',
            },
        )

        cond2, _ = Conductor.objects.get_or_create(
            rut='22222222-2',
            defaults={
                'nombre': 'Ana Soto',
                'telefono': '+56922222222',
            },
        )

        # Furgones
        f1, _ = Furgon.objects.get_or_create(
            patente='ABC-123',
            defaults={
                'modelo': 'Toyota Hiace',
                'anio': 2018,
                'capacidad_maxima': 16,
                'conductor': cond1,
                'colegio': colegio,
            },
        )

        f2, _ = Furgon.objects.get_or_create(
            patente='XYZ-987',
            defaults={
                'modelo': 'Nissan NV200',
                'anio': 2020,
                'capacidad_maxima': 12,
                'conductor': cond2,
                'colegio': colegio,
            },
        )

        # Rutas
        r1, _ = Ruta.objects.get_or_create(
            furgon=f1,
            tipo_ruta='ida',
            defaults={
                'hora_inicio': timezone.datetime.strptime('07:30', '%H:%M').time(),
                'hora_termino': timezone.datetime.strptime('08:00', '%H:%M').time(),
            },
        )

        r2, _ = Ruta.objects.get_or_create(
            furgon=f2,
            tipo_ruta='vuelta',
            defaults={
                'hora_inicio': timezone.datetime.strptime('15:00', '%H:%M').time(),
                'hora_termino': timezone.datetime.strptime('15:30', '%H:%M').time(),
            },
        )

        # Crear usuarios para conductores y asignarlos
        user_cond1 = create_user_if_not_exists(
            username='11111111-1',
            email='juan@example.com',
            password='condpass1',
            groups=['Conductor'],
        )

        user_cond2 = create_user_if_not_exists(
            username='22222222-2',
            email='ana@example.com',
            password='condpass2',
            groups=['Conductor'],
        )
        cond1.user = user_cond1
        cond1.save()
        cond2.user = user_cond2
        cond2.save()

        # Crear usuarios apoderados y estudiantes asignados
        apod1 = create_user_if_not_exists(
            username='maria.gomez',
            email='maria@example.com',
            password='apodpass1',
            groups=['Apoderado'],
        )

        apod2 = create_user_if_not_exists(
            username='carlos.torres',
            email='carlos@example.com',
            password='apodpass2',
            groups=['Apoderado'],
        )

        Estudiante.objects.get_or_create(
            rut='33333333-3',
            defaults={
                'nombre': 'Pedro Gomez',
                'telefono': '56933333333',
                'nombre_apoderado': 'Maria Gomez',
                'telefono_apoderado': '56944444444',
                'furgon': f1,
                'apoderado_user': apod1,
            },
        )

        Estudiante.objects.get_or_create(
            rut='44444444-4',
            defaults={
                'nombre': 'Lucia Torres',
                'telefono': '56955555555',
                'nombre_apoderado': 'Carlos Torres',
                'telefono_apoderado': '56966666666',
                'furgon': f2,
                'apoderado_user': apod2,
            },
        )

        self.stdout.write(self.style.SUCCESS('Seed completado.'))
