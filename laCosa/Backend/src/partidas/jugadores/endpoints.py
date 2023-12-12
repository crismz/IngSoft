from fastapi import APIRouter, HTTPException
from pony.orm import db_session, select
from sse_starlette.sse import EventSourceResponse
from typing import List

from partidas.schema import Partida
from partidas.jugadores.utils import (event_sender, intercambiar_cartas, 
                                      obtener_objetivo_intercambio, verificar_intercambio,
                                     intercambiar_con_mazo)
from partidas.jugadores.schema import (IntercambioIn, RespuestaIntercambioIn, 
                                       Jugador, RevelarIn, IdCartaIn)
from partidas.croupier.schema import Croupier
from partidas.croupier.utils import diccionario_croupier
from partidas.events import (EventoMano, EventoFinalizoPartida, EventoPedidoIntercambio, 
                             EventoRespuestaIntercambio, EventoDescartarCarta, 
                             EventoObjetivoIntercambio, EventoRevelar)
from partidas.utils import *

from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.schema import CardSchema
from partidas.models import PartidaDB

jugadores = APIRouter()

@jugadores.get("/")
async def root_jugadores():
    return {"message" : "Ok"}


@jugadores.delete("/{id_jugador}", status_code=200)
async def abandonar_partida(id_partida: int, id_jugador: int):
    # Obtengo la partida deseada mediante el id con {id_partida}
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"ID ({id_partida}) for match Not Found")

    current_partida = lista_partidas.get_partida_by_index(index)
    
    # Si la partida esta iniciada y no finalizada, no se puede abandonar
    if current_partida.esta_iniciada() and not current_partida.esta_finalizada():
        raise HTTPException(status_code=422, detail="Game already started, can't leave now")

    # Verifico si el jugador existe, en caso de que no arrojo 404
    if not current_partida.existe_jugador(id_jugador):
        raise HTTPException(status_code=404, detail=f"ID ({id_jugador}) for player Not Found")
    
    jugador = current_partida.buscar_jugador(id_jugador)

    # Verifico si es el creador de la partida, y que la partida no haya iniciado 
    if id_jugador == 0 and not current_partida.esta_iniciada():
        # Elimino al usuario
        current_partida.eliminar_jugador(jugador=jugador)
        current_partida.terminate_connection(id_jugador) 
        # Mando a todos los jugadores evento para que abandonen
        evento_abortado = armador_evento_lobby_iniciada(current_partida.esta_iniciada())
        armar_broadcast(_partida_=current_partida, msg=evento_abortado, event_name="Lobby_abortado")

    # Si se va cualquier otro jugador, no importa que la partida haya iniciado o no,
    # se elimina al jugador
    else:

        log = armador_evento_log(
            jugador=current_partida.buscar_jugador(id_jugador),
            context="salirse"
        )
        current_partida.eliminar_jugador(jugador=jugador)
        current_partida.terminate_connection(id_jugador)
        # Si la partida no esta iniciada, se manda el evento para que sepan que se fue
        if not current_partida.esta_iniciada():
            armar_broadcast(current_partida, log, "Log")
            evento_lobby = armador_evento_lobby_jugadores(current_partida.get_jugadores())
            armar_broadcast(_partida_=current_partida, msg=evento_lobby, event_name="Lobby_jugadores")
        
    # Si era el ultimo jugador, se elimina la partida
    if current_partida.get_num_jugadores() == 0:
            if current_partida.esta_iniciada():
                # Eliminamos el croupier correspondiente
                croupier = diccionario_croupier.get_croupier(id)
                diccionario_croupier.remove(id)
                del croupier

            eliminar_partida(current_partida)

    return

@jugadores.patch("/{id_jugador}/intercambiar", status_code=200)
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

