from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Dict, List

app = FastAPI(title="API de Orquestación")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/autenticar-usuario")

# Simulaciones en memoria
users_db = {
    "admin": {"password": "admin123", "role": "Administrador"},
    "orq": {"password": "orq123", "role": "Orquestador"},
    "user": {"password": "user123", "role": "Usuario"}
}
tokens_db = {}  # token: username
services_db = {}
rules_db = {}

# --- Modelos ---

class Servicio(BaseModel):
    nombre: str
    descripcion: str
    endpoints: List[str]

class ReglasOrquestacion(BaseModel):
    reglas: Dict[str, str]

class SolicitudOrquestar(BaseModel):
    servicio_destino: str
    parametros_adicionales: Dict[str, str]

class Credenciales(BaseModel):
    nombre_usuario: str
    contrasena: str

class SolicitudAutorizacion(BaseModel):
    recursos: List[str]
    rol_usuario: str

# --- Utilidades ---

def generar_token(username: str) -> str:
    return f"token-{username}"

def get_current_user(token: str = Depends(oauth2_scheme)):
    username = tokens_db.get(token)
    if not username:
        raise HTTPException(status_code=401, detail="Token inválido")
    return {"username": username, "role": users_db[username]["role"]}

def require_roles(*roles):
    def role_checker(user=Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="No autorizado")
        return user
    return role_checker

# --- Endpoints ---

@app.post("/autenticar-usuario")
def autenticar_usuario(cred: Credenciales):
    usuario = users_db.get(cred.nombre_usuario)
    if not usuario or usuario["password"] != cred.contrasena:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = generar_token(cred.nombre_usuario)
    tokens_db[token] = cred.nombre_usuario
    return {"access_token": token, "token_type": "bearer"}

@app.post("/autorizar-acceso")
def autorizar_acceso(solicitud: SolicitudAutorizacion, user=Depends(require_roles("Administrador", "Orquestador"))):
    # Simula que todos los recursos están permitidos para el rol válido
    return {
        "autorizado": True,
        "rol_usuario": solicitud.rol_usuario,
        "recursos_autorizados": solicitud.recursos
    }

@app.get("/informacion-servicio/{id}")
def obtener_info_servicio(id: str, user=Depends(get_current_user)):
    servicio = services_db.get(id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return {"id": id, "datos": servicio}

@app.post("/registrar-servicio")
def registrar_servicio(servicio: Servicio, user=Depends(require_roles("Administrador"))):
    servicio_id = servicio.nombre.lower().replace(" ", "_")
    services_db[servicio_id] = servicio
    return {"mensaje": "Servicio registrado correctamente", "id": servicio_id}

@app.put("/actualizar-reglas-orquestacion")
def actualizar_reglas(reglas: ReglasOrquestacion, user=Depends(require_roles("Orquestador"))):
    rules_db.update(reglas.reglas)
    return {"mensaje": "Reglas actualizadas", "reglas": rules_db}

@app.post("/orquestar")
def orquestar(solicitud: SolicitudOrquestar, user=Depends(require_roles("Administrador", "Orquestador"))):
    if solicitud.servicio_destino not in services_db:
        raise HTTPException(status_code=404, detail="Servicio de destino no encontrado")
    return {
        "mensaje": "Orquestación exitosa",
        "servicio_destino": solicitud.servicio_destino,
        "parametros_enviados": solicitud.parametros_adicionales
    }
