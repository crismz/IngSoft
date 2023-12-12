import sys
sys.path.append("../..")
from fastapi import FastAPI, HTTPException
from sse_starlette import EventSourceResponse

from partidas.schema import Partida, ListaPartida, Posicion
from partidas.utils import (
    lista_partidas, verificar_datos_creacion, armar_broadcast, armador_evento_mano,
    get_vecinos, armador_ronda, repartir_cartas, armador_evento_turno, primer_turno,
    armador_evento_carta, armador_evento_chat, armador_evento_lobby_jugadores,
    armador_evento_lobby_iniciada, armador_evento_log, verificar_superinfeccion,
    aplicar_superinfeccion, superinfeccion_ronda, armador_evento_mazo
)
from partidas.events import (EventoResultadoDefensa, EventoFinalizoPartida, EventoObjetivoIntercambio,
                             EventoRespuestaIntercambio, EventoMuerte)

from partidas.jugadores.schema import Jugador, DatosJugarCarta, DatosJugarDefensa
from partidas.jugadores.utils import event_sender, obtener_objetivo_intercambio
from utils import WelcomeMessage
from partidas.croupier.schema import DiccionarioCroupier, Croupier
from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.schema import CardSchema

from pony.orm import db_session
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.db import db
from partidas.mazo.cartas.utils import populate_with_cards

db.bind('sqlite',filename="db.sqlite", create_db=True)
db.generate_mapping(create_tables=True)
with db_session:
    if Card.select().count() == 0:
        populate_with_cards()

lista_jugadores = []

lista_jugadores.append(Jugador(id=0, nombre="C. Auguste Dupin", posicion=0, rol="Human"))
lista_jugadores.append(Jugador(id=1, nombre="Sherlock Holmes", posicion=1, rol="Human"))
lista_jugadores.append(Jugador(id=2, nombre="Long John Silver", posicion=2, rol="Human"))
lista_jugadores.append(Jugador(id=3, nombre="Kelsier", posicion=3, rol="Human"))

pocos_jugadores = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=0,
                          max_jugadores=6, min_jugadores=4, posiciones=[],
                          turno=0, mazo=None, jugadores=[], iniciada=True, conexiones={})

for each in range(len(lista_jugadores)):
    jugador = lista_jugadores[each]
    pocos_jugadores.agregar_jugador(jugador)
    pocos_jugadores.agregar_posicion(Posicion())

current_mazo = Mazo(id_partida=0)
current_mazo.create_deck(0, 4)
pocos_jugadores.set_mazo(current_mazo)
# Repartir las cartas que queremos que estén en las manos de los jugadores
for each in pocos_jugadores.obtener_jugadores():
    flamita = CardSchema(id=22+each.get_id(),
                        num_players=pocos_jugadores.get_num_jugadores(),
                        type="Accion",
                        name="Lanzallamas",
                        effect="Elimina de la partida a un jugador adyacente",
                        target="neighbour"
                        )
    blank = CardSchema(id=200+each.get_id(),
                        num_players=pocos_jugadores.get_num_jugadores(),
                        type="Blank",
                        name="Blank",
                        effect="Se descarta sin afectar la partida",
                        target="any")
    if each.get_id() <= 2:
        extintor = CardSchema(id=81+each.get_id(),
                            num_players=pocos_jugadores.get_num_jugadores(),
                            type="Defensa",
                            name="¡Nada de barbacoas!",
                            effect="Cancela una carta \"Lanzallamas\" que te tenga como objetivo. Roba"\
                            " 1 carta \"¡Alejate!\" en sustitucion de esta.",
                            target="self")
        each.agregar_carta_mano(extintor)
    each.agregar_carta_mano(flamita)
    each.agregar_carta_mano(blank)
    
lista_partidas.append(pocos_jugadores)
# Crear el diccionario de croupiers
diccionario_croupier = DiccionarioCroupier()
# Añadir el diccionario de croupiers de la partida
diccionario_croupier.append(pocos_jugadores)

app = FastAPI()

@app.get("/partidas/{id_partida}/jugadores/sse/{id_jugador}", status_code=200)
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
            # Chequeamos si hay una superinfeccion
            jugador_objetivo = current_partida.buscar_jugador(
                                    obtener_objetivo_intercambio(current_partida, jugador))
            superinfeccion: bool = verificar_superinfeccion(jugador, jugador_objetivo)
            if superinfeccion and not (jugador.get_rol() == "Infectado" 
                            and jugador_objetivo.get_rol() == "La Cosa"):
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

    return

