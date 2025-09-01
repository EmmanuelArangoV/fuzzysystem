# fuzzy_mujer.py
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Universos
edad = ctrl.Antecedent(np.arange(0, 101, 1), 'edad')
imc  = ctrl.Antecedent(np.arange(12.0, 50.1, 0.1), 'imc')
riesgo = ctrl.Consequent(np.arange(0, 11, 0.1), 'riesgo')

# ------------------------
# MFs con solape amplio
# ------------------------

# Edad: trapezoidal
edad['joven']  = fuzz.trapmf(edad.universe, [0, 0, 20, 30])
edad['adulta'] = fuzz.trapmf(edad.universe, [25, 35, 50, 60])
edad['mayor']  = fuzz.trapmf(edad.universe, [55, 65, 100, 100])

# IMC: gaussianas solapadas
imc['bajo']      = fuzz.gaussmf(imc.universe, 17.5, 1.8)
imc['normal']    = fuzz.gaussmf(imc.universe, 22.0, 2.0)
imc['sobrepeso'] = fuzz.gaussmf(imc.universe, 27.0, 2.2)
imc['obesidad1'] = fuzz.gaussmf(imc.universe, 32.0, 2.5)
imc['obesidad2'] = fuzz.gaussmf(imc.universe, 38.5, 3.0)

# Riesgo: salida solapada
riesgo['muy_bajo'] = fuzz.trimf(riesgo.universe, [0.0, 0.0, 2.5])
riesgo['bajo']     = fuzz.trimf(riesgo.universe, [2.0, 3.5, 5.0])
riesgo['medio']    = fuzz.trimf(riesgo.universe, [4.5, 5.8, 7.2])
riesgo['alto']     = fuzz.trimf(riesgo.universe, [6.8, 8.0, 9.0])
riesgo['muy_alto'] = fuzz.trimf(riesgo.universe, [8.5, 10.0, 10.0])

# ------------------------
# Reglas ajustadas (mujer)
# Comentario: las reglas pueden provenir de evidencia clínica o heurísticas.
# ------------------------
rules = [
    # IMC normal => bajo riesgo si joven/adulta
    ctrl.Rule(imc['normal'] & (edad['joven'] | edad['adulta']), riesgo['bajo']),
    # IMC bajo y edad mayor => riesgo medio (por sarcopenia etc.)
    ctrl.Rule(imc['bajo'] & edad['mayor'], riesgo['medio']),
    # Sobrepeso + adulto => medio, sobrepeso + mayor => alto
    ctrl.Rule(imc['sobrepeso'] & edad['adulta'], riesgo['medio']),
    ctrl.Rule(imc['sobrepeso'] & edad['mayor'], riesgo['alto']),
    # Obesidad1 => alto (más sensible en mujeres)
    ctrl.Rule(imc['obesidad1'] & (edad['adulta'] | edad['mayor']), riesgo['alto']),
    # Obesidad2 => muy alto
    ctrl.Rule(imc['obesidad2'], riesgo['muy_alto']),
    # Ajuste sutil: IMC normal pero edad mayor -> medio (precaución)
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

def evaluar_mujer_difuso(edad_val: float, peso: float, altura: float):
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

# Si se desea exponer vistas para debugging
def get_system_objects():
    return {
        "edad": edad,
        "imc": imc,
        "riesgo": riesgo,
        "control_system": control_system
    }

if __name__ == "__main__":
    print(evaluar_mujer_difuso(45, 68, 1.65))

imc.view()
edad.view()
riesgo.view()
