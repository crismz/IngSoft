from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pony.orm import db_session
from sse_starlette import EventSourceResponse
from pydantic import BaseModel

import sys
sys.path.append("../../..")

from partidas.schema import Partida, ListaPartida, Posicion
from partidas.events import (EventoRespuestaIntercambio, EventoMano, EventoPedidoIntercambio,
                             EventoObjetivoIntercambio)

from partidas.utils import (lista_partidas, armador_evento_mano, armar_broadcast, armador_ronda,
                            armador_evento_carta, armador_evento_log, armador_evento_mostrar_cartas,
                            armador_evento_mostrar_mano, armador_evento_mazo, verificar_superinfeccion,
                            aplicar_superinfeccion, armador_evento_turno, superinfeccion_ronda)

from partidas.jugadores.schema import Jugador, RespuestaIntercambioIn, IntercambioIn, DatosJugarCarta
from partidas.jugadores.utils import (event_sender, intercambiar_cartas, obtener_objetivo_intercambio, 
                                      verificar_intercambio, intercambiar_con_mazo)
from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.utils import populate_with_cards
from partidas.mazo.cartas.db import db
from partidas.mazo.cartas.schema import CardSchema
from partidas.croupier.schema import DiccionarioCroupier, Croupier


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
                   Jugador(id=1, nombre="Silent", posicion=1, rol="Humano", mano=[], cuarentena=True),
                   Jugador(id=2, nombre="Defect", posicion=2, rol="Infectado", mano=[]),
                   Jugador(id=3, nombre="Neow", posicion=2, rol="Infectado", mano=[])]

lista_posiciones = []
for each in range(0,4):
    lista_posiciones.append(Posicion())

mazo = Mazo()
mazo.create_deck(0, 4)

partida_ejemplo = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=4,
                              max_jugadores=4, min_jugadores=4, posiciones=lista_posiciones,
                              turno=0, mazo=mazo, jugadores=lista_jugadores, 
                              iniciada=True, sentido=True, conexiones={})

lista_jugadores[0].agregar_carta_mano(CardSchema(id=101, 
                                                 num_players=4, 
                                                 type="Panico", 
                                                 name="¿No Podemos Ser Amigos?", 
                                                 effect="Intercambia 1 carta con cualquier jugador de tu eleccion que no este en Cuarentena.", 
                                                 target="any"))
lista_jugadores[0].agregar_carta_mano(CardSchema(id=100, 
                                                 num_players=1, 
                                                 type="Any", 
                                                 name="Ironclads_card", 
                                                 effect="Bore you to death", 
                                                 target="self"))

lista_jugadores[0].agregar_carta_mano(CardSchema(id=106, 
                                                 num_players=1, 
                                                 type="Any", 
                                                 name="Ironclads_card", 
                                                 effect="Bore you to death", 
                                                 target="self"))

lista_jugadores[1].agregar_carta_mano(CardSchema(id=103, 
                                                 num_players=1, 
                                                 type="Any", 
                                                 name="Silents_card", 
                                                 effect="Bore you to death", 
                                                 target="self"))

lista_jugadores[2].agregar_carta_mano(CardSchema(id=104, 
                                                 num_players=1, 
                                                 type="Any", 
                                                 name="Defects_card", 
                                                 effect="Bore you to death", 
                                                 target="self"))

