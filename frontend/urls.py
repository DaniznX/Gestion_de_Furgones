from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='frontend/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='frontend:login'), name='logout'),

    path('colegios/', views.ColegioList.as_view(), name='colegio_list'),
    path('colegios/new/', views.ColegioCreate.as_view(), name='colegio_create'),
    path('colegios/<int:pk>/', views.ColegioDetail.as_view(), name='colegio_detail'),
    path('colegios/<int:pk>/edit/', views.ColegioUpdate.as_view(), name='colegio_edit'),

    path('conductores/', views.ConductorList.as_view(), name='conductor_list'),
    path('conductores/new/', views.ConductorCreate.as_view(), name='conductor_create'),
    path('conductores/<int:pk>/', views.ConductorDetail.as_view(), name='conductor_detail'),
    path('conductores/<int:pk>/edit/', views.ConductorUpdate.as_view(), name='conductor_edit'),

    path('furgones/', views.FurgonList.as_view(), name='furgon_list'),
    path('furgones/new/', views.FurgonCreate.as_view(), name='furgon_create'),
    path('furgones/<int:pk>/edit/', views.FurgonUpdate.as_view(), name='furgon_edit'),
    path('furgones/<int:pk>/', views.FurgonDetail.as_view(), name='furgon_detail'),
    path('furgones/<int:pk>/update_location/', views.furgon_update_location, name='furgon_update_location'),
    path('mi-furgon/', views.FurgonMineView.as_view(), name='mi_furgon'),

    path('estudiantes/', views.EstudianteList.as_view(), name='estudiante_list'),
    path('estudiantes/new/', views.EstudianteCreate.as_view(), name='estudiante_create'),
    path('estudiantes/<int:pk>/edit/', views.EstudianteUpdate.as_view(), name='estudiante_edit'),
    path('estudiantes/<int:pk>/', views.EstudianteDetail.as_view(), name='estudiante_detail'),

    path('rutas/', views.RutaList.as_view(), name='ruta_list'),
    path('rutas/new/', views.RutaCreate.as_view(), name='ruta_create'),
    path('rutas/<int:pk>/', views.RutaDetail.as_view(), name='ruta_detail'),
    path('rutas/<int:pk>/edit/', views.RutaUpdate.as_view(), name='ruta_edit'),

    path('notificaciones/', views.NotificacionList.as_view(), name='notificacion_list'),
    path('notificaciones/new/', views.NotificacionCreate.as_view(), name='notificacion_create'),
    path('notificaciones/<int:pk>/marcar_leida/', views.notificacion_mark_read, name='notificacion_mark_read'),
    path('notificaciones/<int:pk>/', views.NotificacionDetail.as_view(), name='notificacion_detail'),

    path('pagos/', views.PagoList.as_view(), name='pago_list'),
    path('pagos/new/', views.PagoCreate.as_view(), name='pago_create'),
    path('pagos/<int:pk>/', views.PagoDetail.as_view(), name='pago_detail'),

    path('asistencias/', views.AsistenciaList.as_view(), name='asistencia_list'),
    path('asistencias/new/', views.AsistenciaCreate.as_view(), name='asistencia_create'),
    path('asistencias/<int:pk>/', views.AsistenciaDetail.as_view(), name='asistencia_detail'),
]
