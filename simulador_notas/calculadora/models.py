from django.db import models

# Create your models here.

class Ramo(models.Model):
    nombre = models.CharField(max_length=100)
    nota_aprobacion = models.FloatField(default=55.0)

    def __str__(self):
        return self.nombre
class Evaluacion(models.Model):
    ramo = models.ForeignKey(Ramo, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    ponderacion = models.FloatField()

    def __str__(self):
        return f"{self.nombre} ({self.ramo.nombre})"