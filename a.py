from fastapi import FastAPI
from pydantic import BaseModel

app: FastAPI = FastAPI(
    debug=True,
    title="Aplicacion Integracion de Plataformas",
    version="1.0.0"
)

class NewUser(BaseModel):
    name: str
    password: str

@app.get("/")
def _():
    return {
        "message": "Hola Mundo"
    }

@app.post("/user/create")
def createUser():
    return {
        "message": "User created"
    }