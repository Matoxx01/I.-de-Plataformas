from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Orquestación de Servicios")

# --- Simulación de usuarios y tokens/Roles ---
fake_users = {
    "alice": {"password": "secret1", "role": "Administrador"},
    "bob":   {"password": "secret2", "role": "Orquestador"},
    "eve":   {"password": "secret3", "role": "Usuario"}
}
fake_tokens = {}  # token -> username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="autenticar-usuario")

def get_current_user(token: str = Depends(oauth2_scheme)):
    username = fake_tokens.get(token)
    if not username:
        raise HTTPException(status_code=401, detail="Token inválido")
    return {"username": username, "role": fake_users[username]["role"]}

def require_role(*roles):
    def checker(user=Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="No autorizado")
        return user
    return checker

# --- Modelos ---
class OrquestarRequest(BaseModel):
    servicio_destino: str
    parametros_adicionales: Dict

class RegistrarServicioRequest(BaseModel):
    nombre: str
    descripcion: str
    endpoints: List[str]

class ActualizarReglasRequest(BaseModel):
    reglas: Dict

class AutenticarRequest(BaseModel):
    nombre_usuario: str
    contrasena: str

class AutorizarRequest(BaseModel):
    recursos: List[str]
    rol_usuario: str

# --- Endpoints ---

@app.post("/autenticar-usuario")
def autenticar(req: AutenticarRequest):
    user = fake_users.get(req.nombre_usuario)
    if not user or user["password"] != req.contrasena:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    # Generar token (simple)
    token = f"token-{req.nombre_usuario}"
    fake_tokens[token] = req.nombre_usuario
    return {"access_token": token, "token_type": "bearer"}

@app.post("/autorizar-acceso")
def autorizar(req: AutorizarRequest, user=Depends(require_role("Administrador", "Orquestador"))):
    # Ejemplo simple: si el rol pedido coincide con un rol permitido
    if req.rol_usuario not in ["Administrador", "Orquestador", "Usuario"]:
        raise HTTPException(status_code=400, detail="Rol desconocido")
    return {"authorized": True, "recursos": req.recursos}

@app.post("/orquestar")
def orquestar(req: OrquestarRequest, user=Depends(require_role("Administrador", "Orquestador"))):
    # Lógica de orquestación simulada
    return {
        "status": "Orquestación exitosa",
        "servicio": req.servicio_destino,
        "parametros": req.parametros_adicionales
    }

@app.get("/informacion-servicio/{id}")
def informacion_servicio(id: str, user=Depends(get_current_user)):
    # Simulación: devolver datos dummy
    return {"id": id, "nombre": f"Servicio {id}", "endpoints": [f"/serv/{id}/accion"]}

@app.post("/registrar-servicio")
def registrar_servicio(req: RegistrarServicioRequest, user=Depends(require_role("Administrador"))):
    # Simular guardado
    return {"status": "Servicio registrado", "servicio": req}

@app.put("/actualizar-reglas-orquestacion")
def actualizar_reglas(req: ActualizarReglasRequest, user=Depends(require_role("Orquestador"))):
    # Simulación actualizando reglas
    return {"status": "Reglas actualizadas", "reglas": req.reglas}
