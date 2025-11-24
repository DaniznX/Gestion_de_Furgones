from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import Colegio, Conductor, Furgon, Estudiante, Ruta, Notificacion, Pago, Asistencia
from .serializers import (
    ColegioSerializer, ConductorSerializer, FurgonSerializer, EstudianteSerializer,
    RutaSerializer, NotificacionSerializer, PagoSerializer, AsistenciaSerializer
)
from .permissions import IsAdminOrReadOnly, IsAdminOrConductorOrReadOnly, IsAdminOrApoderadoOrConductorOrReadOnly
from .permissions import in_group


class ColegioViewSet(viewsets.ModelViewSet):
    queryset = Colegio.objects.all()
    serializer_class = ColegioSerializer
    permission_classes = [IsAdminOrReadOnly]


class ConductorViewSet(viewsets.ModelViewSet):
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer
    permission_classes = [IsAdminOrReadOnly]


class FurgonViewSet(viewsets.ModelViewSet):
    queryset = Furgon.objects.all()
    serializer_class = FurgonSerializer
    permission_classes = [IsAdminOrConductorOrReadOnly]

    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        """Endpoint para actualizar ubicación GPS del furgón.

        Payload esperado: { "latitude": <float>, "longitude": <float>, "reported_at": "YYYY-MM-DDTHH:MM:SS" (opcional) }
        """
        furgon = self.get_object()
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        reported_at = request.data.get('reported_at')
        if lat is None or lon is None:
            return Response({'detail': 'latitude y longitude son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            return Response({'detail': 'latitude y longitude deben ser números'}, status=status.HTTP_400_BAD_REQUEST)
        if reported_at:
            try:
                reported_at = timezone.datetime.fromisoformat(reported_at)
            except Exception:
                reported_at = timezone.now()
        else:
            reported_at = timezone.now()
        furgon.update_location(latitude=lat, longitude=lon, reported_at=reported_at)
        serializer = self.get_serializer(furgon)
        return Response(serializer.data)


class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiante.objects.all()
    serializer_class = EstudianteSerializer
    permission_classes = [
        # Allow authenticated users to attempt writes; ownership enforced in partial_update
        # by explicit checks.
        
        # Use the permissive class defined for view-level checks
        __import__('core.permissions', fromlist=['']).AllowAuthenticatedWriteOrReadOnly
    ]

    def partial_update(self, request, *args, **kwargs):
        # Custom partial update that enforces ownership without relying on DRF's get_object (which
        # calls object-level permission checks). We retrieve the instance directly and apply
        # ownership rules: Admins can update; Apoderados can update only their own students.
        pk = kwargs.get('pk') or kwargs.get('lookup_value')
        try:
            instance = self.queryset.get(pk=pk)
        except Exception:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        # Admins
        if user and (user.is_staff or in_group(user, 'Administrador')):
            pass
        else:
            # Apoderado owner
            if user and in_group(user, 'Apoderado') and getattr(instance, 'apoderado_user', None) and getattr(instance.apoderado_user, 'pk', None) == getattr(user, 'pk', None):
                pass
            else:
                return Response({'detail': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class RutaViewSet(viewsets.ModelViewSet):
    queryset = Ruta.objects.all()
    serializer_class = RutaSerializer


class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all().order_by('-creado_at')
    serializer_class = NotificacionSerializer

    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        n = self.get_object()
        n.marcar_como_leida()
        return Response({'status': 'ok'})


class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer


class AsistenciaViewSet(viewsets.ModelViewSet):
    queryset = Asistencia.objects.all()
    serializer_class = AsistenciaSerializer
