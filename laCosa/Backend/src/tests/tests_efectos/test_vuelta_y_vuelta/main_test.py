from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pony.orm import db_session
from typing import List

import sys
sys.path.append("../../..")

from partidas.schema import Partida, Posicion
from partidas.events import EventoMano, EventoObjetivoIntercambio
from partidas.utils import lista_partidas, armador_evento_mano, armar_broadcast, \
                           armador_evento_carta, armador_evento_log, armador_ronda
from partidas.jugadores.schema import Jugador, DatosJugarCarta, IdCartaIn
from partidas.jugadores.utils import obtener_objetivo_intercambio, verificar_intercambio
from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.utils import populate_with_cards
from partidas.mazo.cartas.db import db
from partidas.mazo.cartas.schema import CardSchema
from partidas.croupier.schema import DiccionarioCroupier


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db.bind('sqlite',filename="db.sqlite", create_db=True)
db.generate_mapping(create_tables=True)
with db_session:
    if Card.select().count() == 0:
        populate_with_cards()

lista_jugadores = [Jugador(id=0, nombre="Ironclad", posicion=0, rol="La Cosa", mano=[]), 
                   Jugador(id=1, nombre="Silent", posicion=1, rol="Humano", mano=[]),
                   Jugador(id=2, nombre="Defect", posicion=2, rol="Infectado", mano=[]),
                   Jugador(id=3, nombre="Neow", posicion=3, rol="Humano", mano=[])]

partida_ejemplo = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=4,
                              max_jugadores=4, min_jugadores=4, 
                              posiciones=[Posicion(), Posicion(), Posicion(), Posicion()],
                              turno=0, mazo=Mazo(), jugadores=lista_jugadores, 
                              iniciada=True, sentido=True, conexiones={})


partida_ejemplo.get_mazo().create_deck(0, 4)

#lista_partidas = ListaPartida(lista=[partida_ejemplo])
lista_partidas.append(partida=partida_ejemplo)

# Crear el diccionario de croupiers
diccionario_croupier = DiccionarioCroupier()
# Añadir el diccionario de croupiers de la partida
diccionario_croupier.append(partida_ejemplo)

@app.put("/partidas/{id_partida}/jugadores/{id_jugador}/jugar")
async def jugar_carta(id_partida: int, id_jugador: int, jugada: DatosJugarCarta):

    # Obtengo la partida deseada mediante el id con {id_partida}
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"Match ID ({id_partida}) Not Found")
    
    # Como la partida existe, la obtenemos
    current_partida = lista_partidas.get_partida_by_index(index)   

    # Chequeamos que la partida esté iniciada
    if not current_partida.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Not Started Yet")

    # Chequeamos que el jugador esté en la partida
    if not current_partida.existe_jugador(id_jugador):    
        raise HTTPException(status_code=404, detail=f"Player ID ({id_jugador}) Not Found")
    
    # Obtenemos el jugador objetivo
    id_objetivo = jugada.id_objetivo 
    if not current_partida.existe_jugador(id_objetivo):    
        raise HTTPException(status_code=404, detail=f"Player ID ({id_jugador}) Not Found")
    
    # Chequeamos que la carta esté en la mano del jugador
    jugador = current_partida.buscar_jugador(id_jugador)
    id_carta = jugada.id_carta
    if not jugador.tiene_en_mano(id_carta):    
        raise HTTPException(status_code=404, detail=f"Card ID ({id_carta}) Not Found")
    
    # Conseguimos el Croupier de la partida
    croupier = diccionario_croupier.get_croupier(id_partida)

    # Verificamos que la carta se está jugando apropiadamente
    if not croupier.verificar_efecto(id_carta, id_jugador, id_objetivo):
        raise HTTPException(status_code=400, detail=f"Card ID ({id_carta}) Cannot Be Played That Way!")
    
    # Armamos el evento para broadcastear la carta jugada ANTES de ponerla en el stack de ejecución
    # pues una vez hecho esto, la carta se va a la pila de descarte
    carta = jugador.obtener_carta(id_carta)
    evento_carta = armador_evento_carta(carta=carta, objetivo=id_objetivo)

    # La carta se puede jugar apropiadamente, por lo que apilamos la carta en
    # el stack de efectos de la partida usando el croupier,
    # lo cual quita al jugador la carta de su mano
    croupier.stack_card(id_carta, id_jugador, id_objetivo)
    objetivo = current_partida.buscar_jugador(id_objetivo)

    # Se broadcastea un evento carta_jugada
    armar_broadcast(current_partida, evento_carta, "Carta_jugada")

    # Armamos evento Mano con Esperar al jugador de la carta
    evento_jugador = armador_evento_mano(jugador, "Esperar", "Esperando")
    current_partida.post_event(id_jugador, evento_jugador, "Mano")

    # Enviar evento log de carta jugada
    if carta.get_target() == "self":
        armar_broadcast(_partida_=current_partida, 
                msg=armador_evento_log(jugador=jugador, carta=carta, context="jugar"), 
                event_name="Log")
    else:
        armar_broadcast(_partida_=current_partida, 
                msg=armador_evento_log(jugador=jugador, objetivo=objetivo, 
                                    carta=carta, context="jugar_con_objetivo"), 
                event_name="Log")


    if croupier.carta_es_defendible(id_carta):
        # La carta en cuestión tiene una defensa en el mazo
 
        # Armamos evento Mano con Jugar_defensa al objetivo de la carta
        evento_objetivo = armador_evento_mano(objetivo, "Defender", "Defensas")
        # Enviamos los eventos
        current_partida.post_event(id_objetivo, evento_objetivo, "Mano")
    else:
        # No hay defensa posible para esta carta
        # Ejecutamos el stack de efectos de la partida
        croupier.execute_stack()
        # Se broadcastea Resultado_defensa
        objetivo_esta_vivo = current_partida.existe_jugador(id_objetivo)

        # Si el objetivo murió, se termina su conexión SSE
        if not objetivo_esta_vivo:
            # Asumimos que evento_resultado_defensa da suficiente info
            # al front para cerrar la escucha de eventos
            current_partida.terminate_connection(id_objetivo)

        if jugador.get_listo_para_intercambio():
            # Mandamos objetivo de intercambio porque el jugador está listo
            objetivo_intercambio = obtener_objetivo_intercambio(current_partida, jugador)
            evento_objetivo = EventoObjetivoIntercambio(id_jugador=objetivo_intercambio)
            current_partida.post_event(id_jugador, evento_objetivo, "Objetivo_intercambio")
            # Actualizamos la mano del jugador de la carta para el intercambio
            evento_mano = armador_evento_mano(jugador=jugador,
                                            instancia="Intercambiar",
                                            context="Intercambiables",
                                            )
            current_partida.post_event(id_jugador, evento_mano, "Mano")
        else:
            # No mandamos el objetivo del intercambio porque el jugador
            # tiene que hacer algo antes, como descartar y/o robar más
            # cartas
            jugador.set_listo_para_intercambio(True)

        # Se broadcastea la ronda
        evento_ronda = armador_ronda(id_partida)
        armar_broadcast(current_partida, evento_ronda, "Ronda")

    return

