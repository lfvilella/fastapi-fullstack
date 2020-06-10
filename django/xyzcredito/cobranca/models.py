import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class BaseModel(models.Model):
    class Meta:
        abstract = True
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    ultima_alteracao = models.DateTimeField(auto_now=True)


class Cobranca(BaseModel):
    devedor = models.CharField(max_length=50, null=False, blank=False)
    codigo_identificador = models.CharField(max_length=20, null=False, blank=False)
    debito = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False)
    credor = models.ForeignKey("CustomUser", on_delete=models.CASCADE, null=False, blank=False)


class CustomUser(BaseModel, AbstractUser):
    codigo_identificador = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f'{self.username} - {self.codigo_identificador}'
