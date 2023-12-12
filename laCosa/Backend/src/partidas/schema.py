from partidas.mazo.schema import Mazo
from partidas.jugadores.schema import Jugador

from typing import List, Tuple, Optional, Dict
from pydantic import BaseModel, Field

"""
Clase para posiciones, cada posición es una Tupla donde menciona si esta bloqueado
el lado izquierdo y/o derecho (0 el izquierdo y 1 el derecho)

Ejemplo: el lado izquierdo de 1 es 0, el lado derecho de 1 es 2.
            0   
        7       1
      6            2
        5       3
            4

"""

class Posicion(BaseModel):
    pos: Tuple[bool, bool] = [False, False]

    def get(self, lado: int):
        return self.pos[lado]

    def bloquear_pos(self, lado: int):
        self.pos[lado] =  True
    
    def desbloquear_pos(self, lado: int):
        self.pos[lado] =  False


"""
Schema de partida
"""

class Partida(BaseModel):
    id: Optional[int] = None
    nombre: str
    contraseña: Optional[str] = None
    num_jugadores: Optional[int] = 0
    num_jugadores_inicial: Optional[int] = 0
    max_jugadores: int
    min_jugadores: int
    posiciones: Optional[List[Posicion]] = Field(default_factory=list)
    turno: Optional[int] = 0
    sentido: Optional[bool] = False
    mazo: Optional[Mazo] = None
    jugadores: Optional[List[Jugador]] = Field(default_factory=list)
    iniciada: Optional[bool] = False
    finalizada: Optional[bool] = False
    conexiones: Dict[int, List[Tuple[BaseModel, str]]] = {}
    stack : List[Tuple[int, int]] = []
    jugadores_listos: int = 0
    
    def get_posiciones(self) -> List[Posicion]:
        return self.posiciones

    def iniciar(self):
        self.iniciada = True
        return
    
    
    def esta_iniciada(self) -> bool:
        return self.iniciada
    
    def finalizar(self):
        self.finalizada = True
        return
    
    def esta_finalizada(self) -> bool:
        return self.finalizada

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
    
    def set_contraseña(self, contraseña: str):
        self.contraseña = contraseña
        return

    def get_contraseña(self) -> str:
        return self.contraseña

    def set_num_jugadores(self, num_jug: int):
        self.num_jugadores = num_jug
        return

    def get_num_jugadores(self) -> int:
        return self.num_jugadores

    def set_num_jugadores_inicial(self, num_jug: int):
        self.num_jugadores_inicial = num_jug
        return
    
    def get_num_jugadores_inicial(self) -> int:
        return self.num_jugadores_inicial

    def set_max_jugadores(self, max_jug: int):
        self.max_jugadores = max_jug
        return

    def get_max_jugadores(self) -> int:
        return self.max_jugadores
    
    def set_min_jugadores(self, min_jug: int):
        self.min_jugadores = min_jug
        return

    def get_min_jugadores(self) -> int:
        return self.min_jugadores

    def get_jugadores(self) -> List[Jugador]:
        return self.jugadores

    def agregar_posicion(self, posicion: Posicion):
        self.posiciones.append(posicion)
        return

    def proximo_en_ronda(self, posicion: int) -> Jugador:
        if self.get_sentido():
            return self.buscar_jugador_por_posicion(
                                (posicion+1) % self.get_num_jugadores())
        else:
            return self.buscar_jugador_por_posicion(
                                (posicion-1) % self.get_num_jugadores())

    def proximo_turno(self) -> int:
        cantidad_jugadores = self.get_num_jugadores()
        turno = self.get_turno()
        sentido = self.get_sentido()
        if sentido:
            turno = (turno + 1) % cantidad_jugadores
        else:
            turno = (turno - 1) % cantidad_jugadores
        return turno

    def son_adyacentes(self, posicion_a: int, posicion_b: int) -> bool:
        # NOTA: Estos comentarios se deberían borrar en la PR
        # Chequeamos que el input es válido
        cantidad_jugadores = self.get_num_jugadores()
        if posicion_a < 0 or posicion_a >= cantidad_jugadores:
            return False
        if posicion_b < 0 or posicion_b >= cantidad_jugadores:
            return False

        # Queremos chequear que las posiciones son consecutivas
        # Podemos pensar en la ronda como en un arreglo circular
        # La idea es que si dos jugadores son adyacentes, la diferencia
        # absoluta será 1 cuando no estemos comparando la primera y la
        # última posición, y en este último caso será la
        # cantidad de jugadores - 1 (o de igual manera, el número de
        # la última posición en la ronda)
        diferencia = abs(posicion_a-posicion_b)
        adyacentes = diferencia == 1 or diferencia == cantidad_jugadores-1
        return adyacentes

    def hay_bloqueo(self, posicion_a: int, posicion_b: int) -> bool:
        # Asumimos que las dos posiciones son adyacentes,
        # que son dos posiciones distintas
        # y que los dos lados correspondientes al mismo
        # "punto de bloqueo" están seteados al mismo
        # valor de verdad.
        # Calculamos que posición está más a la derecha
        # y devolvemos el estado de su lado izquierdo

        if posicion_a == posicion_b:
            return self.posiciones[posicion_a].get(1)

        cantidad_jugadores = self.get_num_jugadores()
        extremes = [0, cantidad_jugadores-1]

        # Cuando nos interesa el "punto de bloqueo"
        # entre la primera y la última posición
        if posicion_a in extremes and posicion_b in extremes:
            posicion = self.posiciones[0]
        # Cuando nos interesa el "punto de bloqueo"
        # entre cualquier otro par de posiciones
        else:
            diestra = max(posicion_a, posicion_b)
            posicion = self.posiciones[diestra]
        
        return posicion.get(0)

    def bloquear_posicion(self, num_pos: int, lado: int):
        # Bloqueamos el lado de la posición dada
        posicion = self.posiciones[num_pos]
        posicion.bloquear_pos(lado)

        cantidad_jugadores = self.get_num_jugadores()     

        # Conseguimos lado contrario
        lado_contrario = abs(lado-1)

        if lado_contrario == 0:
            lado_a_bloquear = self.posiciones[(num_pos + 1) % cantidad_jugadores]
        elif lado_contrario == 1:
            lado_a_bloquear = self.posiciones[(num_pos - 1) % cantidad_jugadores]

        lado_a_bloquear.bloquear_pos(lado_contrario)

        return
    
    def desbloquear_posicion(self, num_pos: int, lado: int):
        # Desbloqueamos el lado de la posición dada
        posicion = self.posiciones[num_pos]
        posicion.desbloquear_pos(lado)     

        # Conseguimos lado contrario
        lado_contrario = abs(lado-1)

        cantidad_jugadores = self.get_num_jugadores()  

        if lado_contrario == 0:
            lado_a_desbloquear = self.posiciones[(num_pos + 1) % cantidad_jugadores]
        elif lado_contrario == 1:
            lado_a_desbloquear = self.posiciones[(num_pos - 1) % cantidad_jugadores]

        lado_a_desbloquear.desbloquear_pos(lado_contrario)

    def desbloquear_posiciones(self):
        for each in self.posiciones:
            each.desbloquear_pos(0)
            each.desbloquear_pos(1)
        return

    # Se elimina antes de eliminar al jugador (antes de actualizar el num_jugadores)
    def eliminar_posicion(self, num_pos: int):
        cantidad_jugadores = self.get_num_jugadores()
        # Al eliminar la posición se desaparecen 
        # las puertas atrancadas vinculadas a la misma

        # Si la posición a eliminar es la primera
        if num_pos == 0:
            self.posiciones[1].desbloquear_pos(0)
            self.posiciones[cantidad_jugadores-1].desbloquear_pos(1)

        # Si la posición a eliminar es la última
        elif num_pos == cantidad_jugadores-1:
            self.posiciones[cantidad_jugadores-2].desbloquear_pos(1)
            self.posiciones[0].desbloquear_pos(0)

        # Si la posición a eliminar es una intermedia
        else:
            self.posiciones[num_pos+1].desbloquear_pos(0)
            self.posiciones[num_pos-1].desbloquear_pos(1)

        self.posiciones.pop(num_pos)

        return

    def set_turno(self, turno: int):
        self.turno = turno
        return

    def get_turno(self) -> int:
        return self.turno
	
    def set_sentido(self, sentido: bool):
        self.sentido = sentido
        return

    def get_sentido(self) -> bool:
        return self.sentido

    def set_mazo(self, mazo: Mazo):
        self.mazo = mazo
        return

    def get_mazo(self) -> Mazo:
        return self.mazo

    def eliminar_jugador(self, jugador: Jugador):
        if self.esta_iniciada():
            # Obtenemos posición
            posicion = jugador.get_posicion()
            # Eliminamos la posición
            self.eliminar_posicion(num_pos=posicion)

            if self.get_turno() > posicion:
                self.set_turno(self.get_turno()-1)
                
            # Actualizamos las posiciones 
            # del resto de los jugadores
            for each in self.jugadores:
                if each.get_posicion() > posicion:
                    each.set_posicion(each.get_posicion()-1)
    
        # Eliminamos al jugador
        self.jugadores.remove(jugador)
        self.set_num_jugadores(self.get_num_jugadores()-1)  
        
        return 

    def agregar_jugador(self, jugador: Jugador):
        self.jugadores.append(jugador)
        self.set_num_jugadores(self.get_num_jugadores()+1)
        return

    def buscar_jugador(self, id_jugador: int) -> Optional[Jugador]:
        result = None
        for each in self.jugadores:
            if each.get_id() == id_jugador:
                result = each 
        return result

    def buscar_jugador_por_posicion(self, posicion: int) -> Optional[Jugador]:
        result = None
        for each in self.jugadores:
            if each.get_posicion() == posicion:
                result = each
                break
        return result

    def existe_jugador(self, id_jugador: int) -> bool:
        for jugador in self.jugadores:
            if jugador.get_id() == id_jugador:
                return True
        return False
      
    def obtener_jugadores(self) -> List[Jugador]:
        return self.jugadores
    
    def is_connected(self, id_jugador:int) -> bool:
        return id_jugador in self.conexiones
    
    def connect(self, id_jugador) -> None:
        self.conexiones[id_jugador] = []
    
    def post_event(self, id_jugador:int, event: BaseModel, event_name: str) -> None:
        if self.is_connected(id_jugador):
            self.conexiones[id_jugador].append((event, event_name))
    
    def has_events(self, id_jugador: int) -> bool:
        if self.is_connected(id_jugador):
            return self.conexiones[id_jugador] != []
        else:
            return False
        
    def get_event(self, id_jugador:int) -> BaseModel:
        if self.is_connected(id_jugador):
            return self.conexiones[id_jugador].pop(0)
    
    def terminate_connection(self, id_jugador: int) -> None:
        if self.is_connected(id_jugador):
            del self.conexiones[id_jugador]

    def terminate_every_connection(self) -> None:
        self.conexiones = {}

    def broadcast(self, msg: BaseModel, event_name: str) -> None:
        for each in self.conexiones:
            self.post_event(each, msg, event_name)

    def apilar(self, tupla: Tuple[int, int]) -> None:
        self.stack.append(tupla)

    def desapilar(self) -> Optional[Tuple[int, int]]:
        if self.stack == []:
            return None
        else:
            result = self.stack.pop()
            return result
        
    def get_largo_stack(self) -> int:
        return len(self.stack)
    
    def todos_infectados(self):
        for each in self.obtener_jugadores():
            if (each.get_rol() != "Infectado" and 
                each.get_rol() != "La Cosa"):
                return False
        return True

    def sumar_jugador_listo(self) -> None:
        if self.jugadores_listos < self.num_jugadores:
            self.jugadores_listos += 1
        return
    
    def todos_listos(self) -> bool:
        return self.jugadores_listos == self.num_jugadores
    
    def reiniciar_listos(self) -> None:
        self.jugadores_listos = 0
        return
