import sys
sys.path.append("../..")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
from pydantic import BaseModel

from partidas.schema import Partida, ListaPartida, Posicion
from partidas.jugadores.schema import Jugador,IntercambioIn, DatosJugarCarta, DatosJugarDefensa
from partidas.croupier.schema import DiccionarioCroupier
from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.schema import CardSchema
from partidas.utils import armador_evento_mano, EventoPedidoIntercambio, EventoMano, armar_broadcast, \
                            armador_evento_log, armador_ronda, armador_evento_turno, verificar_superinfeccion, \
                            aplicar_superinfeccion, armador_evento_carta
from partidas.jugadores.utils import event_sender, obtener_objetivo_intercambio, verificar_intercambio
from partidas.events import EventoResultadoDefensa, EventoFinalizoPartida, EventoObjetivoIntercambio


lista_jugadores = []

lista_jugadores.append(Jugador(id=0, nombre="C. Auguste Dupin", posicion=0, rol="La Cosa"))
lista_jugadores.append(Jugador(id=1, nombre="Sherlock Holmes", posicion=1, rol="Infectado"))
lista_jugadores.append(Jugador(id=2, nombre="Long John Silver", posicion=2, rol="Human", cuarentena=True))
lista_jugadores.append(Jugador(id=3, nombre="Kelsier", posicion=3, rol="Human"))


lista_partidas = ListaPartida()

# Si es el turno del jugador 0 no entra a superinfeccion por ser 
partida = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=0,
                          max_jugadores=6, min_jugadores=4, posiciones=[],
                          turno=2, mazo=None, jugadores=[], iniciada=True, conexiones={})

for each in range(len(lista_jugadores)):
    jugador = lista_jugadores[each]
    partida.agregar_jugador(jugador)

partida.agregar_posicion(Posicion())
partida.agregar_posicion(Posicion())
partida.agregar_posicion(Posicion())
partida.agregar_posicion(Posicion())


current_mazo = Mazo(id_partida=0)
partida.set_mazo(current_mazo)
# Repartir las cartas que queremos que estén en las manos de los jugadores
infectado = CardSchema(id=1,
                    num_players=partida.get_num_jugadores(),
                    type="Contagio",
                    name="Infectado",
                    effect="Infecta a alguien",
                    target="self"
                    )
blank = CardSchema(id=0,
                    num_players=partida.get_num_jugadores(),
                    type="Blank",
                    name="Blank",
                    effect="Se descarta sin afectar la partida",
                    target="any")

lista_jugadores[0].agregar_carta_mano(blank)
lista_jugadores[0].agregar_carta_mano(blank)
lista_jugadores[0].agregar_carta_mano(blank)
lista_jugadores[0].agregar_carta_mano(blank)
lista_jugadores[1].agregar_carta_mano(infectado)
lista_jugadores[1].agregar_carta_mano(infectado)
lista_jugadores[1].agregar_carta_mano(infectado)
lista_jugadores[1].agregar_carta_mano(infectado)
lista_jugadores[2].agregar_carta_mano(infectado)
lista_jugadores[2].agregar_carta_mano(infectado)
lista_jugadores[2].agregar_carta_mano(infectado)
lista_jugadores[2].agregar_carta_mano(infectado)
lista_jugadores[3].agregar_carta_mano(infectado)
lista_jugadores[3].agregar_carta_mano(infectado)
lista_jugadores[3].agregar_carta_mano(infectado)
lista_jugadores[3].agregar_carta_mano(infectado)

    
lista_partidas.append(partida)
# Crear el diccionario de croupiers
diccionario_croupier = DiccionarioCroupier()
# Añadir el diccionario de croupiers de la partida
diccionario_croupier.append(partida)


class WelcomeMessage(BaseModel):
    msg: str = ""

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    # Chequeo que el jugador_objetivo no cumpla las condiciones de superinfeccion
    # En caso de que este superinfectado se cancela el intercambio y se manda evento de fin de turno
    superinfeccion: bool = verificar_superinfeccion(jugador_objetivo)
    if superinfeccion and not (jugador_objetivo.get_rol() == "Infectado" 
                                and jugador.get_rol() == "La Cosa"):
        # Se eliminar el jugador y se envia el evento log y ronda
        mazo = partida.get_mazo()
        mano = jugador.remover_mano()
        for each in mano:
            mazo.discard_card(each)
        partida.eliminar_jugador(jugador)
        armar_broadcast(_partida_=partida,
                        msg=armador_evento_log(jugador=jugador, context="morir_superinfeccion"),
                        event_name="Log")
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
            # Chequeamos si hay una superinfeccion
            jugador_objetivo = current_partida.buscar_jugador(id_objetivo)
            superinfeccion: bool = verificar_superinfeccion(jugador)
            if superinfeccion and not (jugador.get_rol() == "Infectado" 
                            and jugador_objetivo.get_rol() == "La Cosa"):
                # Se eliminar el jugador y se envia el evento log y ronda
                mazo = partida.get_mazo()
                mano = jugador.remover_mano()
                for each in mano:
                    mazo.discard_card(each)
                partida.eliminar_jugador(jugador)
                armar_broadcast(_partida_=partida,
                                msg=armador_evento_log(jugador=jugador, context="morir_superinfeccion"),
                                event_name="Log")
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
                                                        id_jugador=identficador,
                                                        esta_vivo=objetivo_esta_vivo)
    armar_broadcast(current_partida, evento_resultado_defensa, "Resultado_defensa")

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
        superinfeccion: bool = verificar_superinfeccion(jugador_turno)
        if superinfeccion and not (jugador_turno.get_rol() == "Infectado" 
                        and jugador.get_rol() == "La Cosa"):
            # Se eliminar el jugador y se envia el evento log y ronda
            mazo = partida.get_mazo()
            mano = jugador.remover_mano()
            for each in mano:
                mazo.discard_card(each)
            partida.eliminar_jugador(jugador)
            armar_broadcast(_partida_=partida,
                            msg=armador_evento_log(jugador=jugador, context="morir_superinfeccion"),
                            event_name="Log")
        else:
            objetivo_intercambio = obtener_objetivo_intercambio(current_partida, jugador_turno)
            evento_objetivo = EventoObjetivoIntercambio(id_jugador=objetivo_intercambio)
            current_partida.post_event(jugador_turno.get_id(), evento_objetivo, "Objetivo_intercambio")
            evento_mano_intercambio = armador_evento_mano(jugador_turno, "Intercambiar", "Intercambiables")
            current_partida.post_event(jugador_turno.get_id(), evento_mano_intercambio, "Mano")
            

    return