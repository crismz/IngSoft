from fastapi import APIRouter, HTTPException, status
from pony.orm import db_session
import re
from typing import List
from partidas.events import (EventoResultadoDefensa, EventoFinalizoPartida, EventoObjetivoIntercambio,
                             EventoRespuestaIntercambio, EventoMuerte, EventoMano)

from partidas.utils import (
    CHAR_LIMIT_PER_MESSAGE, lista_partidas, verificar_datos_creacion, armar_broadcast, armador_evento_mano,
    get_vecinos, armador_ronda, repartir_cartas, armador_evento_turno, primer_turno,
    armador_evento_carta, armador_evento_chat, armador_evento_lobby_jugadores,
    armador_evento_lobby_iniciada, armador_evento_log, verificar_superinfeccion,
    aplicar_superinfeccion, superinfeccion_ronda)

from partidas.models import PartidaDB

# Schemas
from partidas.schema import (
    DatosUnion, Partida, RespuestaCrearPartida, DatosCrearPartida, 
    DatosInicio, Posicion, PartidaOut, ListaPartidaOut, ChatInput,
    DefIntercambioInput
)
from partidas.croupier.utils import diccionario_croupier
from partidas.jugadores.schema import Jugador, DatosJugarCarta, DatosJugarDefensa
from partidas.jugadores.utils import obtener_objetivo_intercambio
from partidas.mazo.schema import Mazo


# Routers
from partidas.jugadores.endpoints import jugadores
from partidas.mazo.endpoints import mazo

partidas = APIRouter()
# Incluyo los routers 'bajo partidas'
partidas.include_router(jugadores, prefix="/{id_partida}/jugadores", tags=["jugadores"])
partidas.include_router(mazo, prefix="/{id_partida}/mazo", tags=["mazo"])


@partidas.get("", status_code=200)
async def listar_partidas():

    # Creamos listado de partidas
    listado = ListaPartidaOut()

    total_partidas = lista_partidas.get_length()

    # Agregamos las partidas que no estén iniciadas
    for i in range(total_partidas):
        partida = lista_partidas.get_partida_by_index(i)
        if(not partida.esta_iniciada()):
            listado.append(PartidaOut(id_partida=partida.get_id(),
                                    nombre_partida=partida.get_nombre(), 
                                    jugadores_act=partida.get_num_jugadores(),
                                    max_jugadores=partida.get_max_jugadores(),
                                    tiene_contraseña=partida.get_contraseña() is not None))
            
    return listado

#### DEPRECATED, cuando este sse de lobby####
@partidas.get("/{id_partida}/listar_jugadores", status_code=200)
async def listar_jugadores(id_partida: int):
    # Chequeamos si la partida está creada
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) Not Found")
    
    # Como la partida existe, la obtenemos
    # y preparamos la respuesta para el front
    current_partida = lista_partidas.get_partida_by_index(index)
    jugadores_unidos = current_partida.obtener_jugadores()
    iniciada = current_partida.esta_iniciada()
    lista_jugadores = []
    for each in jugadores_unidos:
        nombre_jugador = each.get_nombre()
        lista_jugadores.append({"name" : nombre_jugador})
    
    response = {
        "jugadores" : lista_jugadores,
        "partida_iniciada" : iniciada,
    }
    return response

@partidas.post("/crear", status_code=201)
async def crear_partida(partida_info: DatosCrearPartida) -> RespuestaCrearPartida:

    # Tratamiento de los string
    partida_info.nombre_partida = re.sub(' +', ' ', partida_info.nombre_partida.strip())
    partida_info.nombre_jugador = re.sub(' +', ' ', partida_info.nombre_jugador.strip())

    # Verificamos datos
    if not verificar_datos_creacion(partida_info=partida_info):
        raise HTTPException(status_code=400, detail="Data Malformed") 

    # Guardamos Partida en base de datos
    with db_session:
        partidaDB = PartidaDB(
            nombre=partida_info.nombre_partida,
            contraseña=partida_info.contraseña,
            max_jugadores=partida_info.max_jugadores,
            min_jugadores=partida_info.min_jugadores,
            iniciada=False,
        )

    # Creamos una instancia de Partida
    partida = Partida(
        nombre=partida_info.nombre_partida, 
        max_jugadores=partida_info.max_jugadores,
        min_jugadores=partida_info.min_jugadores
    )

    # Seteamos los atributos de la partida creada
    partida.set_id(partidaDB.partida_id)
    partida.set_nombre(partida_info.nombre_partida)
    if(partida_info.contraseña != ""):
        partida.set_contraseña(partida_info.contraseña)
    partida.set_mazo(Mazo(id_partida=partida.get_id()))
    nuevo_jugador = Jugador(id=0, 
                        nombre=partida_info.nombre_jugador,
                        posicion=0, 
                        rol="Humano", 
                        mano=[])
    partida.set_num_jugadores(0)
    partida.agregar_jugador(nuevo_jugador)

    # Agregamos a la lista de partidas
    lista_partidas.append(partida)

    # Respondemos al Front
    resp = RespuestaCrearPartida(id_partida=partida.get_id(), id_jugador=0)
    return resp

