from django.db import models
from django.conf import settings
from django.urls import reverse


class Colegio(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    horario_entrada = models.TimeField(null=True, blank=True)
    horario_salida = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('frontend:colegio_edit', args=[self.pk])

    def get_edit_url(self):
        return self.get_absolute_url()


class Conductor(models.Model):
    rut = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=255)
    telefono = models.CharField(max_length=50, blank=True)
    numero_licencia = models.CharField(max_length=100, blank=True)
    tipo_licencia = models.CharField(max_length=50, blank=True)
    fecha_vencimiento_licencia = models.DateField(null=True, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='conductor_profile',
    )

    def __str__(self):
        return f"{self.nombre} ({self.rut})"

    def get_absolute_url(self):
        return reverse('frontend:conductor_edit', args=[self.pk])

    def get_edit_url(self):
        return self.get_absolute_url()


class Furgon(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('mantenimiento', 'En mantenimiento'),
    ]

    patente = models.CharField(max_length=50, unique=True)
    modelo = models.CharField(max_length=100, blank=True)
    anio = models.PositiveIntegerField(null=True, blank=True)
    capacidad_maxima = models.PositiveIntegerField(default=20)
    capacidad_actual = models.PositiveIntegerField(default=0)
    estado_revision_tecnica = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='activo')
    fecha_revision_tecnica = models.DateField(null=True, blank=True)
    conductor = models.ForeignKey(Conductor, null=True, blank=True, on_delete=models.SET_NULL, related_name='furgones')
    colegio = models.ForeignKey(Colegio, null=True, blank=True, on_delete=models.SET_NULL, related_name='furgones')
    # Campos para seguimiento en tiempo real (GPS)
    last_latitude = models.FloatField(null=True, blank=True)
    last_longitude = models.FloatField(null=True, blank=True)
    last_reported_at = models.DateTimeField(null=True, blank=True)
    estado_actual = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.patente

    def get_absolute_url(self):
        return reverse('frontend:furgon_edit', args=[self.pk])

    def get_edit_url(self):
        return self.get_absolute_url()

    def calcular_ocupacion(self):
        if self.capacidad_maxima == 0:
            return 0
        return (self.capacidad_actual / self.capacidad_maxima) * 100

    def verificar_capacidad_disponible(self):
        return self.capacidad_actual < self.capacidad_maxima

    def update_location(self, latitude: float, longitude: float, reported_at=None):
        """Actualiza la ubicación del furgón (no hace integración con GPS, solo guarda los datos)."""
        self.last_latitude = latitude
        self.last_longitude = longitude
        if reported_at:
            self.last_reported_at = reported_at
        from django.utils import timezone
        if not self.last_reported_at:
            self.last_reported_at = timezone.now()
        self.save()


class Estudiante(models.Model):
    rut = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    nombre_apoderado = models.CharField(max_length=255, blank=True)
    telefono_apoderado = models.CharField(max_length=50, blank=True)
    furgon = models.ForeignKey(
        Furgon,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='estudiantes',
    )
    apoderado_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='apoderado_estudiantes',
    )

    def __str__(self):
        return f"{self.nombre} ({self.rut})"

    def get_absolute_url(self):
        return reverse('frontend:estudiante_edit', args=[self.pk])

    def get_edit_url(self):
        return self.get_absolute_url()


class Notificacion(models.Model):
    TIPOS = [
        ('info', 'Información'),
        ('alert', 'Alerta'),
        ('evento', 'Evento'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPOS, default='info')
    mensaje = models.TextField()
    estudiante = models.ForeignKey(
        Estudiante,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='notificaciones',
    )
    furgon = models.ForeignKey(
        Furgon,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='notificaciones',
    )
    creado_at = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        target = self.estudiante.nombre if self.estudiante else (self.furgon.patente if self.furgon else 'General')
        return f"[{self.get_tipo_display()}] {target} - {self.mensaje[:40]}"

    def marcar_como_leida(self):
        self.leido = True
        self.save()


class Pago(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
    ]
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    fecha = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    referencia = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Pago {self.pk} - {self.estudiante.nombre} - {self.monto} ({self.estado})"

    def get_absolute_url(self):
        return reverse('frontend:pago_list')

    def get_edit_url(self):
        return self.get_absolute_url()


class Asistencia(models.Model):
    ESTADO_ASIS = [
        ('presente', 'Presente'),
        ('recogido', 'Recogido'),
        ('entregado', 'Entregado'),
        ('ausente', 'Ausente'),
    ]
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_ASIS)
    furgon = models.ForeignKey(Furgon, null=True, blank=True, on_delete=models.SET_NULL, related_name='asistencias')

    class Meta:
        unique_together = ('estudiante', 'fecha')

    def __str__(self):
        return f"Asistencia {self.estudiante.nombre} - {self.fecha} - {self.estado}"

    def get_absolute_url(self):
        return reverse('frontend:asistencia_list')

    def get_edit_url(self):
        return self.get_absolute_url()


class Ruta(models.Model):
    TIPOS = [
        ('ida', 'Ida'),
        ('vuelta', 'Vuelta'),
        ('completa', 'Completa'),
    ]
    furgon = models.ForeignKey(Furgon, null=True, blank=True, on_delete=models.SET_NULL, related_name='rutas')
    tipo_ruta = models.CharField(max_length=20, choices=TIPOS, default='ida')
    localidades = models.CharField(max_length=500, blank=True, help_text='Lista de localidades / paradas separadas por comas')
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_termino = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Ruta {self.pk} - {self.tipo_ruta}"

    def get_absolute_url(self):
        return reverse('frontend:ruta_edit', args=[self.pk])

    def get_edit_url(self):
        return self.get_absolute_url()
