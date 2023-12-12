from pydantic import BaseModel, Field
from typing import List, Optional, Dict

from partidas.mazo.cartas.schema import CardSchema

class Jugador(BaseModel):
    id: int
    nombre: str
    posicion: int = None
    rol: str = None
    mano: Optional[List[CardSchema]] = Field(default_factory=list)
    cuarentena: bool = False
    # Datos para poder intercambiar cartas
    id_carta_intercambio: int = -1
    # -1 quiere decir "objetivo por defecto" aka el que sigue en la ronda
    id_objetivo_intercambio: int = -1 
    # Inmunidad temporal a Infección por <<¡Fallaste!>> o sucesos similares
    inmunidad_infeccion: bool = False
    # El número de acciones restantes nunca debería bajar de 0
    acciones_restantes: Dict[str, int] = {"robos": 0, "descartes": 0, "intercambios": 0}
    # Flag <<Olvidadizo>>
    listo_para_intercambiar: bool = True
    # Contador para cuarentena
    rondas_en_cuarentena: int = 0

    def set_id(self, id: int):
        self.id = id
        return  
      
    def get_id(self) -> int:
        return self.id
    
    def set_nombre(self, nombre: str):
        self.nombre = nombre
        return

    def get_nombre(self) -> str:
        return self.nombre
    
    def set_posicion(self, pos: int):
        self.posicion = pos
        return
    
    def get_posicion(self) -> int:
        return self.posicion

    def set_rol(self, rol: str):
        self.rol = rol
        return
    
    def get_rol(self) -> str:
        return self.rol
    
    def set_mano(self, mano: List[CardSchema]):
        self.mano = mano
        return

    def get_mano(self) -> List[CardSchema]:
        return self.mano
    
    def agregar_carta_mano(self, carta: CardSchema):
        self.mano.append(carta)
        return
    
    def remover_carta_mano(self, id_carta: int) -> CardSchema:
        mano_temp = self.mano.copy()
        self.mano.clear()
        carta_ret = None
        
        for ind in range(len(mano_temp)):
            if mano_temp[ind].id == id_carta:
                carta_ret = mano_temp[ind]
            else:
                self.mano.append(mano_temp[ind])
        
        mano_temp.clear()
        return carta_ret
    
    def remover_mano(self) -> List[CardSchema]:
        cartas = self.mano.copy()
        self.mano.clear()
        return cartas
    
    def tiene_en_mano(self, id_carta: int) -> bool:
        for each in self.mano:
            if each.get_id() == id_carta:
                return True
        return False
    
    def obtener_carta(self, id_carta: int) -> Optional[CardSchema]:
        # Obtiene una referencia a la carta indicada sin descartarla
        for each in self.mano:
            if each.get_id() == id_carta:
                return each
        return None

    def poner_en_cuarentena(self):
        self.cuarentena = True
        self.rondas_en_cuarentena = 2
        return
    
    def sacar_de_cuarentena(self):
        self.cuarentena = False
        return
    
    def esta_en_cuarentena(self):
        return self.cuarentena

    def set_id_carta_intercambio(self, id_carta: int) -> None:
        self.id_carta_intercambio = id_carta
        return
    
    def get_id_carta_intercambio(self) -> int:
        return self.id_carta_intercambio

    def set_id_objetivo_intercambio(self, valor: int) -> None:
        self.id_objetivo_intercambio = valor
        return
    
    def get_id_objetivo_intercambio(self) -> int:
        return self.id_objetivo_intercambio
    
    def get_inmunidad(self) -> bool:
        return self.inmunidad_infeccion
    
    def set_inmunidad(self, valor: bool) -> None:
        self.inmunidad_infeccion = valor
        return

    def añadir_accion(self, accion: str) -> None:
        self.acciones_restantes[accion] += 1
        return

    def quedan_acciones(self, accion: str) -> bool:
        return self.acciones_restantes[accion] > 0
    
    def restar_accion(self, accion: str) -> None:
        self.acciones_restantes[accion] -= 1
        return
    
    def set_accion(self, accion: str, cantidad: int) -> None:
        self.acciones_restantes[accion] = cantidad
        return
    
    def resetear_acciones(self) -> None:
        self.acciones_restantes["robos"] = 0
        self.acciones_restantes["descartes"] = 0
        self.acciones_restantes["intercambios"] = 0
        return

    def set_listo_para_intercambio(self, valor: bool) -> None:
        self.listo_para_intercambiar = valor
        return
    
    def get_listo_para_intercambio(self) -> bool:
        return self.listo_para_intercambiar

"""
  Schema para respuesta de ver mano
"""

class RespuestaMano(BaseModel):
    rol: str
    cartas: List[CardSchema]

"""
  Clase para Datos de Intercambiar Carta
"""
class IntercambioIn(BaseModel):
    id_carta: int
    #id_jugador_objetivo: int

"""
  Clase para Datos de Respuesta Intercambio
"""
      
class RespuestaIntercambioIn(BaseModel):
    id_carta: int

"""
    Clase para Datos de Jugar Carta
"""
class DatosJugarCarta(BaseModel):
    id_carta: int
    id_objetivo: int

"""
    Clase para Datos de Jugar Defensa
"""
class DatosJugarDefensa(BaseModel):
    id_carta: int

class IdCartaIn(BaseModel):
    id_carta: int

class RevelarIn(BaseModel):
    revela: bool