@partidas.get("/{id_partida}", status_code=200)
async def info_partida(id_partida: int):
    
    # Chequeamos si la partida está creada
    index = lista_partidas.get_index_by_id(id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) Not Found")
    
    # Como la partida está creada, preparamos la respuesta al front
    current_partida = lista_partidas.get_partida_by_index(index)
    response = {
        "nombre_partida" : current_partida.get_nombre(),
        "min_jugadores": current_partida.get_min_jugadores(),
        "max_jugadores": current_partida.get_max_jugadores()
    }

    return response

@partidas.patch("/{id_partida}/iniciar", status_code=200)
async def iniciar_partida(id_partida: int, datosInicio: DatosInicio):

    id_jugador = datosInicio.id_jugador
    # Chequeamos si la partida está creada
    index = lista_partidas.get_index_by_id(id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) Not Found")
    
    # Chequeamos si el jugador que inicia la partida es el creador
    if id_jugador != 0:
        raise HTTPException(status_code=422, detail=f"ID ({id_jugador}) Is Invalid")
    
    # Chequeamos que haya suficientes jugadores
    current_partida = lista_partidas.get_partida_by_index(index)
    jugadores_unidos = current_partida.get_num_jugadores()
    jugadores_requeridos = current_partida.get_min_jugadores()
    if jugadores_unidos < jugadores_requeridos:
        raise HTTPException(status_code=400, detail=f"Not Enough Players")
    
    # Chequeamos si la partida ya está iniciada
    if current_partida.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Already Started")
    
    # Creamos el mazo
    current_mazo = current_partida.get_mazo()
    current_mazo.create_deck(id_partida, jugadores_unidos)

    # Creamos las posiciones
    for _ in range(jugadores_unidos):
        current_partida.agregar_posicion(Posicion())

    # Asignamos el primer turno
    current_partida.set_turno(primer_turno(jugadores_unidos))

    # Asignamos los jugadores que hay al iniciar la partida
    current_partida.set_num_jugadores_inicial(jugadores_unidos)

    # Repartimos las cartas
    repartir_cartas(mazo=current_mazo, jugadores=current_partida.obtener_jugadores())

    # Cambiar el estado de la partida a iniciada en database
    with db_session:
        entidad_partida = PartidaDB.get(partida_id=current_partida.get_id())
        if entidad_partida:
            entidad_partida.iniciada = True

    # Cambiar el estado de la partida a iniciada en el back
    current_partida.iniciar()

    # Agregamos un croupier al diccionario de croupiers
    diccionario_croupier.append(current_partida) 

    # Hacemos la respuesta para el front
    response = {"message" : "ok"}

    #Broadcasteamos que la partida está iniciada
    evento_iniciada = armador_evento_lobby_iniciada(current_partida.esta_iniciada())
    armar_broadcast(current_partida, evento_iniciada, "Lobby_iniciada")

    return response


