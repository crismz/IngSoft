from partidas.schema import ListaPartida, DatosCrearPartida, Partida
from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.schema import CardSchema
from partidas.jugadores.schema import Jugador
from partidas.models import PartidaDB

from pony.orm import db_session, select, exists
import random
from typing import List
from pydantic import BaseModel
from fastapi import HTTPException

from partidas.events import *

"""
Constante que guarda el límite de caracteres por mensaje
"""
CHAR_LIMIT_PER_MESSAGE = 150

"""
Variable que guarda una lista de partidas para manejar en memoria del Backend
"""
lista_partidas = ListaPartida()

"""
Funciones utiles para partidas
"""

def eliminar_partida(current_partida: Partida):
    # Borramos los objetos usados en la partida
    del current_partida.mazo
    # Borramos los jugadores de la partida por las dudas,
    # ya tendria que estár borrado de antes
    for j in current_partida.obtener_jugadores():
        current_partida.eliminar_jugador(jugador=j)

    # Cortamos todas las conexiones por si las dudas,
    # ya no tendría que quedar conexiones de antes
    current_partida.terminate_every_connection()

    # Antes de borrar la partida, guardamos su id
    id = current_partida.get_id()

    # Removemos y eliminamos la partida
    lista_partidas.eliminar_partida(current_partida)
    del current_partida

    # Borramos la partida de la base de datos
    with db_session:
        part = select(p for p in PartidaDB if p.partida_id==id)
        if part.exists():
            part.delete()
    
    return


def verificar_datos_creacion(partida_info: DatosCrearPartida):
    # Chequeo que los string cumplan las especificaciones
    if (' ' == partida_info.nombre_partida or len(partida_info.nombre_partida) > 32 or
       ' ' == partida_info.nombre_jugador or len(partida_info.nombre_jugador) > 16 or
       ' ' in partida_info.contraseña or len(partida_info.contraseña) > 32):
        return False

    # Chequeo que el max_jugador y min_jugador esté dentro de las reglas
    if (partida_info.max_jugadores > 12 or partida_info.min_jugadores < 4
        or partida_info.max_jugadores < partida_info.min_jugadores) :
        return False
    
    return True

def repartir_cartas(mazo: Mazo, jugadores: List[Jugador]):
    # Mazo temporal para repartir cartas
    aux: List[CardSchema] = []

    # Sacamos las cartas según la cantidad de jugadores * 4
    for i in range(4*len(jugadores)):
        aux.append(mazo.take_card())
            
    # Mezclamos el mazo a repartir
    random.shuffle(aux)

    # Repartimos las cartas a los jugadores
    for i in range(4):
        for jugador in jugadores:
            card = aux.pop()
            jugador.agregar_carta_mano(card)
            if card.get_name() == "La cosa":
                jugador.set_rol("La Cosa")
    # Mezclamos el resto del mazo
    mazo.shuffle_cards()


def primer_turno(cant_jugadores: int) -> int:
    return random.randint(0, cant_jugadores - 1)

def get_vecinos(pos_robo: int, partida: Partida):
    jugadores = partida.obtener_jugadores()
    if len(jugadores) == 2:
        if pos_robo == 0:
            jugador = partida.buscar_jugador_por_posicion(1)
            return [jugador, jugador]
        else:   
            jugador = partida.buscar_jugador_por_posicion(0)
            return [jugador, jugador] 
    elif pos_robo == 0:
        pos_1 = partida.get_num_jugadores() - 1
        pos_2 = pos_robo + 1
    elif pos_robo == (partida.get_num_jugadores() - 1):
        pos_1 = pos_robo - 1
        pos_2 = 0
    else:
        pos_1 = pos_robo - 1
        pos_2= pos_robo + 1
    vecino1: Jugador = None
    vecino2: Jugador = None
    each: Jugador
    for each in partida.obtener_jugadores():
        if each.get_posicion() == pos_1:
            vecino1 = each
        elif each.get_posicion() == pos_2:
            vecino2 = each

    return [vecino1, vecino2]