"""
Clase para datos de crear partida
"""

class DatosCrearPartida(BaseModel):
    nombre_partida: str
    contraseña: Optional[str] = None
    max_jugadores: int
    min_jugadores: int
    nombre_jugador: str



"""
Clase para respuesta de crear partida
"""

class RespuestaCrearPartida(BaseModel):
    id_partida: int
    id_jugador: int

"""
Clase para Datos de unir jugador
"""
      
class DatosUnion(BaseModel):
    nombre_jugador: str
    contraseña:str = None

"""
Clase para Datos de Iniciar partida
"""

class DatosInicio(BaseModel):
    id_jugador: int


"""
Clase Lista para partidas
"""

class ListaPartida(BaseModel):
    lista: List[Partida] = Field(default_factory=list)

    def append(self, partida: Partida):
        self.lista.append(partida)
        return
    
    def remove(self, partida: Partida):
        self.lista.remove(partida)
        return
    
    def get_length(self) -> int:
        return len(self.lista)
    
    def get_partida_by_index(self, index: int) -> Partida:
        if index < 0 or index >= len(self.lista):
            return None
        return self.lista[index]

    def get_index_by_id(self, id_param: int) -> int:
        index = 0
        while index < len(self.lista):
            if self.lista[index].get_id() == id_param:
                break
            else:
                index += 1

        if index == len(self.lista):
            return -1
    
        return index

    def eliminar_partida(self, partida: Partida):
        self.lista.remove(partida)
        return


"""
Clase Respuesta Partida 
"""
class PartidaOut(BaseModel):
    id_partida: int
    nombre_partida: str
    jugadores_act: int
    max_jugadores: int
    tiene_contraseña: bool


"""
Clase Lista de Respuesta Partida
"""
class ListaPartidaOut(BaseModel):
    lista: List[PartidaOut] = Field(default_factory=list)

    def append(self, partida: PartidaOut):
        self.lista.append(partida)
        return
    
    def remove(self, partida: PartidaOut):
        self.lista.remove(partida)
        return
    
    def get_length(self) -> int:
        return len(self.lista)

"""
Clase para Datos de Chat
"""
class ChatInput(BaseModel):
    id_jugador: int
    mensaje: str

"""
Clase para info de la defensa contra intercambios
"""
class DefIntercambioInput(BaseModel):
    id_carta: int