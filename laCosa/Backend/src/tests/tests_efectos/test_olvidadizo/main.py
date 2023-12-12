from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pony.orm import db_session
from sse_starlette import EventSourceResponse
from pydantic import BaseModel

import sys
sys.path.append("../../..")

from partidas.schema import Partida, Posicion
from partidas.utils import *
from partidas.jugadores.schema import Jugador, DatosJugarCarta
from partidas.jugadores.utils import event_sender, obtener_objetivo_intercambio
from partidas.events import EventoObjetivoIntercambio, EventoDescartarCarta
from partidas.mazo.schema import Mazo, RoboIn
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

lista_posiciones = []
for each in range(0,4):
    lista_posiciones.append(Posicion())

partida_ejemplo = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=4,
                              max_jugadores=4, min_jugadores=4, posiciones=lista_posiciones,
                              turno=0, mazo=Mazo(), jugadores=lista_jugadores, 
                              iniciada=True, sentido=True, conexiones={})


lista_jugadores[0].agregar_carta_mano(CardSchema(id=98, 
                                                 num_players=1, 
                                                 type="Panico", 
                                                 name=" Olvidadizo", 
                                                 effect="Descarta 3 cartas de tu mano y roba 3 nuevas cartas \"¡Alejate!\", descartando cualquier carta de \"Panico\"", 
                                                 target="self"))

lista_jugadores[0].agregar_carta_mano(CardSchema(id=400, 
                                                 num_players=1, 
                                                 type="Animal", 
                                                 name="Patito", 
                                                 effect=" Hace \"¡Quack!\" y se descarta", 
                                                 target="self"))

lista_jugadores[0].agregar_carta_mano(CardSchema(id=401, 
                                                 num_players=1, 
                                                 type="Animal", 
                                                 name="Patito", 
                                                 effect=" Hace \"¡Quack!\" y se descarta", 
                                                 target="self"))

lista_jugadores[0].agregar_carta_mano(CardSchema(id=402, 
                                                 num_players=1, 
                                                 type="Animal", 
                                                 name="Patito", 
                                                 effect=" Hace \"¡Quack!\" y se descarta", 
                                                 target="self"))

partida_ejemplo.get_mazo().create_deck(0, 4)

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
            #current_partida.post_event(id_jugador, SuccessfulConectionEvent)

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

    response = {
        "robos": jugador.acciones_restantes["robos"],
        "descartes": jugador.acciones_restantes["descartes"],
        "intercambios": jugador.acciones_restantes["intercambios"]
    }
    return response

@app.patch("/partidas/{id_partida}/jugadores/{id_jugador}/descartar", status_code=200)
async def descartar_carta(id_carta: int, id_partida: int, id_jugador: int):
    
    index : int = lista_partidas.get_index_by_id(id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) for match Not Found")
    
    _partida_ = lista_partidas.get_partida_by_index(index)
    
    if not _partida_.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Not Started Yet")

    # Chequeamos que el jugador esté en la partida
    if not _partida_.existe_jugador(id_jugador):    
        raise HTTPException(status_code=404, detail=f"Player ID ({id_jugador}) Not Found")
    
    # Chequeamos que la carta esté en la mano del jugador
    mano = _partida_.buscar_jugador(id_jugador).get_mano()
    exists : bool = id_carta in [card.get_id() for card in mano]    

    if not exists:
        raise HTTPException(status_code=404, detail=f"Card ID ({id_carta}) Not Found in Player({id_jugador})'s Hand")

    # Descartamos la carta
    #croupier : Croupier = diccionario_croupier.get_croupier(_partida_.get_id())
    #croupier.descartar(id_carta, id_jugador)

    jugador : Jugador = _partida_.buscar_jugador(id_jugador)
    mazo = _partida_.get_mazo()
    card = jugador.remover_carta_mano(id_carta)
    mazo.discard_card(card)
    
    if jugador.esta_en_cuarentena():
        mano = [
            armador_evento_mostrar_cartas(card.get_id(), card.get_name(), card.get_type(), card.get_effect())
        ]
        armar_broadcast(_partida_=_partida_,
            msg=armador_evento_mostrar_mano(jugador.get_id(), mano),
            event_name="Cartas_mostrables"
        )

    # Armamos el evento de descarte
    evento_descarte = EventoDescartarCarta(id_jugador=id_jugador)
    # Encolar evento de descarte
    armar_broadcast(_partida_=_partida_, msg=evento_descarte, event_name="Carta_descartada")
    
    # Enviar log de carta descartada
    armar_broadcast(_partida_=_partida_, 
                    msg=armador_evento_log(jugador=jugador, context="descartar"), 
                    event_name="Log")

    jugador.restar_accion("descartes")
    if jugador.quedan_acciones("descartes"):
        evento_respuesta = armador_evento_mano(jugador=jugador, 
                                                instancia="Descartar", 
                                                context="Descartables")
        _partida_.post_event(id_jugador=id_jugador, event=evento_respuesta, event_name="Mano")
    else:
        while jugador.quedan_acciones("robos"):
            carta_robada = mazo.take_card()
            while carta_robada.get_type() == "Panico":
                mazo.discard_card(carta_robada)
                carta_robada = mazo.take_card()
            jugador.agregar_carta_mano(carta_robada)
            jugador.restar_accion("robos")
            
        # Chequeamos si hay una superinfeccion
        jugador_objetivo = _partida_.buscar_jugador(
                                    obtener_objetivo_intercambio(_partida_, jugador))
        superinfeccion: bool = verificar_superinfeccion(jugador, jugador_objetivo)
        if superinfeccion:
            aplicar_superinfeccion(partida=_partida_, jugador=jugador)
            # Mandamos turno de siguiente jugador
            _partida_.set_turno(_partida_.proximo_turno())
            evento_turno = armador_evento_turno(id_partida)
            armar_broadcast(_partida_=_partida_,
                    msg=armador_evento_log(
                        jugador=_partida_.buscar_jugador_por_posicion(
                                                _partida_.get_turno()), 
                        context="comienzo_turno"), 
                    event_name="Log")
            armar_broadcast(_partida_=_partida_, msg=evento_turno, event_name="Turno")
        else:
            # Envia objetivo de intercambio al jugador
            objetivo_intercambio = obtener_objetivo_intercambio(_partida_, jugador)
            evento_objetivo = EventoObjetivoIntercambio(id_jugador=objetivo_intercambio)
            _partida_.post_event(id_jugador, evento_objetivo, "Objetivo_intercambio")        

            # Enviar evento de mano al jugador
            evento_respuesta = armador_evento_mano(jugador=jugador,
                                                instancia="Intercambiar",
                                                context="Intercambiables"
                                                )
            _partida_.post_event(id_jugador=id_jugador, event=evento_respuesta, event_name="Mano")
    
    response = {
        "robos": jugador.acciones_restantes["robos"],
        "descartes": jugador.acciones_restantes["descartes"],
        "intercambios": jugador.acciones_restantes["intercambios"]
    }
    return response