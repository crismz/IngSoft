from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pony.orm import db_session

import sys
sys.path.append("../../..")

from partidas.schema import Partida, DefIntercambioInput
from partidas.events import EventoRespuestaIntercambio, EventoMano, EventoPedidoIntercambio, \
                            EventoResultadoDefensa, EventoObjetivoIntercambio
from partidas.utils import lista_partidas, armador_evento_mano, armar_broadcast, armador_evento_log
from partidas.jugadores.schema import Jugador, IntercambioIn
from partidas.jugadores.utils import obtener_objetivo_intercambio, verificar_intercambio
from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.utils import populate_with_cards
from partidas.mazo.cartas.db import db
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
                   Jugador(id=3, nombre="Neow", posicion=2, rol="Infectado", mano=[])]

partida_ejemplo = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=4,
                              max_jugadores=4, min_jugadores=4, posiciones=[],
                              turno=1, mazo=Mazo(), jugadores=lista_jugadores, 
                              iniciada=True, sentido=True, conexiones={})


partida_ejemplo.get_mazo().create_deck(0, 4)

lista_partidas.append(partida=partida_ejemplo)

# Crear el diccionario de croupiers
diccionario_croupier = DiccionarioCroupier()
# Añadir el diccionario de croupiers de la partida
diccionario_croupier.append(partida_ejemplo)


@app.patch("/partidas/{id_partida}/jugadores/{id_jugador}/intercambiar", status_code=200)
async def intercambiar_carta(id_partida: int, id_jugador: int, trade_data_ini: IntercambioIn):
    # Primero obtengo la partida y el jugador que invocó el endpoint
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    partida = lista_partidas.get_partida_by_index(index)
    jugador = partida.buscar_jugador(id_jugador)
    
    # Obtengo el jugador con quien se quiere intercambiar
    id_objetivo = obtener_objetivo_intercambio(partida, jugador)
    jugador_objetivo = partida.buscar_jugador(id_objetivo)
    jugador.set_id_objetivo_intercambio(-1)

    if not verificar_intercambio(jugador, jugador_objetivo.get_rol(), trade_data_ini.id_carta):
        raise HTTPException(status_code=400, detail="Invalid card choice, please select a different card to trade.")
    
    # - Reservar/apartar el id de la carta que se quiere intercambiar
    jugador.set_id_carta_intercambio(trade_data_ini.id_carta)
    #   > Como el que inicia el intercambio es siempre el jugador del turno,
    #   no hace falta guardar su id

    # - Armar y enviar evento de mano bloqueada, para que no juegue ni descarte nada mientras tanto
    evento_mano_bloqueda : EventoMano = armador_evento_mano(jugador=jugador,
                                                            instancia="Esperar", 
                                                            context="Esperando")
    partida.post_event(id_jugador=id_jugador, 
                         event=evento_mano_bloqueda, 
                         event_name="Mano")

    # - Armar y enviar evento de mano para intercambio dirigido al objetivo del intercambio
    # El pedido es una formalidad más que otra cosa 
    evento_pedido_intercambio = EventoPedidoIntercambio(id_jugador=id_jugador)

    partida.post_event(id_jugador=id_objetivo, 
                         event=evento_pedido_intercambio, 
                         event_name="Pedido_intercambio")

    evento_mano_intercambiables : EventoMano = armador_evento_mano(jugador=jugador_objetivo,
                                                                   instancia="Intercambiar_Defender",
                                                                   context="Intercambiables_defensa")
    partida.post_event(id_jugador=id_objetivo, 
                         event=evento_mano_intercambiables, 
                         event_name="Mano")

    # Si pasó todos los chequeos, consumó un intercambio
    jugador.restar_accion("intercambios")
    return


@app.put("/partidas/{id_partida}/jugadores/{id_jugador}/defensa_intercambio", status_code=200)
async def jugar_defensa_intercambio(id_partida: int, id_jugador: int, input_data: DefIntercambioInput):
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"Match ID ({id_partida}) Not Found")
    
    current_partida = lista_partidas.get_partida_by_index(index)

    if not current_partida.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Not Started Yet")

    if not current_partida.existe_jugador(id_jugador):    
        raise HTTPException(status_code=404, detail=f"Player ID ({id_jugador}) Not Found")
    
    id_carta = input_data.id_carta
    croupier = diccionario_croupier.get_croupier(id_partida)
    jugador = current_partida.buscar_jugador(id_jugador)
    
    if not jugador.tiene_en_mano(id_carta):
        raise HTTPException(status_code=404, detail=f"Card ID ({id_carta}) Not Found")
    
    jugador_objetivo = current_partida.buscar_jugador_por_posicion(current_partida.get_turno())

    carta_jugada = jugador.obtener_carta(id_carta=id_carta)
    if not (carta_jugada.get_name() in ["Aterrador", "¡No, gracias!", "¡Fallaste!"] and
        croupier.verificar_efecto(id_carta, id_jugador, jugador_objetivo.get_id())):
        raise HTTPException(status_code=400, detail=f"Card ID ({id_carta}) Cannot Be Played That Way!")

    croupier.stack_card(id_carta, id_jugador, jugador_objetivo.get_id())

    evento_jugador = armador_evento_mano(jugador, "Esperar", "Esperando")
    current_partida.post_event(id_jugador, evento_jugador, "Mano")    

    croupier.execute_stack()

    armar_broadcast(_partida_=current_partida, 
                    msg=armador_evento_log(jugador=jugador, objetivo=jugador_objetivo, 
                                           carta=carta_jugada, context="defender_intercambio"), 
                    event_name="Log")

    jugador.set_inmunidad(False)

    evento_resultado_defensa = EventoResultadoDefensa(nombre_jugador=jugador.get_nombre(),
                                                      id_jugador=id_jugador,
                                                      esta_vivo=True)
    armar_broadcast(current_partida, evento_resultado_defensa, "Resultado_defensa")
    # Si la defensa fue con '¡Fallaste!', el turno aún no termina
    if carta_jugada.get_name() != "¡Fallaste!":    
        evento_intercambio_resuelto = EventoRespuestaIntercambio(id_jugador_turno=jugador_objetivo.get_id(),
                                                                 id_jugador_objetivo=jugador.get_id())
        if jugador_objetivo.quedan_acciones("intercambios"):
            # Reinicio el proceso de intercambio
            evento_objetivo_intercambio = EventoObjetivoIntercambio(id_jugador=obtener_objetivo_intercambio(current_partida, jugador_objetivo))
            current_partida.post_event(jugador_objetivo.get_id(), evento_objetivo_intercambio, "Objetivo_intercambio")
            mano_objetivo = armador_evento_mano(jugador=jugador_objetivo,
                                                instancia="Intercambiar",
                                                context="Intercambiables")
        else:
            mano_objetivo = armador_evento_mano(jugador=jugador_objetivo, 
                                                instancia="Esperar", 
                                                context="Fin_Turno")

        current_partida.post_event(id_jugador=jugador_objetivo.get_id(), 
                                   event=mano_objetivo,
                                   event_name="Mano") 
        
        armar_broadcast(_partida_=current_partida, msg=evento_intercambio_resuelto, event_name="Respuesta_intercambio")
    return