def armar_broadcast(_partida_: Partida, msg: BaseModel, event_name: str):
    try:
        _partida_.broadcast(msg, event_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Stream Malfunction")



def intercambiable(id_carta: int, tipo_carta: str, rol: str, mano: List[CardSchema]) -> bool:
    permitido = True
    match rol:
        case "Humano":
            # Lo único que no puede intercambiar son cartas de Infección
            if tipo_carta == "Contagio":
                permitido = False

        case "Infectado":
            # Puede, además de lo permitido a Humano, intercambiar cartas de Infección sólo con La Cosa
            if tipo_carta == "Contagio":
                num_infecciones = 0
                for each in mano:
                    if each.get_type() == "Contagio":
                        num_infecciones += 1
                permitido = (num_infecciones >= 2)

        case "La Cosa":
            # Puede intercambiar cualquier carta (excepto la de La Cosa) con cualquier jugador
            if id_carta == 1:
                permitido = False
    
    return  permitido

def descartable(id_carta: int, tipo_carta: str, rol: str, mano: List[CardSchema]) -> bool:
    permitido = True
    match rol:
        case "Humano":
            # No tiene limitaciones a la hora de descartar
            pass

        case "Infectado":
            # EN TEORÍA, puede descartar cualquier carta mientras conserve UNA (1) de Infección en mano
            if tipo_carta == "Contagio":
                num_infecciones = 0
                for each in mano:
                    if each.get_type() == "Contagio":
                        num_infecciones += 1
                permitido = (num_infecciones >= 2)

        case "La Cosa":
            # Puede descartar cualquier carta, excepto la de La Cosa
            if id_carta == 1:
                permitido = False
    
    return permitido

# Defino diccionarios para facilitar el filtrado según las circunstancias que involucran a la mano
selectables_dict = {
                    "Jugar_Descartar": lambda id, type, role, hand, panicking: 
                                            type == "Panico" if panicking 
                                            else descartable(id_carta=id, tipo_carta=type, rol=role, mano=hand) or 
                                            (type != "Contagio" and type != "Defensa"),
                    "Intercambiar": lambda id, type, role, hand, panicking: 
                                        intercambiable(id_carta=id, tipo_carta=type, rol=role, mano=hand), 
                    "Intercambiar_Defender": lambda id, type, role, hand, panicking:
                                                intercambiable(id_carta=id, tipo_carta=type, rol=role, mano=hand) or
                                                type == "Defensa",
                    "Defender": lambda id, type, role, hand, panicking: type == "Defensa",
                    "Esperar": lambda id, type, role, hand, panicking: False,
                    "Descartar": lambda id, type, role, hand, panicking: 
                                    descartable(id_carta=id, tipo_carta=type, rol=role, mano=hand)
}

playables_dict = {
                    "Jugar_Descartar": lambda type, panicking: 
                                            type == "Panico" if panicking 
                                            else (type != "Contagio" and type != "Defensa"),
                    "Intercambiar": lambda type, panicking: False,
                    "Intercambiar_Defender": lambda type, panicking:
                                                type == "Defensa",
                    "Defender": lambda type, panicking: type == "Defensa",
                    "Esperar": lambda type, panicking: False,
                    "Descartar": lambda type, panicking: False
}

disposables_dict = {
                    "Jugar_Descartar": lambda id, type, role, hand, panicking: 
                                        False if panicking 
                                        else descartable(id_carta=id, tipo_carta=type, rol=role, mano=hand),
                    "Intercambiar": lambda id, type, role, hand, panicking: False,
                    "Intercambiar_Defender": lambda id, type, role, hand, panicking: False,
                    "Defender": lambda id, type, role, hand, panicking: False,
                    "Esperar": lambda id, type, role, hand, panicking: False,
                    "Descartar": lambda id, type, role, hand, panicking: 
                                    descartable(id_carta=id, tipo_carta=type, rol=role, mano=hand)
}

##### TODOS LOS EVENTOS SE LLAMAN "Mano", PERO LO QUE LOS DIFERENCIA UNO DE OTROS PARA EL FRONT ES
##### <<context>>; <<instancia>> ES QUÉ VAMOS A HACER CON LAS CARTAS, PERO ESO EL FRONT NO LO VE
def armador_evento_mano(jugador: Jugador, instancia: str, context: str) -> EventoMano:
    rol = jugador.get_rol()
    mano = jugador.get_mano()
    resultado = EventoMano(context=context, rol_jugador=rol, cartas=[])
    carta: CardSchema
    hay_panico = False

    for carta in mano:
        hay_panico = hay_panico or (carta.get_type() == "Panico")
        
    for carta in mano:
        evaluacion_carta = EventoCarta(id=carta.get_id(), 
                                       name=carta.get_name(), 
                                       type=carta.get_type(),
                                       effectDescription=carta.get_effect(),
                                       target=carta.get_target())
        
        select_func = selectables_dict.get(instancia)
        evaluacion_carta.set_Selectable(select_func(carta.get_id(), carta.get_type(), rol, mano, hay_panico))

        play_func = playables_dict.get(instancia)
        evaluacion_carta.set_Playable(play_func(carta.get_type(), hay_panico))

        dispose_func = disposables_dict.get(instancia)
        evaluacion_carta.set_Disposable(dispose_func(carta.get_id(), carta.get_type(), rol, mano, hay_panico))

        resultado.agregar_eval_carta(ev_carta=evaluacion_carta)

    return resultado

def armador_ronda(id_partida: int) -> EventoRonda:
    ronda = EventoRonda()
    index = lista_partidas.get_index_by_id(id_partida)
    partida: Partida = lista_partidas.get_partida_by_index(index)
    
    jugadores = partida.obtener_jugadores()
    for jugador in jugadores:    

        posiciones = partida.get_posiciones()
        posicion_jugador = posiciones[jugador.get_posicion()]
        pos_izq = posicion_jugador.pos[1]

        ronda.ronda.append(EventoJugador(id_jugador=jugador.get_id(), 
                                         nombre_jugador=jugador.get_nombre(), 
                                         posicion=jugador.get_posicion(),
                                         tiene_cuarentena=jugador.esta_en_cuarentena(),
                                         puerta_atrancada_izq=pos_izq))
    return ronda

def armador_evento_turno(id_partida: int) -> EventoTurno:
    index = lista_partidas.get_index_by_id(id_partida)
    turno = lista_partidas.get_partida_by_index(index).get_turno()
    jugador_turno = lista_partidas.get_partida_by_index(index).buscar_jugador_por_posicion(turno)
    return EventoTurno(id_jugador=jugador_turno.get_id())

def armador_evento_mazo(partida: Partida):
    es_panico : bool = partida.get_mazo().get_first_card_type() == "Panico"
    return EventoMazo(es_panico=es_panico)

def armador_evento_carta(carta: CardSchema, objetivo: int):
    return EventoCartaJugada(carta=EventoCartaJugar(id=carta.get_id(), 
                                                    name=carta.get_name(), 
                                                    effectDescription=carta.get_effect(),
                                                    type=carta.get_type()), 
                             objetivo=objetivo)

def armador_evento_chat(nombre: str, nuevo_mensaje: str):
    return EventoChat(emisor=nombre, mensaje=nuevo_mensaje)


def armador_evento_lobby_jugadores(lista_jugadores: List[Jugador]):
    lobby = EventoLobbyJugadores()
    for each in lista_jugadores:
        lobby.jugadores.append(EventoLobbyJugador(name=each.get_nombre()))
    return lobby

def armador_evento_lobby_iniciada(iniciada: bool):
    return EventoLobbyIniciada(partida_iniciada=iniciada)

def armador_evento_mostrar_cartas(id: int, name: str, type: str,
                                  effectDescription: str):
    return EventoMostrarCartas(
        id=id,
        name=name,
        type=type,
        effectDescription=effectDescription
    )

def armador_evento_mostrar_mano(id_jugador: int, 
                                cartas: List[EventoMostrarCartas]):
    return EventoMostrarMano(
        id_jugador=id_jugador,
        cartas=cartas,
    )

def armador_evento_log(jugador: Jugador = None, carta: CardSchema = None,
                         context: str="", message="",
                         objetivo: Jugador = None) -> EventoLog:
    # El objetivo para el caso de la defensa se corresponde con el 
    # jugador que inicio el ataque
    nombre_jugador: str = jugador.get_nombre() if jugador else ""
    nombre_objetivo: str = objetivo.get_nombre() if objetivo else ""
    nombre_carta: str = carta.get_name() if carta else ""
    
    logMessage : str = ""  

    match context:
        case "comienzo_partida": 
            logMessage = "Comenzo la partida."
        case "comienzo_turno":
            logMessage = f"Comenzo el turno de {nombre_jugador}."
        case "jugar":
            logMessage = f"{nombre_jugador} jugo {nombre_carta}."
        case "jugar_con_objetivo":
            logMessage = f"{nombre_jugador} jugo {nombre_carta} sobre {nombre_objetivo}."
        case "descartar":
            logMessage =  f"{nombre_jugador} descarto."
        case "defender":
            logMessage = f"{nombre_jugador} se defendio con {nombre_carta}."
        case "intercambiar":
            logMessage = f"{nombre_jugador} intercambio con {nombre_objetivo}."
        case "defender_intercambio":
            logMessage = f"{nombre_jugador} se defendio de intercambiar con {nombre_objetivo} usando {nombre_carta}."
        case "cambiar_lugar":
            logMessage = f"{nombre_jugador} cambio de lugar con {nombre_objetivo}."
        case "morir_incinerado":
            logMessage = f"{nombre_jugador} murio incinerado."
        case "morir_superinfeccion":
            logMessage = f"{nombre_jugador} murio por superinfeccion."
        case "cambiar_sentido":
            logMessage = "Se cambio el sentido de la ronda."
        case "unirse":
            logMessage = f"{nombre_jugador} se unió a la partida"
        case "salirse":
            logMessage = f"{nombre_jugador} se fue de la partida"
        case "bloqueo":
            logMessage = f"{jugador.get_nombre()} no puede intercambiar con {objetivo.get_nombre()} porque hay un bloqueo"
        case "":
            logMessage = message

    return EventoLog(mensaje=logMessage)

def verificar_superinfeccion(jugador: Jugador, jugador_objetivo: Jugador) -> bool:
    # Chequeamos por superinfeccion
    superinfeccion: bool = True
    for carta in jugador.get_mano():
        if carta.get_name() != "Infectado": 
            superinfeccion = False
            continue
    superinfeccion = superinfeccion and not (jugador.get_rol() == "Infectado" 
                                        and jugador_objetivo.get_rol() == "La Cosa")
    return superinfeccion

def aplicar_superinfeccion(partida: Partida, jugador: Jugador):
        # Se eliminar el jugador y se envia el evento log y ronda
        id_partida = partida.get_id()
        mazo = partida.get_mazo()
        mano = jugador.remover_mano()
        for each in mano:
            mazo.discard_card(each)
        partida.post_event(id_jugador=jugador.get_id(), 
                    event=EventoMuerte(contexto="Superinfeccion"), 
                    event_name="Muerte")
        partida.eliminar_jugador(jugador)
        armar_broadcast(_partida_=partida,
                        msg=armador_evento_log(jugador=jugador, context="morir_superinfeccion"),
                        event_name="Log")
        armar_broadcast(_partida_=partida, msg=armador_ronda(id_partida), event_name="Ronda")

def superinfeccion_ronda(partida: Partida):
    for each in partida.get_jugadores():
        each_obj = partida.proximo_en_ronda(each.get_posicion())
        if verificar_superinfeccion(each, each_obj):
            aplicar_superinfeccion(partida=partida, jugador=each)
            