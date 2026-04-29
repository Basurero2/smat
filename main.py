from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import models
from database import SessionLocal, engine

# Crea las tablas en el archivo smat.db si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SMAT - Sistema de Monitoreo de Alerta Temprana")

# Dependencia para conectar a la DB en cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINTS DE ESTACIONES ---

@app.post("/estaciones/", status_code=201)
def crear_estacion(id: int, nombre: str, ubicacion: str, db: Session = Depends(get_db)):
    # Verificar si el ID ya existe en la base de datos
    existe = db.query(models.Estacion).filter(models.Estacion.id == id).first()
    if existe:
        raise HTTPException(status_code=400, detail="El ID de la estación ya existe")
    
    nueva_estacion = models.Estacion(id=id, nombre=nombre, ubicacion=ubicacion)
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    return {"msj": "Estación guardada en DB", "data": nueva_estacion}

@app.get("/estaciones/")
def listar_estaciones(db: Session = Depends(get_db)):
    return db.query(models.Estacion).all()

# --- ENDPOINTS DE LECTURAS ---

@app.post("/lecturas/", status_code=201)
def registrar_lectura(estacion_id: int, valor: float, db: Session = Depends(get_db)):
    # Validar si la estación existe antes de enviarle una lectura
    estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    nueva_lectura = models.Lectura(estacion_id=estacion_id, valor=valor)
    db.add(nueva_lectura)
    db.commit()
    return {"status": "Lectura guardada", "valor": valor}

# --- MOTOR DE RIESGO Y HISTORIAL (RETO SEMANA 2 + SEMANA 3) ---

@app.get("/estaciones/{id}/riesgo")
def obtener_riesgo(id: int, db: Session = Depends(get_db)):
    # Buscar la última lectura en la base de datos
    lectura = db.query(models.Lectura).filter(models.Lectura.estacion_id == id).order_by(models.Lectura.id.desc()).first()
    
    if not lectura:
        return {"id": id, "nivel": "SIN DATOS", "valor": 0}
    
    # Lógica de riesgo (Semana 2)
    valor = lectura.valor
    nivel = "PELIGRO" if valor > 20.0 else "ALERTA" if valor > 10.0 else "NORMAL"
    
    return {"id": id, "valor": valor, "nivel": nivel}

@app.get("/estaciones/{id}/historial")
def obtener_historial(id: int, db: Session = Depends(get_db)):
    # 1. Verificar si la estación existe
    estacion = db.query(models.Estacion).filter(models.Estacion.id == id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    # 2. Traer todas las lecturas de esa estación
    lecturas = db.query(models.Lectura).filter(models.Lectura.estacion_id == id).all()
    valores = [l.valor for l in lecturas]
    
    if not valores:
        return {"estacion": estacion.nombre, "promedio": 0, "conteo": 0}
    
    # 3. Cálculo de promedio
    promedio = sum(valores) / len(valores)
    
    return {
        "estacion_id": id,
        "nombre": estacion.nombre,
        "lecturas": valores,
        "conteo": len(valores),
        "promedio": round(promedio, 2)
    }