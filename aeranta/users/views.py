from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from .forms import LoginUserForm, RegisterUserForm, EditProfileForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from weather.models import OpenWeatherApi
from django.views.decorators.http import require_POST



class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': "Авторизация"}

    def get_success_url(self):
        return reverse_lazy('users:profile')


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация пользователей'}
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        forecast = OpenWeatherApi.objects.create(user=user)
        forecast.update_data()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('users:confirm_email_prompt')


class ProfileUser(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context['title'] = 'profile'
        context['user'] = self.request.user

        try:
            if 'page' not in self.request.GET:
                user.open_weather.update_data()
        except Exception:
            print(f'Falied data update for {user}')

        try:
            weather = user.open_weather.weather_data
            forecast = user.open_weather.forecast_data
            max_min_temp = [weather['temp']]
            for i in range(8):
                max_min_temp.append(forecast[i]['temp'])
            weather['temp_max'] = max(max_min_temp)
            weather['temp_min'] = min(max_min_temp)
            weather['temp_kf'] = round(float(weather['temp_max'] - weather['temp_min']), 2)
            paginator = Paginator(forecast, 8)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['current_weather'] = weather
            context['last_updated'] = user.open_weather.last_updated
            context['page_obj'] = page_obj
        except Exception as e:
            print(f'Failed: {e}')
            context['current_weather'] = None
            context['forecast'] = None
        if hasattr(user, 'auroras'):
            try:
                user.auroras.update_data()
                cosmic_data = user.auroras.current_data
                context['cosmic_data'] = cosmic_data
            except Exception as e:
                print(f'Failed: {e}')
        if hasattr(user, 'ipga'):
            try:
                user.ipga.update_data()
                lunar_data = user.ipga.current_data
                context['moon_data'] = lunar_data
            except Exception as e:
                print(f'Failed: {e}')
        return context


@require_POST
def update_location(request):
    user = request.user
    try:
        lat = float(request.POST.get('lat'))
        lon = float(request.POST.get('lon'))

        user.location = Point(lon, lat, srid=4326)
        user.save()

        user.open_weather.update_data()

        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


class ProfileForecastBlock(ProfileUser):
    template_name = 'includes/forecast_block.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        html = render_to_string(self.template_name, context, request=request)
        return JsonResponse({'html': html})



class EditProfileView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = EditProfileForm
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        if not self.request.user.email_confirmed:
            return redirect('users:confirm_email_prompt')
        return response