@app.put("/partidas/{id_partida}/jugadores/{id_jugador}/defensa", status_code=200)
async def jugar_defensa(id_partida: int, id_jugador:int, jugada:DatosJugarDefensa):
    # Obtengo la partida deseada mediante el id
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
    
    # Chequeamos si el jugador se está defendiendo
    # Asumimos que el front enviará un id_carta == -1
    # si el jugador no tiene una carta para defenderse o
    # elige no defenderse
    id_carta = jugada.id_carta
    croupier = diccionario_croupier.get_croupier(id_partida)
    jugador = current_partida.buscar_jugador(id_jugador)

    nombre = jugador.get_nombre()
    identficador = jugador.get_id()
    rol = jugador.get_rol()
    posicion = jugador.get_posicion() 
    if id_carta == -1:
        # El jugador no se defiende, porque no tiene la carta necesaria o no quiere usarla

        # Actualizamos la mano del "defensor" vivo para que no realice mas acciones
        evento_jugador = armador_evento_mano(jugador, "Esperar", "Esperando")
        current_partida.post_event(id_jugador, evento_jugador, "Mano")

        # Se ejecuta la pila
        croupier.execute_stack()
    else:
        # El jugador se defiende

        # Chequeamos que la carta esté en la mano del jugador
        if not jugador.tiene_en_mano(id_carta):    
            raise HTTPException(status_code=404, detail=f"Card ID ({id_carta}) Not Found")
        
        # Verificamos que la carta se está jugando apropiadamente
        # Las cartas de defensa se juegan, en general, sobre uno mismo
        if not croupier.verificar_efecto(id_carta, id_jugador, id_jugador):
            raise HTTPException(status_code=400, detail=f"Card ID ({id_carta}) Cannot Be Played That Way!")
        
        # Mensaje log de que el jugador se defendio
        carta = jugador.obtener_carta(id_carta)

        # La carta se pone en el stack de ejecución
        croupier.stack_card(id_carta, id_jugador, id_jugador)

        # Actualizamos la mano del "defensor" vivo para que no realice mas acciones
        evento_jugador = armador_evento_mano(jugador, "Esperar", "Esperando")
        current_partida.post_event(id_jugador, evento_jugador, "Mano")

        armar_broadcast(_partida_=current_partida, 
        msg=armador_evento_log(jugador=jugador, carta=carta, context="defender"), 
        event_name="Log")

        # La carta se juega apropiadamente
        croupier.execute_stack()

    # En ambos casos, es necesario broadcastear los siguientes eventos:
    # Se broadcastea Resultado_defensa
    objetivo_esta_vivo = current_partida.existe_jugador(id_jugador)
    evento_resultado_defensa = EventoResultadoDefensa(nombre_jugador=nombre,
                                                        id_jugador=identficador)
    armar_broadcast(current_partida, evento_resultado_defensa, "Resultado_defensa")
    if not objetivo_esta_vivo:
        evento_muerte = EventoMuerte(contexto="Quemado", nombre_jugador=nombre)
        current_partida.post_event(id_jugador=identficador, 
                                   event=evento_muerte, 
                                   event_name="Muerte")

    # Si el jugador era la cosa, se termina la partida
    if not objetivo_esta_vivo and rol == "La Cosa":
        evento_finalizar = EventoFinalizoPartida(rol_ganador="Humanos", contexto="CosaMuerta")
        armar_broadcast(current_partida, evento_finalizar, "Finalizo_partida")
        current_partida.finalizar()

    else:
        # Si el objetivo murió, se termina su conexión SSE
        #if not objetivo_esta_vivo:
            # Asumimos que evento_resultado_defensa da suficiente info
            # al front para cerrar la escucha de eventos
            #current_partida.terminate_connection(id_jugador)

        # Actualizamos la mano del jugador del turno, que deberá proceder con el intercambio
        turno = current_partida.get_turno()
        
        jugador_turno = current_partida.buscar_jugador_por_posicion(turno)

        # Chequeamos si hay una superinfeccion
        superinfeccion: bool = verificar_superinfeccion(jugador_turno, jugador)
        if superinfeccion:
            aplicar_superinfeccion(partida=current_partida, jugador=jugador_turno)
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
            objetivo_intercambio = obtener_objetivo_intercambio(current_partida, jugador_turno)
            evento_objetivo = EventoObjetivoIntercambio(id_jugador=objetivo_intercambio)
            current_partida.post_event(jugador_turno.get_id(), evento_objetivo, "Objetivo_intercambio")
            evento_mano_intercambio = armador_evento_mano(jugador_turno, "Intercambiar", "Intercambiables")
            current_partida.post_event(jugador_turno.get_id(), evento_mano_intercambio, "Mano")
            
            # Se broadcastea la ronda
            evento_ronda = armador_ronda(id_partida)
            armar_broadcast(current_partida, evento_ronda, "Ronda")

    return