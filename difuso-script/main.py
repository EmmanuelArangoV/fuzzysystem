# main.py
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from fuzzy_hombre import evaluar_hombre_difuso
from fuzzy_mujer import evaluar_mujer_difuso

app = FastAPI(title="Fuzzy IMC API (separate gender systems)")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Entrada(BaseModel):
    edad: int = Field(..., ge=0, le=120, description="Edad en años")
    genero: Literal['femenino', 'masculino'] = Field(..., description="'femenino' o 'masculino'")
    peso: float = Field(..., gt=0, description="Peso en kilogramos")
    altura: float = Field(..., gt=0, description="Altura en metros (ej. 1.70)")


@app.post("/riesgo")
def calcular_riesgo(data: Entrada):
    # validación simple
    if data.genero not in ('masculino', 'femenino'):
        raise HTTPException(status_code=400, detail="genero debe ser 'femenino' o 'masculino'")

    if data.genero == 'femenino':
        res = evaluar_mujer_difuso(edad_val=data.edad, peso=data.peso, altura=data.altura)
    else:
        res = evaluar_hombre_difuso(edad_val=data.edad, peso=data.peso, altura=data.altura)

    # categorización opcional por rangos (interpretación)
    riesgo_val = res['riesgo']
    if riesgo_val < 3.5:
        categoria = "Muy bajo"
    elif riesgo_val < 5.0:
        categoria = "Bajo"
    elif riesgo_val < 6.8:
        categoria = "Medio"
    elif riesgo_val < 8.6:
        categoria = "Alto"
    else:
        categoria = "Muy alto"

    imc_val = res['imc']
    if imc_val < 18.5:
        categoria2 = "Bajo peso"
    elif imc_val < 25:
        categoria2 = "Normal"
    elif imc_val < 30:
        categoria2 = "Sobrepeso"
    else:
        categoria2 = "Obesidad"

    # Antes de formatear_difuso y generar_recomendaciones -> Ajustar extremos de las graficas
    if categoria == "Muy alto" and categoria2 == "Obesidad":
        res['imc_difuso'] = {"bajo": "0.0", "normal": "0.0", "sobrepeso": "0.0", "obesidad1": "0.0", "obesidad2": "1.0"}
        res['riesgo_difuso'] = {"muy_bajo": "0.0", "bajo": "0.0", "medio": "0.0", "alto": "0.0", "muy_alto": "1.0"}
    elif categoria == "Bajo" or categoria == "Muy bajo" and categoria2 == "Bajo peso":
        res['imc_difuso'] = {"bajo": "1.0", "normal": "0.0", "sobrepeso": "0.0", "obesidad1": "0.0", "obesidad2": "0.0"}
        res['riesgo_difuso'] = {"muy_bajo": "0.0", "bajo": "0.0", "medio": "0.0", "alto": "1.0", "muy_alto": "0.0"}
        categoria = "Alto"

    recomendaciones = generar_recomendaciones(res['imc_difuso'], res['riesgo_difuso'])

    estadosdifusos = formatear_difuso(res['imc_difuso'], res['riesgo_difuso'])

    return {
        "IMCValue": round(res['imc'], 2),
        "IMCDifuso": estadosdifusos,
        "MainDescription": categoria2,
        "RiskDescription": categoria,
        "MainRisk": round(riesgo_val, 3),
        "Recomendaciones": recomendaciones
    }


def generar_recomendaciones(imc_difuso: dict, riesgo_difuso: dict) -> str:
    # Ordena las categorías por grado de pertenencia
    imc_sorted = sorted(imc_difuso.items(), key=lambda x: float(x[1]), reverse=True)
    riesgo_sorted = sorted(riesgo_difuso.items(), key=lambda x: float(x[1]), reverse=True)

    recomendaciones = []

    # IMC: toma las dos categorías principales si ambas tienen pertenencia > 0.2
    for cat, val in imc_sorted[:2]:
        if float(val) > 0.2:
            if cat == "bajo":
                recomendaciones.append("Tienes tendencia a bajo peso, considera aumentar tu ingesta calórica.")
            elif cat == "normal":
                recomendaciones.append("Tu IMC está cerca de lo normal, mantén hábitos saludables.")
            elif cat == "sobrepeso":
                recomendaciones.append("Hay indicios de sobrepeso, mejora tu alimentación y actividad física.")
            elif cat in ["obesidad1", "obesidad2"]:
                recomendaciones.append("Presentas tendencia a obesidad, busca apoyo profesional.")

    # Riesgo: igual, dos principales si > 0.2
    for cat, val in riesgo_sorted[:2]:
        if float(val) > 0.2:
            if cat in ["muy_bajo", "bajo"]:
                recomendaciones.append("Tu riesgo es bajo, sigue cuidando tu salud.")
            elif cat == "medio":
                recomendaciones.append("Riesgo medio, realiza chequeos periódicos.")
            elif cat in ["alto", "muy_alto"]:
                recomendaciones.append("Riesgo elevado, consulta a un médico.")

    return " ".join(recomendaciones)


def formatear_difuso(imc_difuso: dict, riesgo_difuso: dict) -> str:
    imc_labels = {
        "bajo": "Bajo peso",
        "normal": "Normal",
        "sobrepeso": "Sobrepeso",
        "obesidad1": "Obesidad tipo 1",
        "obesidad2": "Obesidad tipo 2"
    }
    riesgo_labels = {
        "muy_bajo": "Muy bajo",
        "bajo": "Bajo",
        "medio": "Medio",
        "alto": "Alto",
        "muy_alto": "Muy alto"
    }

    imc_str = "IMC Difuso:\n" + "\n".join(
        f"- {imc_labels[k]}: {float(v):.2f}" for k, v in imc_difuso.items() if float(v) > 0
    )
    riesgo_str = "Riesgo Difuso:\n" + "\n".join(
        f"- {riesgo_labels[k]}: {float(v):.2f}" for k, v in riesgo_difuso.items() if float(v) > 0
    )
    return f"{imc_str}\n{riesgo_str}"


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Datos inválidos",
            "detalles": exc.errors(),
            "body_recibido": exc.body
        },
    )
