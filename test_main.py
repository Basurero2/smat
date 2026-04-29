from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_crear_estacion():
    response = client.post("/estaciones/", json={
        "id": 1, "nombre": "Estación Rímac", "ubicacion": "Chosica"
    })
    assert response.status_code == 201
    assert response.json()["data"]["nombre"] == "Estación Rímac"

    

def test_historial_y_promedio():
    # Registramos estación y 3 lecturas: 10.0, 20.0, 30.0 (Promedio = 20.0)
    client.post("/estaciones/", json={"id": 20, "nombre": "Río Yauli", "ubicacion": "La Oroya"})
    client.post("/lecturas/", json={"estacion_id": 20, "valor": 10.0})
    client.post("/lecturas/", json={"estacion_id": 20, "valor": 20.0})
    client.post("/lecturas/", json={"estacion_id": 20, "valor": 30.0})
    
    response = client.get("/estaciones/20/historial")
    assert response.status_code == 200
    assert response.json()["promedio"] == 20.0