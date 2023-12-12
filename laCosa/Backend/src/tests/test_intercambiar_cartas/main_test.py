from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pony.orm import db_session

import sys
sys.path.append("../..")

from partidas.schema import Partida, Posicion
from partidas.events import EventoPedidoIntercambio, EventoRespuestaIntercambio, EventoMano, \
                            EventoObjetivoIntercambio
from partidas.utils import lista_partidas, armador_evento_mano, armar_broadcast, armador_evento_log
from partidas.jugadores.schema import Jugador, RespuestaIntercambioIn, IntercambioIn
from partidas.jugadores.utils import intercambiar_cartas, obtener_objetivo_intercambio, verificar_intercambio
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.utils import populate_with_cards
from partidas.mazo.cartas.db import db
from partidas.mazo.schema import Mazo
from partidas.croupier.utils import DiccionarioCroupier


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
                   Jugador(id=2, nombre="Defect", posicion=2, rol="Humano", mano=[]),
                   Jugador(id=3, nombre="Neow", posicion=3, rol="Infectado", mano=[])]

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


@app.patch("/partidas/{id_partida}/jugadores/{id_jugador}/resolver_intercambio", status_code=200)
async def resolver_intercambio(id_partida: int, id_jugador: int, trade_data_res: RespuestaIntercambioIn):

    index = lista_partidas.get_index_by_id(id_param=id_partida)
    partida = lista_partidas.get_partida_by_index(index)
    jugador_resolvente = partida.buscar_jugador(id_jugador)
    # - Buscar la carta que le quieren dar a este jugador
    #   > El que inicia el intercambio es siempre el jugador del turno
    jugador_ofrecedor: Jugador = partida.buscar_jugador_por_posicion(partida.get_turno())

    if not verificar_intercambio(jugador_resolvente, jugador_ofrecedor.get_rol(), trade_data_res.id_carta):
        raise HTTPException(status_code=400, detail="Invalid card choice, please select a different card to trade.")
    
    id_carta_ofrecida : int = jugador_ofrecedor.get_id_carta_intercambio()

    # - Intercambiar las cartas
    #   > Función en <utils>, no confundir con el endpoint
    intercambiar_cartas([id_carta_ofrecida, trade_data_res.id_carta],
                        [jugador_ofrecedor, jugador_resolvente])

    jugador_ofrecedor.set_inmunidad(False)
    jugador_resolvente.set_inmunidad(False)

    # Reseteo el id de la carta a intercambiar
    jugador_ofrecedor.set_id_carta_intercambio(-1)
    
    # - Armar y enviar eventos de las nuevas manos
    #  Si al jugador ofrecedor le quedan intercambios pendientes, volvemos a mandar
    # la mano que le permita realizarlos
    if jugador_ofrecedor.quedan_acciones("intercambios"):
        # Reinicio el proceso de intercambio
        evento_objetivo = EventoObjetivoIntercambio(id_jugador=obtener_objetivo_intercambio(partida, jugador_ofrecedor))
        partida.post_event(jugador_ofrecedor.get_id(), evento_objetivo, "Objetivo_intercambio")
        evento_mano_bloqueda1 : EventoMano = armador_evento_mano(jugador=jugador_ofrecedor,
                                                                instancia="Intercambiar",
                                                                context="Intercambiables")
    else:
        evento_mano_bloqueda1 : EventoMano = armador_evento_mano(jugador=jugador_ofrecedor,
                                                                instancia="Esperar", 
                                                                context="Fin_Turno")

    evento_mano_bloqueda2 : EventoMano = armador_evento_mano(jugador=jugador_resolvente,
                                                            instancia="Esperar", 
                                                            context="Esperando")
    
    # Los eventos de mano hacen lo mismo pero significan cosas distintas:
    # > "Mano_Fin_Turno" indica que tiene que terminar el turno
    # > "Mano_Esperando" indica que simplemente tiene que esperar 
    #    hasta que le llegue un próximo evento para hacer algo (intercambio, inicio turno, etc)
    partida.post_event(id_jugador=jugador_ofrecedor.get_id(), 
                         event=evento_mano_bloqueda1, 
                         event_name="Mano")

    partida.post_event(id_jugador=jugador_resolvente.get_id(), 
                         event=evento_mano_bloqueda2, 
                         event_name="Mano")

    # Mensaje log de intercambio
    armar_broadcast(_partida_=partida,
                    msg=armador_evento_log(jugador=jugador_ofrecedor, 
                                           objetivo=jugador_resolvente, 
                                           context="intercambiar"), 
                    event_name="Log")

    # - Armar y broadcastear el mensaje de que se produjo un intercambio
    evento_intercambio_resuelto = EventoRespuestaIntercambio(id_jugador_turno=jugador_ofrecedor.get_id(),
                                                             id_jugador_objetivo=jugador_resolvente.get_id())
    
    armar_broadcast(_partida_=partida, msg=evento_intercambio_resuelto, event_name="Respuesta_intercambio")

    return