lista_jugadores[3].agregar_carta_mano(CardSchema(id=105, 
                                                 num_players=1, 
                                                 type="Any", 
                                                 name="Neows_card", 
                                                 effect="Bore you to death", 
                                                 target="self"))

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
        # Agregamos el evento de Ronda, Turno, Mazo y Mano
        # No se hace broadcasting, porque se envia a cada jugador que se conecta
        # por lo tanto lo terminan recibiendo todos
        current_partida.post_event(id_jugador=id_jugador, 
                                    event=armador_ronda(id_partida), 
                                    event_name="Ronda")
        current_partida.post_event(id_jugador=id_jugador, 
                                    event=armador_evento_turno(id_partida),
                                    event_name="Turno")
        current_partida.post_event(id_jugador=id_jugador,
                                    event=armador_evento_mazo(current_partida),
                                    event_name="Mazo")
        
        jugador = current_partida.buscar_jugador(id_jugador)

        current_partida.post_event(id_jugador=id_jugador,
                                    event=armador_evento_mano(jugador=jugador,
                                                            instancia="Esperar", 
                                                            context="Esperando"),
                                    event_name="Mano")
        
        # Mandamos mensaje log de partida iniciada
        current_partida.post_event(id_jugador=id_jugador, 
                                     event=armador_evento_log(context="comienzo_partida"), 
                                     event_name="Log")

        # Mandamos mensaje log de primer turno
        jugador_turno = current_partida.buscar_jugador_por_posicion(current_partida.get_turno())
        current_partida.post_event(id_jugador=id_jugador,
                                    event=armador_evento_log(jugador=jugador_turno,
                                                            context="comienzo_turno"), 
                                    event_name="Log")

        return EventSourceResponse(event_sender(current_partida, id_jugador))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

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
    id_objetivo = jugada.id_objetivo if jugada.id_objetivo < 100 else jugada.id_objetivo - 100
    if not current_partida.existe_jugador(id_objetivo):    
        raise HTTPException(status_code=404, detail=f"Player ID ({id_objetivo}) Not Found")
    
    # Chequeamos que la carta esté en la mano del jugador
    jugador = current_partida.buscar_jugador(id_jugador)
    id_carta = jugada.id_carta
    if not jugador.tiene_en_mano(id_carta):    
        raise HTTPException(status_code=404, detail=f"Card ID ({id_carta}) Not Found")
    
    # Conseguimos el Croupier de la partida
    croupier = diccionario_croupier.get_croupier(id_partida)

    # Verificamos que la carta se está jugando apropiadamente
    if not croupier.verificar_efecto(id_carta, id_jugador, jugada.id_objetivo):
        raise HTTPException(status_code=400, detail=f"Card ID ({id_carta}) Cannot Be Played That Way!")
    
    # Armamos el evento para broadcastear la carta jugada ANTES de ponerla en el stack de ejecución
    # pues una vez hecho esto, la carta se va a la pila de descarte
    carta = jugador.obtener_carta(id_carta)
    evento_carta = armador_evento_carta(carta=carta, objetivo=id_objetivo)

    # La carta se puede jugar apropiadamente, por lo que apilamos la carta en
    # el stack de efectos de la partida usando el croupier,
    # lo cual quita al jugador la carta de su mano
    croupier.stack_card(id_carta, id_jugador, jugada.id_objetivo)
    
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

    # Si la carta es vuelta y vuelta, antes de ejecutar chequeamos
    # si hay una superinfeccion en algun jugador y aplicamos de ser necesario
    if id_carta in range(99,101):
        superinfeccion_ronda(partida=current_partida)

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
            # Chequeamos si hay una superinfeccion
            jugador_objetivo = current_partida.buscar_jugador(
                                    obtener_objetivo_intercambio(current_partida, jugador))
            superinfeccion: bool = verificar_superinfeccion(jugador, jugador_objetivo)
            if superinfeccion:
                aplicar_superinfeccion(partida=current_partida, jugador=jugador)
                # Mandamos turno de siguiente jugador
                current_partida.set_turno(current_partida.proximo_turno())
                evento_turno = armador_evento_turno(id_partida)
                armar_broadcast(_partida_=current_partida,
                        msg=armador_evento_log(
                            jugador=current_partida.buscar_jugador_por_posicion(
                                                    current_partida.get_turno()), 
                            context="comienzo_turno"), 
                        event_name="Log")
                armar_broadcast(_partida_=current_partida, msg=evento_turno, event_name="Turno")
            else:
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
        

        else:
            # No mandamos el objetivo del intercambio porque el jugador
            # tiene que hacer algo antes, como descartar y/o robar más
            # cartas
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
    
    # Chequeo que el jugador_objetivo no cumpla las condiciones de superinfeccion
    # En caso de que este superinfectado se cancela el intercambio y se manda evento de fin de turno
    superinfeccion: bool = verificar_superinfeccion(jugador_objetivo, jugador)
    if superinfeccion:
        aplicar_superinfeccion(partida=partida, jugador=jugador_objetivo)
        evento_mano : EventoMano = armador_evento_mano(jugador=jugador,
                                                        instancia="Esperar", 
                                                        context="Fin_Turno")
        partida.post_event(id_jugador=jugador.get_id(), 
                        event=evento_mano, 
                        event_name="Mano")
        # Se consumiria un intercambio en este caso? (consultar a tomi)
    else:
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
    carta_ofrecida = jugador_ofrecedor.obtener_carta(id_carta_ofrecida).model_copy()
    carta_resolvente = jugador_resolvente.obtener_carta(trade_data_res.id_carta).model_copy()

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
        evento_mano_ofrecedor : EventoMano = armador_evento_mano(jugador=jugador_ofrecedor,
                                                                instancia="Intercambiar",
                                                                context="Intercambiables")
    else:
        evento_mano_ofrecedor : EventoMano = armador_evento_mano(jugador=jugador_ofrecedor,
                                                                instancia="Esperar", 
                                                                context="Fin_Turno")

    evento_mano_bloqueda : EventoMano = armador_evento_mano(jugador=jugador_resolvente,
                                                            instancia="Esperar", 
                                                            context="Esperando")
    
    # Los eventos de mano hacen lo mismo pero significan cosas distintas:
    # > "Mano_Fin_Turno" indica que tiene que terminar el turno
    # > "Mano_Esperando" indica que simplemente tiene que esperar 
    #    hasta que le llegue un próximo evento para hacer algo (intercambio, inicio turno, etc)
    partida.post_event(id_jugador=jugador_ofrecedor.get_id(), 
                         event=evento_mano_ofrecedor, 
                         event_name="Mano")

    partida.post_event(id_jugador=jugador_resolvente.get_id(), 
                         event=evento_mano_bloqueda, 
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

    if jugador_ofrecedor.esta_en_cuarentena():
        
        cards = [armador_evento_mostrar_cartas(carta_ofrecida.get_id(), carta_ofrecida.get_name(), 
                                 carta_ofrecida.get_type(), carta_ofrecida.get_effect())]
        partida.broadcast(
            msg=armador_evento_mostrar_mano(jugador_ofrecedor.get_id(), cards),
            event_name="Cartas_mostrables"
        )
    if jugador_resolvente.esta_en_cuarentena():
        cards = [armador_evento_mostrar_cartas(carta_resolvente.get_id(), carta_resolvente.get_name(), 
                                 carta_resolvente.get_type(), carta_resolvente.get_effect())]
        partida.broadcast(
            msg=armador_evento_mostrar_mano(jugador_resolvente.get_id(), cards),
            event_name="Cartas_mostrables"
        )

    return