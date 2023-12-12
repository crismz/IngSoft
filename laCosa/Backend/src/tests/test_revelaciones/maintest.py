import sys
sys.path.append("../..")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
from pydantic import BaseModel

from partidas.schema import Partida, ListaPartida, Posicion
from partidas.jugadores.schema import Jugador,IntercambioIn, DatosJugarCarta, DatosJugarDefensa, RevelarIn
from partidas.croupier.schema import DiccionarioCroupier
from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.schema import CardSchema
from partidas.utils import armador_evento_mano, EventoPedidoIntercambio, EventoMano, armar_broadcast, \
                            armador_evento_log, armador_ronda, armador_evento_turno, \
                            armador_evento_carta, armador_evento_mostrar_cartas, \
                            armador_evento_mostrar_mano, EventoRevelar
from partidas.jugadores.utils import event_sender, obtener_objetivo_intercambio, verificar_intercambio
from partidas.events import EventoResultadoDefensa, EventoFinalizoPartida, EventoObjetivoIntercambio


lista_jugadores = []

lista_jugadores.append(Jugador(id=0, nombre="C. Auguste Dupin", posicion=0, rol="La Cosa"))
lista_jugadores.append(Jugador(id=1, nombre="Sherlock Holmes", posicion=1, rol="Infectado"))
lista_jugadores.append(Jugador(id=2, nombre="Long John Silver", posicion=2, rol="Human", cuarentena=True))
lista_jugadores.append(Jugador(id=3, nombre="Kelsier", posicion=3, rol="Human"))


lista_partidas = ListaPartida()

partida = Partida(id=0, nombre="patito", contraseña="123", num_jugadores=0,
                          max_jugadores=6, min_jugadores=4, posiciones=[],
                          turno=1, mazo=None, jugadores=[], iniciada=True, conexiones={})

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
revelaciones = CardSchema(id=108,
                        num_players=partida.get_num_jugadores(),
                        type="Panico",
                        name="Revelaciones",
                        effect="Vuelta de revelaciones",
                        target="self")

lista_jugadores[0].agregar_carta_mano(blank)
lista_jugadores[0].agregar_carta_mano(blank)
lista_jugadores[0].agregar_carta_mano(blank)
lista_jugadores[0].agregar_carta_mano(blank)
lista_jugadores[1].agregar_carta_mano(revelaciones)
lista_jugadores[1].agregar_carta_mano(blank)
lista_jugadores[1].agregar_carta_mano(blank)
lista_jugadores[1].agregar_carta_mano(blank)
lista_jugadores[2].agregar_carta_mano(infectado)
lista_jugadores[2].agregar_carta_mano(blank)
lista_jugadores[2].agregar_carta_mano(blank)
lista_jugadores[2].agregar_carta_mano(blank)
lista_jugadores[3].agregar_carta_mano(blank)
lista_jugadores[3].agregar_carta_mano(blank)
lista_jugadores[3].agregar_carta_mano(blank)
lista_jugadores[3].agregar_carta_mano(blank)

    
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

@app.put("/partidas/{id_partida}/jugadores/{id_jugador}/revelar", status_code=200)
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