@app.patch("/partidas/{id_partida}/jugadores/{id_jugador}/vuelta_y_vuelta", status_code=200)
async def vuelta_y_vuelta(id_partida: int, id_jugador: int, VyV_info: IdCartaIn):
    index : int = lista_partidas.get_index_by_id(id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) for match Not Found")
    
    partida: Partida = lista_partidas.get_partida_by_index(index)
    jugador: Jugador = partida.buscar_jugador(id_jugador)
    id_jugador_siguiente: int = obtener_objetivo_intercambio(partida, jugador)

    if not verificar_intercambio(jugador, partida.buscar_jugador(id_jugador_siguiente).get_rol(), VyV_info.id_carta):
        raise HTTPException(status_code=400, detail="Invalid card choice, please select a different card to trade.")
    
    jugador.set_id_carta_intercambio(VyV_info.id_carta)
    mano_esperando: EventoMano = armador_evento_mano(jugador, "Esperar", "Esperando")
    partida.post_event(id_jugador, mano_esperando, "Mano")
    #  Como 'Vuelta y vuelta' sólo se puede jugar al principio del turno y es la única
    # carta que se juega, podemos asumir que el id_objetivo_intercambio de todos estará en -1
    partida.sumar_jugador_listo()
    if partida.todos_listos():
        lista_jugadores: List[Jugador] = partida.obtener_jugadores()
        # Ubico todas las cartas con sus nuevos dueños
        for each in lista_jugadores:
            id_carta_a_entregar: int = each.get_id_carta_intercambio()
            carta_a_entregar: CardSchema = each.remover_carta_mano(id_carta_a_entregar)

            id_jugador_siguiente: int = obtener_objetivo_intercambio(partida, each)
            jugador_siguiente: Jugador = partida.buscar_jugador(id_jugador_siguiente)

            jugador_siguiente.agregar_carta_mano(carta_a_entregar)
            if each.get_rol() == "La Cosa" and carta_a_entregar.get_type() == "Contagio":
                jugador_siguiente.set_rol("Infectado")
        
        # Mando todas las manos actualizadas
        id_jugador_turno: int = partida.buscar_jugador_por_posicion(partida.get_turno()).get_id()
        for each in lista_jugadores:
            if each.get_id() == id_jugador_turno:
                mano_actualizada: EventoMano = armador_evento_mano(each, "Esperar", "Fin_Turno")
            else:
                mano_actualizada: EventoMano = armador_evento_mano(each, "Esperar", "Esperando")
            
            partida.post_event(each.get_id(), mano_actualizada, "Mano")

        # Por último, reseteo el valor del campo para próximas jugadas sde 'Vuelta y vuelta'
        partida.reiniciar_listos()
    return