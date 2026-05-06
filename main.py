from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import router
from pagos_mp import router_pagos     

app = FastAPI(
    title="EduCore MVP",
    description="REST API core para la gestión escolar y cobranza",
    version="1.0.0"
)

#Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(router_pagos) 

@app.get("/health", tags=["System"])
def check_system_health():
    return {"status": "ok", "message": "API EduCore operativa"}