@jugadores.patch("/{id_jugador}/resolver_intercambio", status_code=200)
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

    
@jugadores.get("/sse/{id_jugador}")
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
 
    
@jugadores.get("/sse/{id_jugador}/lobby")
async def suscribir_al_lobby(id_partida: int, id_jugador: int):

    # Obtengo la partida deseada mediante el id con {id_partida}
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"Match ID ({id_partida}) Not Found")
    
    # Como la partida existe, la obtenemos
    current_partida = lista_partidas.get_partida_by_index(index)   

    # Chequeamos que la partida esté iniciada
    if current_partida.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Started Already!")

    # Chequeamos que el jugador esté en la partida
    if not current_partida.existe_jugador(id_jugador):    
        raise HTTPException(status_code=404, detail=f"Player ID ({id_jugador}) Not Found")
    
    try:
        if not current_partida.is_connected(id_jugador):
            current_partida.connect(id_jugador)
            current_jugadores = current_partida.obtener_jugadores()
            evento_jugadores = armador_evento_lobby_jugadores(current_jugadores)

            # Aunque se broadcastea un evento de jugadores cuando añadimos a cada jugador
            # necesitamos que se envíen estos eventos al jugador que se une
            # por el orden en que se invocan los endpoints
            current_partida.post_event(id_jugador, evento_jugadores, "Lobby_jugadores")
            log = armador_evento_log(
                jugador=current_partida.buscar_jugador(id_jugador),
                context="unirse"
            )
            armar_broadcast(current_partida, log, "Log")
            return EventSourceResponse(event_sender(current_partida, id_jugador))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

            
@jugadores.patch("/{id_jugador}/descartar", status_code=200)
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
            
        # Chequeamos si hay una superinfeccion, pero antes de chequeamos que no
        # haya un bloqueo con el jugador que va a intercambiar
        jugador_objetivo = _partida_.buscar_jugador(
                                    obtener_objetivo_intercambio(_partida_, jugador))
        superinfeccion: bool = verificar_superinfeccion(jugador, jugador_objetivo)
        if (_partida_.son_adyacentes(jugador.get_posicion(), jugador_objetivo.get_posicion()) and
            _partida_.hay_bloqueo(jugador.get_posicion(), jugador_objetivo.get_posicion())):
                # Mandamos log
                armar_broadcast(_partida_=_partida_,
                                msg=armador_evento_log(jugador=jugador,
                                                       objetivo=jugador_objetivo,
                                                       context="bloqueo"),
                                event_name="Log")
                # Terminamos el turno
                evento_mano : EventoMano = armador_evento_mano(jugador=jugador,
                                                        instancia="Esperar", 
                                                        context="Fin_Turno")
                _partida_.post_event(id_jugador=jugador.get_id(), 
                         event=evento_mano, 
                         event_name="Mano")
        elif superinfeccion:
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
    
    return {"message" : "OK"}

@jugadores.patch("/{id_jugador}/vuelta_y_vuelta", status_code=200)
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

@jugadores.get("/{id_jugador}/declarar_victoria", status_code=200)
async def declarar_victoria(id_partida: int, id_jugador: int):
 
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
    
    # Chequeamos que el jugador es la Cosa
    if current_partida.buscar_jugador(id_jugador).get_rol() != "La Cosa":
        raise HTTPException(status_code=400, detail="Only The Thing can declare victory")

    # Si no están todos infectados, por lo tanto queda algún humano
    if not current_partida.todos_infectados():
        # Ganan los humanos
        evento_finalizar = EventoFinalizoPartida(rol_ganador="Humanos", contexto="MalDeclaracion")
        armar_broadcast(current_partida, evento_finalizar, "Finalizo_partida")
    else:
        # Si todos fueron infectados
        if current_partida.get_num_jugadores() == current_partida.get_num_jugadores_inicial():
            # Gana la Cosa
            evento_finalizar = EventoFinalizoPartida(rol_ganador="La Cosa", contexto="TodosInfectados")
            armar_broadcast(current_partida, evento_finalizar, "Finalizo_partida")
        else:
            # Ganan los infectados
            evento_finalizar = EventoFinalizoPartida(rol_ganador="Infectados", contexto="NoHumanos")
            armar_broadcast(current_partida, evento_finalizar, "Finalizo_partida")
  
    # Finalizamos la partida
    current_partida.finalizar()

    return

