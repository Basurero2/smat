from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Estacion(Base):
    __tablename__ = "estaciones"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    ubicacion = Column(String)

class Lectura(Base):
    __tablename__ = "lecturas"
    id = Column(Integer, primary_key=True, index=True)
    estacion_id = Column(Integer)
    valor = Column(Float)