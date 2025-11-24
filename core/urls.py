from rest_framework import routers
from django.urls import path, include
from . import views

router = routers.DefaultRouter()
router.register(r'colegios', views.ColegioViewSet)
router.register(r'conductores', views.ConductorViewSet)
router.register(r'furgones', views.FurgonViewSet)
router.register(r'estudiantes', views.EstudianteViewSet)
router.register(r'rutas', views.RutaViewSet)
router.register(r'notificaciones', views.NotificacionViewSet)
router.register(r'pagos', views.PagoViewSet)
router.register(r'asistencias', views.AsistenciaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