@partidas.post("/{id_partida}/unir", status_code=201)
async def unir_jugador(id_partida: int, datosUnion: DatosUnion):
    
    # Obtengo la partida deseada mediante el id con {id_partida}
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) Not Found")
    
    # Esto es una REFERENCIA a la partida, ergo los cambios se reflejan en el objeto original
    _partida_ : Partida = lista_partidas.get_partida_by_index(index)

    # Verifico si aún no ha iniciado la partida, en cuyo caso arrojo 422 (Bad Entity)
    if _partida_.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Already Started")

    # Guardo el número de jugadores en la partida para usar de acá en adelante
    cantidad_jugadores = _partida_.get_num_jugadores()

    # Veo si hay lugar en la partida. De no ser así, devuelvo 400 (Bad Request)
    if _partida_.get_max_jugadores() == cantidad_jugadores:
        raise HTTPException(status_code=400, detail="Lobby Already at Capacity")

    # Si contraseña != None, comparo contraseñas
    if _partida_.get_contraseña() is not None:
        if _partida_.get_contraseña() != datosUnion.contraseña:
            # Si la contraseña no es correcta, devuelvo 400 (Bad Request)
            raise HTTPException(status_code=400, detail="Incorrect Password")
        
    # Asigno ID al jugador y actualizo la cantidad de jugadores en la partida
    # Busco id de jugador disponible
    for i in range(cantidad_jugadores+1):
        if not _partida_.existe_jugador(i):
            id_jugador = i
            break
        
    nuevo_jugador = Jugador(id=id_jugador, 
                            nombre=datosUnion.nombre_jugador,
                            posicion=id_jugador, 
                            rol="Humano", 
                            mano=[])
    _partida_.agregar_jugador(nuevo_jugador)

    #Broadcasteamos la llegada del nuevo jugador
    evento_jugadores = armador_evento_lobby_jugadores(
        lista_jugadores=_partida_.obtener_jugadores()
    )
    armar_broadcast(_partida_, evento_jugadores, "Lobby_jugadores")
    
    # Incluyo ese mismo ID en la respuesta    
    return {"id_jugador" : id_jugador}

@partidas.post("/{id_partida}/chat", status_code=200)
async def chatear(id_partida: int, chat_input_data: ChatInput):
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) Not Found")
    
    _partida_ : Partida = lista_partidas.get_partida_by_index(index)

    #if not _partida_.esta_iniciada():
    #    raise HTTPException(status_code=422, detail="Game Not Yet Started")
    
    if len(chat_input_data.mensaje) > CHAR_LIMIT_PER_MESSAGE:
        raise HTTPException(status_code=413, detail="Message Is Too Long")
    
    nombre_emisor = _partida_.buscar_jugador(chat_input_data.id_jugador).get_nombre()
    nuevo_evento_chat = armador_evento_chat(nombre_emisor, chat_input_data.mensaje)

    armar_broadcast(_partida_=_partida_, msg=nuevo_evento_chat, event_name="Chat")

    return

@partidas.patch("/{id_partida}/finalizar_turno", status_code=200)
async def fin_turno(id_partida: int):

    # Obtengo la partida deseada mediante el id con {id_partida}
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) Not Found")
    
    # Esto es una REFERENCIA a la partida, ergo los cambios se reflejan en el objeto original
    _partida_ : Partida = lista_partidas.get_partida_by_index(index)

    # Verifico si aún no ha iniciado la partida, en cuyo caso arrojo 422 (Bad Entity)
    if not _partida_.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Not Yet Started")
    
    #  Primero necesito saber cuántos jugadores hay, ya que dados N jugadores presentes
    # en la partida, las posiciones estarán definidas de 0 a N - 1 clockwise 
    ultima_posicion : int = _partida_.get_num_jugadores() - 1

    turno_por_terminar : int = _partida_.get_turno()

    # Reseteo los contadores de acciones de todos
    lista_jugadores: List[Jugador] = _partida_.obtener_jugadores()
    for each in lista_jugadores:
        each.resetear_acciones()
        # Checheamos si hay que sacarlo de la cuarentena
        if (each.get_posicion() == turno_por_terminar and
            each.esta_en_cuarentena()):
            each.rondas_en_cuarentena -= 1

            if each.rondas_en_cuarentena <= 0:
                each.sacar_de_cuarentena()
                # Descartamos la carta de cuarentena
                mazo = _partida_.get_mazo()
                mazo.discard_played_card("Cuarentena")
                armar_broadcast(_partida_= _partida_,
                                msg=armador_evento_log(jugador=each,
                                                       message=f"{each.get_nombre()} salió de cuarentena"),
                                event_name="Log")
                armar_broadcast(_partida_= _partida_,
                                msg=armador_ronda(_partida_.get_id()),
                                event_name="Ronda")
                                
    proximo_turno : int

    #  Si el sentido es positivo/clockwise (True), sumo 1 al turno salvo que se trate de la ultima
    # posición, en cuyo caso el turno pasa a tenerlo quien se encuentre en la primera posición (0)
    if _partida_.get_sentido() == True:
        if turno_por_terminar == ultima_posicion:
            proximo_turno = 0
        else:
            proximo_turno = turno_por_terminar + 1
    #  Si el sentido es negativo/counter-clockwise (False), sustraigo 1 al turno salvo que se trate de
    # la primera posición, en cuyo caso el turno pasa a tenerlo quien se encuentre en la última posición
    else:
        if turno_por_terminar == 0:
            proximo_turno = ultima_posicion
        else:
            proximo_turno = turno_por_terminar - 1
    
    # Los cambios a 
    _partida_.set_turno(proximo_turno)

    # Enviamos evento log de turno
    jugador_turno = _partida_.buscar_jugador_por_posicion(proximo_turno)
    armar_broadcast(_partida_=_partida_,
                    msg=armador_evento_log(jugador=jugador_turno, context="comienzo_turno"), 
                    event_name="Log")

    # Enviamos el evento de turno
    armar_broadcast(_partida_,msg=armador_evento_turno(_partida_.get_id()), event_name="Turno")

    jugador_turno.set_accion("robos", 1)
    jugador_turno.set_accion("intercambios", 1)
    jugador_turno.set_accion("descartes", 1)
    return

