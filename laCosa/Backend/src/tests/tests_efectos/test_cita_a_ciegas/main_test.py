from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pony.orm import db_session
from sse_starlette import EventSourceResponse
from pydantic import BaseModel

import sys
sys.path.append("../../..")

from partidas.schema import Partida, Posicion
from partidas.events import EventoMano, EventoPedidoIntercambio, EventoObjetivoIntercambio
from partidas.utils import lista_partidas, armador_evento_mano, armar_broadcast, armador_evento_log, \
                            armador_evento_carta, armador_ronda, armador_evento_mazo
from partidas.jugadores.schema import Jugador, IntercambioIn, DatosJugarCarta
from partidas.jugadores.utils import event_sender, intercambiar_con_mazo, \
                                     obtener_objetivo_intercambio, verificar_intercambio
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
                   Jugador(id=2, nombre="Defect", posicion=2, rol="Humano", mano=[]),
                   Jugador(id=3, nombre="Neow", posicion=3, rol="Infectado", mano=[])]

partida_ejemplo = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=4,
                              max_jugadores=4, min_jugadores=4, 
                              posiciones=[Posicion(), Posicion(), Posicion(), Posicion()],
                              turno=0, mazo=Mazo(), jugadores=lista_jugadores, 
                              iniciada=True, sentido=True, conexiones={})


lista_jugadores[0].agregar_carta_mano(CardSchema(id=1000, 
                                                 num_players=1, 
                                                 type="Any", 
                                                 name="Ironclads_card", 
                                                 effect="Bore you to death", 
                                                 target="self"))

lista_jugadores[0].agregar_carta_mano(CardSchema(id=103,
                                                 num_players=4,
                                                 type="Panico",
                                                 name="Cita a ciegas",
                                                 effect="Intercambia una carta de tu mano con la primera \
                                                        carta del mazo, descartando cualquier carta de \"Panico\" \
                                                        robada. Tu turno termina",
                                                target="self"))


partida_ejemplo.get_mazo().create_deck(0, 4)
partida_ejemplo.get_mazo().place_on_top(CardSchema(id=777, num_players=4, type="Panico", name="Ejemplo Panico", 
                                                   effect="Molestar", target="self"))

#lista_partidas = ListaPartida(lista=[partida_ejemplo])
lista_partidas.append(partida=partida_ejemplo)

# Crear el diccionario de croupiers
diccionario_croupier = DiccionarioCroupier()
# Añadir el diccionario de croupiers de la partida
diccionario_croupier.append(partida_ejemplo)

class WelcomeMessage(BaseModel):
    msg: str = ""

@app.get("/")
async def hub():
    return {"message" : "Main Hub"}

@app.get("/partidas/{id_partida}/jugadores/sse/{id_jugador}")
async def suscribir_al_stream(id_partida: int, id_jugador: int):

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
    
    try:
        if not current_partida.is_connected(id_jugador):
            current_partida.connect(id_jugador)
            # Acá añadimos el evento de "Conexión exitosa" o similar
            eventoInicial = WelcomeMessage(msg="Hola wachin")
            current_partida.post_event(id_jugador, eventoInicial, "bienvenida")
        return EventSourceResponse(event_sender(current_partida, id_jugador))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/partidas/{id_partida}/jugadores/{id_jugador}/jugar", status_code=200)
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
            # Mandamos objetivo de intercambio
            objetivo_intercambio = obtener_objetivo_intercambio(current_partida, jugador)
            evento_objetivo = EventoObjetivoIntercambio(id_jugador=objetivo_intercambio)
            current_partida.post_event(id_jugador, evento_objetivo, "Objetivo_intercambio")
            # Actualizamos la mano del jugador de la carta para el intercambio
            evento_mano = armador_evento_mano(jugador=jugador,
                                            instancia="Intercambiar",
                                            context="Intercambiables",
                                            )
            current_partida.post_event(id_jugador, evento_mano, "Mano")
        
        # Una vez evaluado el atributo, podemos devolverlo a su valor normal
        jugador.set_listo_para_intercambio(True)
        # Se broadcastea la ronda
        evento_ronda = armador_ronda(id_partida)
        armar_broadcast(current_partida, evento_ronda, "Ronda")

    return

@app.patch("/partidas/{id_partida}/jugadores/{id_jugador}/intercambiar", status_code=200)
async def intercambiar_carta(id_partida: int, id_jugador: int, trade_data_ini: IntercambioIn):
    # Primero obtengo la partida y el jugador que invocó el endpoint
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    partida = lista_partidas.get_partida_by_index(index)
    jugador = partida.buscar_jugador(id_jugador)
    
    # Obtengo el jugador con quien se quiere intercambiar
    id_objetivo = obtener_objetivo_intercambio(partida, jugador)
    jugador.set_id_objetivo_intercambio(-1)

    ###### Caso 'Cita a Ciegas'
    if id_objetivo == -2:
        intercambiar_con_mazo(trade_data_ini.id_carta, jugador, partida)
        partida.broadcast(msg=armador_evento_mazo(partida), event_name="Mazo")
        # Al terminar, termina el turno
        evento_mano_ofrecedor : EventoMano = armador_evento_mano(jugador=jugador,
                                                                instancia="Esperar",
                                                                context="Fin_Turno")
        partida.post_event(id_jugador=id_jugador, 
                           event=evento_mano_ofrecedor, 
                           event_name="Mano")
        return
    ######
    
    jugador_objetivo = partida.buscar_jugador(id_objetivo)

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