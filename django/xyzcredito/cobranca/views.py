from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from . import forms
from . import models


class Home(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/users/login')

        return render(request, 'home.html')


class CreateCobranca(LoginRequiredMixin, View):
    def get(self, request):
        cobranca_form = forms.CobrancaForm()
        return render(request, 'cobranca/create.html', context={'form': cobranca_form})
    
    def post(self, request):
        cobranca_form = forms.CobrancaForm(request.POST)

        if not cobranca_form.is_valid():
            return render(request, 'cobranca/create.html', context={'form': cobranca_form})

        data = cobranca_form.cleaned_data
        cobranca = models.Cobranca()
        cobranca.devedor = data['devedor']
        cobranca.codigo_identificador = data['codigo_identificador']
        cobranca.debito = data['debito']
        cobranca.credor_id = request.user.pk
        cobranca.save()

        return redirect('cobranca:list')


class ListCobranca(LoginRequiredMixin, View):
    def get(self, request):
        cobrancas = models.Cobranca.objects.all()
        return render(request, 'cobranca/list.html', context={'cobrancas': cobrancas})


class SignUpView(CreateView):
    form_class = forms.CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
