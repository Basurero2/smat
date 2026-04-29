from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="SMAT API")

class Estacion(BaseModel):
    id: int
    nombre: str
    ubicacion: str

db_estaciones = []

@app.post("/estaciones/", status_code=201)
async def crear_estacion(estacion: Estacion):
    db_estaciones.append(estacion)
    return {"msj": "Estación creada", "data": estacion}


class Lectura(BaseModel):
    estacion_id: int
    valor: float

db_lecturas = []

@app.post("/lecturas/", status_code=201)
async def registrar_lectura(lectura: Lectura):
    db_lecturas.append(lectura)
    return {"status": "Lectura recibida"}

@app.get("/estaciones/{id}/riesgo")
async def obtener_riesgo(id: int):
    # Validar si la estación existe (Requisito 404)
    if not any(e.id == id for e in db_estaciones):
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    # Filtrar lecturas y evaluar riesgo
    lecturas = [l for l in db_lecturas if l.estacion_id == id]
    if not lecturas:
        return {"id": id, "nivel": "SIN DATOS", "valor": 0}
    
    ultima_lectura = lecturas[-1].valor
    nivel = "PELIGRO" if ultima_lectura > 20.0 else "ALERTA" if ultima_lectura > 10.0 else "NORMAL"
    return {"id": id, "valor": ultima_lectura, "nivel": nivel}


@app.get("/estaciones/{id}/historial")
async def obtener_historial(id: int):
    # 1. Verificar existencia
    if not any(e.id == id for e in db_estaciones):
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    # 2. Filtrar y calcular
    lecturas_filtradas = [l.valor for l in db_lecturas if l.estacion_id == id]
    
    if not lecturas_filtradas:
        return {"estacion_id": id, "lecturas": [], "conteo": 0, "promedio": 0}
    
    promedio = sum(lecturas_filtradas) / len(lecturas_filtradas)
    
    return {
        "estacion_id": id,
        "lecturas": lecturas_filtradas,
        "conteo": len(lecturas_filtradas),
        "promedio": round(promedio, 2)
    }