@jugadores.put("/{id_jugador}/revelar", status_code=200)
async def revelar(id_partida: int, id_jugador: int, revela: RevelarIn):
    # Obtengo la partida deseada mediante el id con {id_partida}
    index = lista_partidas.get_index_by_id(id_param=id_partida)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"Match ID ({id_partida}) Not Found")
    
    # Como la partida existe, la obtenemos
    partida = lista_partidas.get_partida_by_index(index)   

    # Chequeamos que la partida esté iniciada
    if not partida.esta_iniciada():
        raise HTTPException(status_code=422, detail="Game Not Started Yet")

    # Chequeamos que el jugador esté en la partida
    if not partida.existe_jugador(id_jugador):    
        raise HTTPException(status_code=404, detail=f"Player ID ({id_jugador}) Not Found")
    
    jugador = partida.buscar_jugador(id_jugador)

    # Bool para indicar si termino revelaciones
    termino_revelaciones = False

    # Si decide revelar la carta chequeamos que tenga una carta infectado,
    # si tiene solo muestra esa carta y termina la ronda de Revelaciones,
    # en caso contrario muestra toda la mano
    if revela.revela:
        mano_jugador = jugador.get_mano()
        for each in mano_jugador:
            if each.get_name() == "Infectado":
                termino_revelaciones = True
                mano: list = [armador_evento_mostrar_cartas(id=each.get_id(),
                                                      name=each.get_name(),
                                                      type=each.get_type(),
                                                      effectDescription=each.get_effect()
                                                      )
                ]
                continue
        
        if termino_revelaciones:
            armar_broadcast(_partida_ = partida,
                            msg = armador_evento_mostrar_mano(id_jugador, mano),
                            event_name = 'Cartas_mostrables')
        else:
            mano : list = [
                armador_evento_mostrar_cartas(id=carta.get_id(),
                                            name=carta.get_name(),
                                            type=carta.get_type(),
                                            effectDescription=carta.get_effect()
                                            )
                for carta in mano_jugador
            ]
            armar_broadcast(_partida_ = partida,
                            msg = armador_evento_mostrar_mano(id_jugador, mano),
                            event_name = 'Cartas_mostrables')

    proximo_jugador = partida.proximo_en_ronda(jugador.get_posicion())
    # Chequeamos si se termina por mostrar carta infectado o por dar vuelta la ronda    
    if termino_revelaciones or proximo_jugador.get_posicion() == partida.get_turno():
        
        evento_log = armador_evento_log(jugador=jugador, message="Finalizo ronda de Revelaciones")
        armar_broadcast(_partida_=partida, msg=evento_log, event_name="Log")
        # Si se termina, prosigue el jugador en turno con el intercambio
        jugador_turno = partida.buscar_jugador_por_posicion(partida.get_turno())
        objetivo_intercambio = obtener_objetivo_intercambio(partida, jugador_turno)
        evento_objetivo = EventoObjetivoIntercambio(id_jugador=objetivo_intercambio)
        partida.post_event(jugador_turno.get_id(), evento_objetivo, "Objetivo_intercambio")
        # Actualizamos la mano del jugador de la carta para el intercambio
        evento_mano = armador_evento_mano(jugador=jugador_turno,
                                        instancia="Intercambiar",
                                        context="Intercambiables",
                                        )
        partida.post_event(id_jugador=jugador_turno.get_id(), 
                           event=evento_mano, 
                           event_name="Mano")

    else:
        # Si no se termina la ronda revelaciones se manda el evento
        # al proximo jugador que debe revelar
        evento_revelar = EventoRevelar(id_jugador=proximo_jugador.get_id())
        partida.post_event(id_jugador=proximo_jugador.get_id(), 
                           event=evento_revelar, 
                           event_name="Revelar")
