import os
import sys
import pathlib

# Ensure project root is on sys.path
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_furgones.settings')
import django

django.setup()

from core.models import Ruta, Estudiante, Furgon, Asistencia
from django.utils import timezone
from datetime import date

# Seed some Temuco localities in routes
rutas = [
    {
        'tipo_ruta': 'ida',
        'hora_inicio': None,
        'hora_termino': None,
        'localidades': 'Estadio Germán Becker, Plaza Aníbal Pinto, Universidad de La Frontera',
    },
    {
        'tipo_ruta': 'ida',
        'hora_inicio': None,
        'hora_termino': None,
        'localidades': 'Terminal de Buses, Mall Portal Temuco, Avenida Alemania',
    },
    {
        'tipo_ruta': 'vuelta',
        'hora_inicio': None,
        'hora_termino': None,
        'localidades': 'Estadio Germán Becker, Barrio Norte, Plaza Dagoberto Godoy',
    },
]

created = []
for rdata in rutas:
    r, created_flag = Ruta.objects.get_or_create(
        localidades=rdata['localidades'],
        defaults={
            'tipo_ruta': rdata['tipo_ruta'],
            'hora_inicio': rdata['hora_inicio'],
            'hora_termino': rdata['hora_termino'],
        },
    )
    created.append((r, created_flag))

print('Rutas creadas/aseguradas:')
for r, c in created:
    print('-', r.pk, r.localidades)

# Create a test student if not exists
est_rut = '99999999-9'
student, s_created = Estudiante.objects.get_or_create(
    rut=est_rut,
    defaults={
        'nombre': 'Estudiante Prueba',
        'direccion': 'Temuco',
    },
)
print('Estudiante:', student.pk, student.nombre, '(created)' if s_created else '(exists)')

# Assign to a furgon if any exists
any_furgon = Furgon.objects.first()
if any_furgon and not student.furgon:
    student.furgon = any_furgon
    student.save()
    print('Asignado a furgon', any_furgon.patente)

# Create asistencia for today
today = date.today()
asis, a_created = Asistencia.objects.get_or_create(
    estudiante=student,
    fecha=today,
    defaults={'estado': 'presente', 'furgon': student.furgon},
)
print('Asistencia:', asis.pk, asis.estado, '(created)' if a_created else '(exists)')
