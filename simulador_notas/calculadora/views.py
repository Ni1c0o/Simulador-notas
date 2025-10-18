from django.shortcuts import render, get_object_or_404
from .models import Ramo, Evaluacion

def main_page(request):
    ramos = Ramo.objects.all()
    return render(request, 'calculadora/main_page.html', {'ramos': ramos})

def calculadora_ramo(request, ramo_id):
    ramo = get_object_or_404(Ramo, pk=ramo_id)
    evaluaciones = Evaluacion.objects.filter(ramo=ramo)
    contexto = {
        'ramo': ramo,
        'evaluaciones': evaluaciones,
    }

    if request.method == 'POST':
        nota_acumulada = 0.0
        ponderacion_acumulada = 0.0

        # --- INICIO DE LA LÓGICA CONDICIONAL ---
        if ramo.nombre == 'MAT071':
            # --- Lógica especial SOLO para MAT071 ---
            
            # 1. Separamos las notas de controles del resto de evaluaciones (certámenes)
            notas_controles = []
            aporte_otros = 0.0
            ponderacion_total_controles = 0.0 # Necesitamos la ponderación total del grupo de controles

            for evaluacion in evaluaciones:
                nombre_input = f'evaluacion-{evaluacion.id}'
                nota_str = request.POST.get(nombre_input)
                evaluacion.nota_ingresada = nota_str

                # Si es un Control, lo guardamos en una lista para procesarlo después
                if 'Control' in evaluacion.nombre:
                    ponderacion_total_controles += evaluacion.ponderacion
                    if nota_str:
                        notas_controles.append(float(nota_str))
                
                # Si es otra cosa, lo calculamos de la forma normal
                else:
                    if nota_str:
                        nota = float(nota_str)
                        aporte_otros += nota * evaluacion.ponderacion

            # 2. Aplicamos la regla de eliminar la peor nota a los controles
            notas_controles.sort() # Ordenamos de menor a mayor
            
            if len(notas_controles) > 5:
                # Si hay más de 5 notas, eliminamos la primera (la más baja)
                notas_a_considerar = notas_controles[1:]
            else:
                # Si hay 5 o menos, se consideran todas
                notas_a_considerar = notas_controles
            
            # 3. Calculamos el promedio de los controles que sí cuentan
            promedio_controles = 0
            if notas_a_considerar:
                promedio_controles = sum(notas_a_considerar) / len(notas_a_considerar)
            
            # 4. Calculamos el aporte total de los controles y lo sumamos al resto
            aporte_total_controles = promedio_controles * 0.25
            nota_acumulada = aporte_total_controles + aporte_otros

            # 5. Finalmente, recalculamos la ponderación acumulada para los cálculos finales
            for evaluacion in evaluaciones:
                if request.POST.get(f'evaluacion-{evaluacion.id}'):
                    ponderacion_acumulada += evaluacion.ponderacion

        elif ramo.nombre == 'FIS111':
            # --- Lógica especial SOLO para FIS111 ---
            dicc = {'notas_controles': [], 'notas_tareas': [], 'notas_experiencias': [], 'notas_quiz': [], 'notas_certamenes': []}
            # Al principio de la lógica de FIS111, después de definir 'dicc'

            notas_para_promedio_simple = []
            ponderacion_acumulada = 0.0
            for evaluacion in evaluaciones:                
                nombre_input = f'evaluacion-{evaluacion.id}'
                nota_str = request.POST.get(nombre_input)
                evaluacion.nota_ingresada = nota_str
                if not nota_str:
                    continue
                nota = float(nota_str)
                notas_para_promedio_simple.append(nota)

                if 'Control' in evaluacion.nombre:
                    if nota_str:
                        dicc['notas_controles'].append(float(nota_str)*5)
                elif 'Tarea' in evaluacion.nombre:
                    if nota_str:
                        dicc['notas_tareas'].append(float(nota_str))
                elif 'Experiencia' in evaluacion.nombre:
                    if nota_str:
                        dicc['notas_experiencias'].append(float(nota_str))
                elif 'Quiz' in evaluacion.nombre:
                    if nota_str:
                        dicc['notas_quiz'].append(float(nota_str))
                elif 'Certamen' in evaluacion.nombre:
                    if nota_str:
                        dicc['notas_certamenes'].append(float(nota_str))           
            
            certamenes = dicc['notas_certamenes']
            certamenes.sort()
            PC = sum(certamenes)/3
                        
            controles = dicc['notas_controles']
            controles.sort()
            if len(controles) > 5:
                    notas_a_considerar = controles[1:]
            else:
                notas_a_considerar = controles
            PQ = sum(notas_a_considerar)/5
            

            tareas = dicc['notas_tareas']
            tareas.sort()
            if len(tareas) > 5:
                    notas_a_considerar = tareas[1:]
            else:
                notas_a_considerar = tareas
            PT = sum(notas_a_considerar)/5
            

            experiencias = dicc['notas_experiencias']
            experiencias.sort()
            if len(experiencias) > 6:
                    notas_a_considerar = experiencias[1:]
            else:
                notas_a_considerar = experiencias
            promedio_exp = sum(notas_a_considerar)/6
            
            quizes = dicc['notas_quiz']
            promedio_qui = sum(quizes)/3

            NL = (0.5*promedio_qui) + (0.5*promedio_exp)
            nota_final = (0.75 * PC) + (0.10 * PT) + (0.15 * PQ)
            nota_acumulada = (0.8 * nota_final) + (0.20 * NL)
            
            for evaluacion in evaluaciones:
                if request.POST.get(f'evaluacion-{evaluacion.id}'):
                    ponderacion_acumulada += evaluacion.ponderacion
        
        else:
            # --- Lógica genérica para todos los demás ramos (la que ya tenías) ---
            for evaluacion in evaluaciones:
                nombre_input = f'evaluacion-{evaluacion.id}'
                nota_str = request.POST.get(nombre_input)
                evaluacion.nota_ingresada = nota_str
                
                if nota_str:
                    nota = float(nota_str)
                    ponderacion = evaluacion.ponderacion
                    nota_acumulada += nota * ponderacion
                    ponderacion_acumulada += ponderacion
        
        # -------------------------------------------------------------------
        # CÁLCULOS FINALES (ESTA PARTE ES IGUAL PARA TODOS LOS RAMOS)
        # -------------------------------------------------------------------
        promedio_actual = 0
        if ponderacion_acumulada > 0:
            promedio_actual = sum(notas_para_promedio_simple) / len(notas_para_promedio_simple) if notas_para_promedio_simple else 0.0
        ponderacion_restante = 1.0 - ponderacion_acumulada
        mensaje = ""
        nota_necesaria = 0

        if ponderacion_restante > 0.001: # Usamos un valor pequeño para evitar errores de precisión con decimales
            puntos_necesarios = ramo.nota_aprobacion - nota_acumulada        
            if puntos_necesarios > 0:
                nota_necesaria = puntos_necesarios / ponderacion_restante
                if nota_necesaria > 100.0:
                    mensaje = "Ya no es posible aprobar el ramo."
                elif nota_necesaria <= 0.0:
                    mensaje = "¡Ya aprobaste el ramo! Felicidades."
                    nota_necesaria = 0.0
                else:
                    mensaje = "Aún puedes aprobar."
            else:
                mensaje = "¡Ya aprobaste el ramo! Felicidades."
                nota_necesaria = 0.0        
        else:
             promedio_actual = nota_acumulada
             if nota_acumulada >= ramo.nota_aprobacion:
                 mensaje = "¡Aprobado! Tu nota final es " + str(round(nota_acumulada, 2))
             else:
                 mensaje = "Reprobado. Tu nota final es " + str(round(nota_acumulada, 2))

        # Pasamos los resultados a la plantilla
        resultado = {
            'promedio_actual': promedio_actual,
            'ponderacion_cubierta': ponderacion_acumulada * 100,
            'nota_necesaria': nota_necesaria,
            'mensaje': mensaje,
        }
        contexto['resultado'] = resultado

    return render(request, 'calculadora/calculadora_ramo.html', contexto)
# Create your views here.
