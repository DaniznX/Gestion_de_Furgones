from django.contrib import admin
from .models import (
    Colegio,
    Conductor,
    Furgon,
    Estudiante,
    Ruta,
    Notificacion,
    Pago,
    Asistencia,
)


@admin.register(Colegio)
class ColegioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion", "telefono")


@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "rut",
        "telefono",
        "numero_licencia",
        "user",
    )


@admin.register(Furgon)
class FurgonAdmin(admin.ModelAdmin):
    list_display = (
        "patente",
        "modelo",
        "anio",
        "capacidad_maxima",
        "capacidad_actual",
        "estado_revision_tecnica",
        "conductor",
        "colegio",
    )
    list_filter = ("estado_revision_tecnica", "anio")


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "rut",
        "furgon",
        "nombre_apoderado",
        "apoderado_user",
    )


@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ("id", "furgon", "tipo_ruta", "hora_inicio", "hora_termino")


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("tipo", "estudiante", "furgon", "creado_at", "leido")
    list_filter = ("tipo", "leido")


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        "estudiante",
        "monto",
        "fecha",
        "estado",
        "referencia",
    )
    list_filter = ("estado",)


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ("estudiante", "fecha", "estado", "furgon")
    list_filter = ("estado",)
