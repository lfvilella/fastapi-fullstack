from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from . import models
from validate_docbr import CNPJ, CPF


class CobrancaForm(forms.Form):
    devedor = forms.CharField()
    codigo_identificador = forms.CharField()
    debito = forms.DecimalField()

    def clean_codigo_identificador(self):
        data = self.cleaned_data['codigo_identificador']

        cnpj, cpf = CNPJ(), CPF()
        if not (cnpj.validate(data) or cpf.validate(data)):
            raise forms.ValidationError("CNPJ/CPF inválido!")

        return data


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = models.CustomUser
        fields = ('username', 'email', 'codigo_identificador')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = models.CustomUser
        fields = ('username', 'email', 'codigo_identificador')