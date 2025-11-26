from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import DetailView
from django.db.models import Count, Q

from core.models import Colegio, Conductor, Furgon, Estudiante, Ruta, Notificacion, Pago, Asistencia
from core.permissions import in_group
from .forms import (
    ColegioForm, ConductorForm, FurgonForm, EstudianteForm, RutaForm,
    NotificacionForm, PagoForm, AsistenciaForm
)


class IndexView(TemplateView):
    template_name = 'frontend/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        # Global counts
        ctx['count_furgones'] = Furgon.objects.count()
        ctx['count_colegios'] = Colegio.objects.count()
        ctx['count_conductores'] = Conductor.objects.count()
        ctx['count_estudiantes'] = Estudiante.objects.count()
        ctx['count_rutas'] = Ruta.objects.count()
        ctx['count_pagos'] = Pago.objects.count()
        ctx['count_asistencias'] = Asistencia.objects.count()
        # user-specific counts
        if user and user.is_authenticated and in_group(user, 'Conductor'):
            ctx['count_my_furgones'] = Furgon.objects.filter(conductor__user=user).count()
        else:
            ctx['count_my_furgones'] = 0
        if user and user.is_authenticated:
            # unread notifications relevant to user
            if in_group(user, 'Apoderado'):
                qs = Notificacion.objects.filter(
                    estudiante__apoderado_user=user,
                    leido=False,
                )
                ctx['count_unread_notifications'] = qs.count()
            elif in_group(user, 'Conductor'):
                qs = Notificacion.objects.filter(
                    furgon__conductor__user=user,
                    leido=False,
                )
                ctx['count_unread_notifications'] = qs.count()
            else:
                ctx['count_unread_notifications'] = Notificacion.objects.filter(leido=False).count()
        else:
            ctx['count_unread_notifications'] = 0
        # top colegios by furgones
        ctx['top_colegios'] = (
            Colegio.objects.annotate(num_furgones=Count('furgones'))
            .order_by('-num_furgones')[:5]
        )
        return ctx


class ColegioList(LoginRequiredMixin, ListView):
    model = Colegio
    template_name = 'frontend/colegio_list.html'
    paginate_by = 20
    ordering = ['nombre']

    def get_queryset(self):
        qs = super().get_queryset().order_by('nombre')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user and (user.is_staff or in_group(user, 'Administrador'))


