from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, database # El punto (.) indica que están en la misma carpeta

# Inicialización de la Base de Datos
models.Base.metadata.create_all(bind=database.engine)

# --- METADATOS DE DOCUMENTACIÓN (Lab 4.2) ---
app = FastAPI(
    title="SMAT - Sistema de Monitoreo FISI UNMSM",
    description="""
    ## API Profesional de Telemetría y Alerta Temprana
    Esta API permite gestionar estaciones de monitoreo y procesar lecturas de sensores con seguridad avanzada.
    * **Arquitectura:** Estructura modular /app.
    * **Seguridad:** Implementación de JWT (OAuth2).
    * **Persistencia:** SQLite con SQLAlchemy.
    """,
    version="1.6.2",
    contact={"name": "Juan Carlos", "email": "juan.carlos@unmsm.edu.pe"}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite conexiones de cualquier origen (Chrome, Móvil)
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- CONFIGURACIÓN DE SEGURIDAD (Lab 4.4) ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token", tags=["Seguridad"], summary="Obtener token de acceso")
async def login():
    # En una app real se validaría usuario/password. Aquí usamos una llave estática para el lab.
    return {"access_token": "token_secreto_unmsm_2026", "token_type": "bearer"}

# Dependencia para la DB
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINTS PROTEGIDOS ---

@app.post("/estaciones/", status_code=status.HTTP_201_CREATED, tags=["Gestión"], summary="Registrar nueva estación")
def crear_estacion(id: int, nombre: str, ubicacion: str, 
                   db: Session = Depends(get_db), 
                   token: str = Depends(oauth2_scheme)): # Pide el token
    if token != "token_secreto_unmsm_2026":
        raise HTTPException(status_code=401, detail="No autorizado")
    
    existe = db.query(models.Estacion).filter(models.Estacion.id == id).first()
    if existe:
        raise HTTPException(status_code=400, detail="El ID ya existe")
    
    nueva = models.Estacion(id=id, nombre=nombre, ubicacion=ubicacion)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@app.post("/lecturas/", status_code=201, tags=["Telemetría"], summary="Registrar lectura de sensor")
def registrar_lectura(estacion_id: int, valor: float, 
                      db: Session = Depends(get_db),
                      token: str = Depends(oauth2_scheme)):
    estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    nueva = models.Lectura(estacion_id=estacion_id, valor=valor)
    db.add(nueva)
    db.commit()
    return {"status": "Lectura guardada", "valor": valor}

# --- ENDPOINTS DE CONSULTA ---

@app.get("/estaciones/{id}/historial", tags=["Reportes Históricos"], summary="Promedio y lista de lecturas")
def obtener_historial(id: int, db: Session = Depends(get_db)):
    estacion = db.query(models.Estacion).filter(models.Estacion.id == id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    lecturas = db.query(models.Lectura).filter(models.Lectura.estacion_id == id).all()
    valores = [l.valor for l in lecturas]
    promedio = sum(valores) / len(valores) if valores else 0
    
    return {
        "estacion": estacion.nombre,
        "conteo": len(valores),
        "promedio": round(promedio, 2),
        "lecturas": valores
    }

@app.get("/estaciones/", tags=["Gestión"])
def listar(db: Session = Depends(get_db)):
    return db.query(models.Estacion).all()