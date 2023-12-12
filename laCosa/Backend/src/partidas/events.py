from pydantic import BaseModel, Field
from typing import Optional, List

"""
BaseModels para respuesta de eventos
"""

class EventoJugador(BaseModel):
    id_jugador: int
    nombre_jugador: str
    posicion: int
    tiene_cuarentena: bool = False
    puerta_atrancada_izq: bool = False

class EventoRonda(BaseModel):
    ronda: Optional[List[EventoJugador]] = Field(default_factory=list)

class EventoCarta(BaseModel):
    id: int
    name: str
    type: str
    effectDescription: str
    isSelectable: bool = None
    isPlayable: bool = None
    isDisposable: bool = None
    target: str

    def set_Selectable(self, valor: bool):
        self.isSelectable = valor
        return

    def set_Playable(self, valor: bool):
        self.isPlayable = valor
        return
    
    def set_Disposable(self, valor: bool):
        self.isDisposable = valor
        return

class EventoMano(BaseModel):
    context: str
    rol_jugador: str
    cartas: Optional[List[EventoCarta]] = Field(default_factory=list)

    def agregar_eval_carta(self, ev_carta: EventoCarta) -> None:
        self.cartas.append(ev_carta)
        return

class EventoTurno(BaseModel):
    id_jugador: int

class EventoMazo(BaseModel):
    es_panico: bool

class EventoCartaJugar(BaseModel):
    id: int
    name: str
    type: str
    effectDescription: str

class EventoCartaJugada(BaseModel):
    carta: EventoCartaJugar
    objetivo: int

class EventoObjetivoIntercambio(BaseModel):
    id_jugador: int

class EventoPedidoIntercambio(BaseModel):
    id_jugador: int

class EventoRespuestaIntercambio(BaseModel):
    id_jugador_turno: int
    id_jugador_objetivo: int

class EventoResultadoDefensa(BaseModel):
    nombre_jugador: str
    id_jugador: int

class EventoFinalizoPartida(BaseModel):
    rol_ganador: str
    contexto: str

class EventoDescartarCarta(BaseModel):
    id_jugador: int

class EventoChat(BaseModel):
    emisor: str
    mensaje: str

class EventoMostrarCartas(BaseModel):
    id: int
    name: str
    type: str
    effectDescription: str 

class EventoMostrarMano(BaseModel):    
    id_jugador: int
    cartas: List[EventoMostrarCartas] = Field(default_factory=list)

class EventoLobbyJugador(BaseModel):
    name: str

class EventoLobbyJugadores(BaseModel):
    jugadores: Optional[List[EventoLobbyJugador]] = Field(default_factory=list)

class EventoLobbyIniciada(BaseModel):
    partida_iniciada: bool

class EventoLog(BaseModel):
    mensaje: str

class EventoRevelar(BaseModel):
    id_jugador: int

class EventoMuerte(BaseModel):
    contexto: str
    nombre_jugador: str = ""