@partidas.put("/{id_partida}/jugadores/{id_jugador}/jugar", status_code=200)
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
            # Chequeamos si hay una superinfeccion, pero antes de chequeamos que no
            # haya un bloqueo con el jugador que va a intercambiar
            objetivo_intercambio = obtener_objetivo_intercambio(current_partida, jugador)
            superinfeccion: bool = False
            if objetivo_intercambio != -2: 
                jugador_objetivo = current_partida.buscar_jugador(objetivo_intercambio)
                superinfeccion = verificar_superinfeccion(jugador, jugador_objetivo)
            else:
                superinfeccion = verificar_superinfeccion(jugador, jugador)
            if ((carta.get_id() not in range(60,67) and carta.get_id() not in range(101,103)) and
            objetivo_intercambio != -2 and
            current_partida.son_adyacentes(jugador.get_posicion(), jugador_objetivo.get_posicion()) and
            current_partida.hay_bloqueo(jugador.get_posicion(), jugador_objetivo.get_posicion())):
                # Mandamos log
                armar_broadcast(_partida_=current_partida,
                                msg=armador_evento_log(jugador=jugador,
                                                       objetivo=jugador_objetivo,
                                                       context="bloqueo"),
                                event_name="Log")
                # Terminamos el turno
                evento_mano : EventoMano = armador_evento_mano(jugador=jugador,
                                                        instancia="Esperar", 
                                                        context="Fin_Turno")
                current_partida.post_event(id_jugador=jugador.get_id(), 
                         event=evento_mano, 
                         event_name="Mano")
            elif superinfeccion:
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

@partidas.put("/{id_partida}/jugadores/{id_jugador}/defensa", status_code=200)
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

        jugador.añadir_accion("robos")


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

        # Chequeamos si hay una superinfeccion, pero antes de chequeamos que no
        # haya un bloqueo con el jugador que va a intercambiar
        objetivo_intercambio = obtener_objetivo_intercambio(current_partida, jugador_turno)
        jugador_objetivo = current_partida.buscar_jugador(objetivo_intercambio)
        superinfeccion: bool = verificar_superinfeccion(jugador_turno, jugador_objetivo)
        if (current_partida.son_adyacentes(jugador_turno.get_posicion(), jugador_objetivo.get_posicion()) and
            current_partida.hay_bloqueo(jugador_turno.get_posicion(), jugador_objetivo.get_posicion())):
                # Mandamos log
                armar_broadcast(_partida_=current_partida,
                                msg=armador_evento_log(jugador=jugador_turno,
                                                       objetivo=jugador_objetivo,
                                                       context="bloqueo"),
                                event_name="Log")
                # Terminamos el turno
                evento_mano : EventoMano = armador_evento_mano(jugador=jugador_turno,
                                                        instancia="Esperar", 
                                                        context="Fin_Turno")
                current_partida.post_event(id_jugador=jugador_turno.get_id(), 
                         event=evento_mano, 
                         event_name="Mano")
        elif superinfeccion:
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
            evento_objetivo = EventoObjetivoIntercambio(id_jugador=objetivo_intercambio)
            current_partida.post_event(jugador_turno.get_id(), evento_objetivo, "Objetivo_intercambio")
            evento_mano_intercambio = armador_evento_mano(jugador_turno, "Intercambiar", "Intercambiables")
            current_partida.post_event(jugador_turno.get_id(), evento_mano_intercambio, "Mano")
            
            # Se broadcastea la ronda
            evento_ronda = armador_ronda(id_partida)
            armar_broadcast(current_partida, evento_ronda, "Ronda")

    return

@partidas.put("/{id_partida}/jugadores/{id_jugador}/defensa_intercambio", status_code=200)
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
                                                      id_jugador=id_jugador)
    armar_broadcast(current_partida, evento_resultado_defensa, "Resultado_defensa")

    jugador.añadir_accion("robos")
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
