from django.contrib import admin
from .models import Ramo, Evaluacion

# 1. Creamos una clase para mostrar las Evaluaciones "en línea" dentro de Ramo
class EvaluacionInline(admin.TabularInline):
    model = Evaluacion
    # 'extra' controla cuántos campos vacíos para nuevas evaluaciones se muestran
    extra = 1

# 2. Creamos una clase personalizada para el admin de Ramo
class RamoAdmin(admin.ModelAdmin):
    # Columnas que se mostrarán en la lista principal de ramos
    list_display = ('nombre', 'nota_aprobacion')
    # ¡Aquí conectamos las evaluaciones para que aparezcan dentro de Ramo!
    inlines = [EvaluacionInline]

# 3. Registramos nuestros modelos con la nueva configuración
#    Primero des-registramos la versión simple de Ramo si ya existía
#    (No da error si no estaba registrada, así que es seguro ponerlo)
try:
    admin.site.unregister(Ramo)
except admin.sites.NotRegistered:
    pass

admin.site.register(Ramo, RamoAdmin) # Registramos Ramo con su nueva clase admin
admin.site.register(Evaluacion) # Podemos mantener el admin de Evaluacion por separado

# Register your models here.

