from django import forms
from core.models import Colegio, Conductor, Furgon, Estudiante, Ruta, Notificacion, Pago, Asistencia


class ColegioForm(forms.ModelForm):
    class Meta:
        model = Colegio
        fields = '__all__'


class ConductorForm(forms.ModelForm):
    class Meta:
        model = Conductor
        fields = '__all__'


class FurgonForm(forms.ModelForm):
    class Meta:
        model = Furgon
        fields = '__all__'


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = '__all__'


class RutaForm(forms.ModelForm):
    class Meta:
        model = Ruta
        fields = '__all__'


class NotificacionForm(forms.ModelForm):
    class Meta:
        model = Notificacion
        fields = '__all__'


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = '__all__'


class AsistenciaForm(forms.ModelForm):
    class Meta:
        model = Asistencia
        fields = '__all__'
