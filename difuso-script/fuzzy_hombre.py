# fuzzy_hombre.py
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Universos
edad = ctrl.Antecedent(np.arange(0, 101, 1), 'edad')
imc  = ctrl.Antecedent(np.arange(12.0, 50.1, 0.1), 'imc')
riesgo = ctrl.Consequent(np.arange(0, 11, 0.1), 'riesgo')

# ------------------------
# MFs con solape amplio (parámetros distintos a mujer)
# ------------------------

edad['joven']  = fuzz.trapmf(edad.universe, [0, 0, 20, 30])
edad['adulto'] = fuzz.trapmf(edad.universe, [25, 35, 50, 60])
edad['mayor']  = fuzz.trapmf(edad.universe, [55, 65, 100, 100])

# IMC (hombres tienden a tener composición distinta -> thresholds ligeramente desplazados)
imc['bajo']      = fuzz.gaussmf(imc.universe, 18.0, 1.9)
imc['normal']    = fuzz.gaussmf(imc.universe, 23.0, 2.1)
imc['sobrepeso'] = fuzz.gaussmf(imc.universe, 28.0, 2.2)
imc['obesidad1'] = fuzz.gaussmf(imc.universe, 33.0, 2.6)
imc['obesidad2'] = fuzz.gaussmf(imc.universe, 39.0, 3.2)

# Riesgo salida
riesgo['muy_bajo'] = fuzz.trimf(riesgo.universe, [0.0, 0.0, 2.0])
riesgo['bajo']     = fuzz.trimf(riesgo.universe, [1.8, 3.2, 4.8])
riesgo['medio']    = fuzz.trimf(riesgo.universe, [4.4, 5.8, 7.0])
riesgo['alto']     = fuzz.trimf(riesgo.universe, [6.6, 8.0, 9.2])
riesgo['muy_alto'] = fuzz.trimf(riesgo.universe, [8.6, 10.0, 10.0])

# ------------------------
# Reglas (hombre) — calibración distinta
# ------------------------
rules = [
    ctrl.Rule(imc['normal'] & (edad['joven'] | edad['adulto']), riesgo['bajo']),
    # Hombres con IMC bajo y edad mayor -> riesgo medio (similar)
    ctrl.Rule(imc['bajo'] & edad['mayor'], riesgo['medio']),
    # Sobrepeso: en hombres pasa a alto más rápido
    ctrl.Rule(imc['sobrepeso'] & (edad['adulto'] | edad['mayor']), riesgo['alto']),
    # Obesidad1 -> muy alto (más agresivo para hombres)
    ctrl.Rule(imc['obesidad1'], riesgo['muy_alto']),
    ctrl.Rule(imc['obesidad2'], riesgo['muy_alto']),
    # Precaución: IMC normal + mayor -> medio (igual)
    ctrl.Rule(imc['normal'] & edad['mayor'], riesgo['medio']),
]

control_system = ctrl.ControlSystem(rules)

def grados_imc(imc_val):
    grados = {}
    for etiqueta in imc.terms:
        mf = imc[etiqueta].mf
        grados[etiqueta] = fuzz.interp_membership(imc.universe, mf, imc_val)
    return grados

def grados_riesgo(riesgo_val):
    grados = {}
    for etiqueta in riesgo.terms:
        mf = riesgo[etiqueta].mf
        grados[etiqueta] = fuzz.interp_membership(riesgo.universe, mf, riesgo_val)
    return grados

def evaluar_hombre_difuso(edad_val: float, peso: float, altura: float):
    altura = altura / 100
    imc_val = float(peso) / (float(altura) ** 2)
    sim = ctrl.ControlSystemSimulation(control_system)
    sim.input['edad'] = float(edad_val)
    sim.input['imc'] = float(imc_val)
    sim.compute()
    riesgo_val = float(sim.output['riesgo'])

    imc_grados = grados_imc(imc_val)
    riesgo_grados = grados_riesgo(riesgo_val)

    return {
        "imc": imc_val,
        "imc_difuso": imc_grados,
        "riesgo": riesgo_val,
        "riesgo_difuso": riesgo_grados
    }

def get_system_objects():
    return {
        "edad": edad,
        "imc": imc,
        "riesgo": riesgo,
        "control_system": control_system
    }

if __name__ == "__main__":
    print(evaluar_hombre_difuso(50, 95, 1.78))

imc.view()
edad.view()
riesgo.view()