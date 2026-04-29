from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Definimos el nombre del archivo de base de datos
SQLALCHEMY_DATABASE_URL = "sqlite:///./smat.db"

# 2. Creamos el motor (engine)
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# 3. Creamos la sesión para hacer consultas
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Clase base para los modelos
Base = declarative_base()