class ColegioCreate(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Colegio
    form_class = ColegioForm
    template_name = 'frontend/form.html'
    success_url = reverse_lazy('frontend:colegio_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Colegio creado correctamente.')
        return response


class ColegioUpdate(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Colegio
    form_class = ColegioForm
    template_name = 'frontend/form.html'
    success_url = reverse_lazy('frontend:colegio_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Colegio actualizado correctamente.')
        return response


class ConductorList(LoginRequiredMixin, ListView):
    model = Conductor
    template_name = 'frontend/conductor_list.html'
    paginate_by = 20
    ordering = ['nombre']

    def get_queryset(self):
        qs = super().get_queryset().order_by('nombre')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(rut__icontains=q))
        return qs


class ConductorCreate(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Conductor
    form_class = ConductorForm
    template_name = 'frontend/form.html'
    success_url = reverse_lazy('frontend:conductor_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Conductor creado correctamente.')
        return response


class ConductorUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Conductor
    form_class = ConductorForm
    template_name = 'frontend/form.html'
    success_url = reverse_lazy('frontend:conductor_list')

    def test_func(self):
        user = self.request.user
        # admins allowed
        if user and (user.is_staff or in_group(user, 'Administrador')):
            return True
        # conductor can edit their own profile
        obj = self.get_object()
        return getattr(obj, 'user', None) == user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Conductor actualizado correctamente.')
        return response


class FurgonList(LoginRequiredMixin, ListView):
    model = Furgon
    template_name = 'frontend/furgon_list.html'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        # Admins see all
        if user and (user.is_staff or in_group(user, 'Administrador')):
            qs = super().get_queryset().order_by('patente')
        else:
            qs = None
        # Conductors see only their furgones
        if user and in_group(user, 'Conductor'):
            qs = Furgon.objects.filter(conductor__user=user).order_by('patente')
        # Apoderado sees furgones related to their students
        if user and in_group(user, 'Apoderado'):
            qs = Furgon.objects.filter(estudiantes__apoderado_user=user).distinct().order_by('patente')
        # apply search filter if present
        q = self.request.GET.get('q')
        if qs is None:
            qs = Furgon.objects.none()
        if q:
            qs = qs.filter(Q(patente__icontains=q) | Q(modelo__icontains=q))
        return qs


class FurgonMineView(LoginRequiredMixin, TemplateView):
    template_name = 'frontend/mi_furgon.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        # Admins see all furgones, but 'mi-furgon' is primarily for conductors
        if user and (user.is_staff or in_group(user, 'Administrador')):
            furgones = Furgon.objects.all()
        elif user and in_group(user, 'Conductor'):
            furgones = Furgon.objects.filter(conductor__user=user)
        else:
            furgones = Furgon.objects.none()
        # for now assume at most one primary furgon; but pass list for completeness
        ctx['furgones'] = furgones
        # include students and routes for the first furgon
        if furgones.exists():
            f = furgones.first()
            ctx['students'] = f.estudiantes.all()
            ctx['routes'] = f.rutas.all()
        else:
            ctx['students'] = []
            ctx['routes'] = []
        return ctx


class FurgonCreate(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Furgon
    form_class = FurgonForm
    template_name = 'frontend/form.html'
    success_url = reverse_lazy('frontend:furgon_list')


class ColegioDetail(LoginRequiredMixin, DetailView):
    model = Colegio
    template_name = 'frontend/detail.html'


class ConductorDetail(LoginRequiredMixin, DetailView):
    model = Conductor
    template_name = 'frontend/detail.html'


class FurgonDetail(LoginRequiredMixin, DetailView):
    model = Furgon
    template_name = 'frontend/detail.html'


class FurgonUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Furgon
    form_class = FurgonForm
    template_name = 'frontend/form.html'
    success_url = reverse_lazy('frontend:furgon_list')

    def test_func(self):
        user = self.request.user
        if user and (user.is_staff or in_group(user, 'Administrador')):
            return True
        # owner
        obj = self.get_object()
        return (
            in_group(user, 'Conductor')
            and getattr(obj, 'conductor', None)
            and getattr(obj.conductor, 'user', None) == user
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Furgón actualizado correctamente.')
        return response


@login_required
def furgon_update_location(request, pk):
    f = get_object_or_404(Furgon, pk=pk)
    user = request.user
    # Authorization: admin allowed; conductor allowed only on own furgon
    if not (user and (user.is_staff or in_group(user, 'Administrador'))):
        if not (user and in_group(user, 'Conductor') and getattr(f.conductor, 'user', None) == user):
            messages.error(request, 'No autorizado para actualizar ubicación')
            return redirect('frontend:furgon_list')
    lat = request.POST.get('latitude')
    lon = request.POST.get('longitude')
    if not lat or not lon:
        messages.error(request, 'latitude y longitude son requeridos')
        return redirect('frontend:furgon_list')
    try:
        f.update_location(float(lat), float(lon))
        messages.success(request, 'Ubicación actualizada')
    except Exception:
        messages.error(request, 'Error actualizando ubicación')
    return redirect('frontend:furgon_list')


class EstudianteList(LoginRequiredMixin, ListView):
    model = Estudiante
    template_name = 'frontend/estudiante_list.html'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        if user and (user.is_staff or in_group(user, 'Administrador')):
            qs = super().get_queryset().order_by('nombre')
        else:
            qs = None
        if user and in_group(user, 'Apoderado'):
            qs = Estudiante.objects.filter(apoderado_user=user).order_by('nombre')
        if user and in_group(user, 'Conductor'):
            qs = Estudiante.objects.filter(furgon__conductor__user=user).order_by('nombre')
        if qs is None:
            qs = Estudiante.objects.none()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(rut__icontains=q))
        return qs


class EstudianteCreate(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Estudiante
    form_class = EstudianteForm
    template_name = 'frontend/form.html'
    success_url = reverse_lazy('frontend:estudiante_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Estudiante creado correctamente.')
        return response


class EstudianteDetail(LoginRequiredMixin, DetailView):
    model = Estudiante
    template_name = 'frontend/detail.html'


class EstudianteUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Estudiante
    form_class = EstudianteForm
    template_name = 'frontend/form.html'
    success_url = reverse_lazy('frontend:estudiante_list')

    def test_func(self):
        user = self.request.user
        # admins
        if user and (user.is_staff or in_group(user, 'Administrador')):
            return True
        # apoderado owner
        obj = self.get_object()
        if in_group(user, 'Apoderado'):
            apod = getattr(obj, 'apoderado_user', None)
            if apod and getattr(apod, 'pk', None) == getattr(user, 'pk', None):
                return True
        # conductor assigned to student's furgon
        if in_group(user, 'Conductor') and getattr(obj, 'furgon', None):
            if getattr(obj.furgon.conductor, 'user', None) == user:
                return True
        return False

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Estudiante actualizado correctamente.')
        return response


class RutaList(LoginRequiredMixin, ListView):
    model = Ruta
    template_name = 'frontend/ruta_list.html'
    paginate_by = 20
    ordering = ['hora_inicio']

    def get_queryset(self):
        qs = super().get_queryset().order_by('hora_inicio')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(tipo_ruta__icontains=q) | Q(furgon__patente__icontains=q))
        return qs


class RutaCreate(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Ruta
    form_class = RutaForm
    template_name = 'frontend/form.html'
    success_url = reverse_lazy('frontend:ruta_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ruta creada correctamente.')
        return response


class RutaUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ruta
    form_class = RutaForm
    template_name = 'frontend/form.html'
    success_url = reverse_lazy('frontend:ruta_list')

    def test_func(self):
        user = self.request.user
        # Admins allowed
        if user and (user.is_staff or in_group(user, 'Administrador')):
            return True
        # allow a conductor to edit routes that are assigned to their furgon
        obj = self.get_object()
        if getattr(obj, 'furgon', None) and getattr(obj.furgon, 'conductor', None):
            return getattr(obj.furgon.conductor, 'user', None) == user
        return False

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ruta actualizada correctamente.')
        return response


class RutaDetail(LoginRequiredMixin, DetailView):
    model = Ruta
    template_name = 'frontend/detail.html'


class NotificacionList(LoginRequiredMixin, ListView):
    model = Notificacion
    template_name = 'frontend/notificacion_list.html'
    ordering = ['-creado_at']
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        if user and (user.is_staff or in_group(user, 'Administrador')):
            qs = super().get_queryset().order_by('-creado_at')
        elif user and in_group(user, 'Apoderado'):
            qs = Notificacion.objects.filter(estudiante__apoderado_user=user).order_by('-creado_at')
        elif user and in_group(user, 'Conductor'):
            qs = Notificacion.objects.filter(furgon__conductor__user=user).order_by('-creado_at')
        else:
            qs = Notificacion.objects.none()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(mensaje__icontains=q)
        return qs


@login_required
def notificacion_mark_read(request, pk):
    n = get_object_or_404(Notificacion, pk=pk)
    user = request.user
    allowed = False
    if user and (user.is_staff or in_group(user, 'Administrador')):
        allowed = True
    if user and in_group(user, 'Apoderado') and getattr(n.estudiante, 'apoderado_user', None) == user:
        allowed = True
    if user and in_group(user, 'Conductor'):
        f_conductor = getattr(n.furgon, 'conductor', None)
        if f_conductor and getattr(f_conductor, 'user', None) == user:
            allowed = True
    if not allowed:
        messages.error(request, 'No autorizado')
        return redirect('frontend:notificacion_list')

    n.marcar_como_leida()
    messages.success(request, 'Notificación marcada como leída')
    return redirect('frontend:notificacion_list')


class NotificacionCreate(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Notificacion
    form_class = NotificacionForm
    template_name = 'frontend/form.html'
    success_url = reverse_lazy('frontend:notificacion_list')


class NotificacionDetail(LoginRequiredMixin, DetailView):
    model = Notificacion
    template_name = 'frontend/detail.html'


class PagoList(LoginRequiredMixin, ListView):
    model = Pago
    template_name = 'frontend/pago_list.html'
    paginate_by = 20
    ordering = ['-fecha']

    def get_queryset(self):
        qs = super().get_queryset().order_by('-fecha')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(estudiante__nombre__icontains=q) | Q(referencia__icontains=q))
        return qs


class PagoCreate(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'frontend/form.html'
    success_url = reverse_lazy('frontend:pago_list')


class PagoDetail(LoginRequiredMixin, DetailView):
    model = Pago
    template_name = 'frontend/detail.html'


class AsistenciaList(LoginRequiredMixin, ListView):
    model = Asistencia
    template_name = 'frontend/asistencia_list.html'
    paginate_by = 20
    ordering = ['-fecha']

    def get_queryset(self):
        qs = super().get_queryset().order_by('-fecha')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(estudiante__nombre__icontains=q))
        return qs


class AsistenciaCreate(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Asistencia
    form_class = AsistenciaForm
    template_name = 'frontend/form.html'
    success_url = reverse_lazy('frontend:asistencia_list')


class AsistenciaDetail(LoginRequiredMixin, DetailView):
    model = Asistencia
    template_name = 'frontend/detail.html'
