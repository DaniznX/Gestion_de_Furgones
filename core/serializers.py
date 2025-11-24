from rest_framework import serializers
from .models import Colegio, Conductor, Furgon, Estudiante, Ruta, Notificacion, Pago, Asistencia


class ColegioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colegio
        fields = '__all__'


class ConductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conductor
        fields = '__all__'


class FurgonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Furgon
        fields = '__all__'


class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudiante
        fields = '__all__'


class RutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruta
        fields = '__all__'


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'


class AsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asistencia
        fields = '__all__'
