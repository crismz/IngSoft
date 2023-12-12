from pydantic import BaseModel

class WelcomeMessage(BaseModel):
    id_jugador: int
    nombre_jugador: str
    posicion: int
