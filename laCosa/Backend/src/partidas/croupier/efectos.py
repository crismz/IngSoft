from partidas.schema import Partida
from partidas.utils import (armador_evento_mostrar_cartas, armador_evento_mostrar_mano,
                            armador_evento_log, armar_broadcast, armador_evento_mano,
                            armador_ronda)
from partidas.events import *
from partidas.jugadores.schema import Jugador
from partidas.mazo.cartas.schema import CardSchema
from partidas.jugadores.utils import obtener_objetivo_intercambio
import random
from abc import ABC, abstractmethod

class CardEffect(ABC):
    @abstractmethod
    def verificar(self, id_carta:int, id_jugador: int, id_objetivo: int, partida: Partida):
        pass

    @abstractmethod
    def aplicar(self, id_objetivo: int, partida: Partida, id_jugador: int = None):
        pass

class Quemar(CardEffect):

    def verificar(self, id_carta:int, id_jugador: int, id_objetivo: int, partida: Partida):
        #Verificamos que la carta es un lanzallamas
        if id_carta not in range(22, 27):
            return False
        
        # Chequeamos que un jugador no use el lanzallamas en si mismo
        if id_jugador == id_objetivo:
            return False

        jugador = partida.buscar_jugador(id_jugador)
        objetivo = partida.buscar_jugador(id_objetivo)

        # Obtenemos las posiciones de los jugadores
        posicion_jugador = jugador.get_posicion()
        posicion_objetivo = objetivo.get_posicion()

        # Chequeamos si los jugadores son adyacentes
        if not partida.son_adyacentes(posicion_jugador, posicion_objetivo):
            return False

        # Chequeamos si hay un bloqueo que impida que la carta se juegue
        if partida.hay_bloqueo(posicion_jugador, posicion_objetivo):
            return False

        if jugador.esta_en_cuarentena():
            return False
            
        return True
    
    def aplicar(self, id_objetivo: int, partida: Partida):
        # Obtenemos el objetivo del lanzallamas
        objetivo = partida.buscar_jugador(id_objetivo)
        # Obtenemos el mazo de la partida
        mazo = partida.get_mazo()
        # Quitamos la mano al objetivo y la agregamos a la pila de descarte
        mano = objetivo.remover_mano()
        for each in mano:
            mazo.discard_card(each)
        # Eliminamos el jugador de la partida
        # No hace falta eliminar la posición pues esto ya es manejado
        # por la instancia de Partida
        partida.eliminar_jugador(objetivo)
        # Mandamos evento log
        armar_broadcast(_partida_=partida,
                        msg=armador_evento_log(jugador=objetivo, context="morir_incinerado"),
                        event_name="Log")

class Extintor(CardEffect):
    def verificar(self, id_carta:int, id_jugador: int, id_objetivo: int, partida: Partida):
        # La defensa del lanzallamas requiere una lógica complementaria
        # al mismo lanzallamas
        # Chequeamos que la carta que se usa para defenderse es un
        # "Nada de Barbacoas"
        if id_carta not in range(81, 84):
            return False
        
        # Chequeamos que el jugador está jugando la defensa sobre sí mismo
        if id_jugador != id_objetivo:
            return False
        
        # Chequeamos que la última carta jugada es un lanzallamas y que
        # el objetivo es el jugador de la carta de defensa
        tupla = partida.desapilar()
        id_carta = tupla[0]
        objetivo = tupla[1]
        partida.apilar(tupla)
        if not (id_carta in range(22, 27) and objetivo == id_jugador):
            return False
        
        return True
    
    def aplicar(self, id_objetivo: int, partida: Partida):
        # Si bien asumimos que verificar() se ha llamado antes
        # para asegurar que el desapilar() es procedente, usamos el
        # id del objetivo para chequear lo desapilado pues el aplicar()
        # puede llamarse independientemente del verificar()
        tupla = partida.desapilar()
        if tupla[1] != id_objetivo:
            partida.apilar(tupla)

class Seducir(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):

        if id_carta not in range(60, 67):
            return False
        
        if id_jugador == id_objetivo:
            return False

        # Verificar si el jugador objetivo está en cuarentena
        if partida.buscar_jugador(id_jugador=id_objetivo).esta_en_cuarentena():
            return False

        return True

    def aplicar(self, id_objetivo: int, partida: Partida):
        #  Sólo altero el objetivo del intercambio, ya que después de realizar
        # el mismo sólo queda terminar el turno (como normalmente)
        jugador = partida.buscar_jugador_por_posicion(partida.get_turno())
        jugador.set_id_objetivo_intercambio(id_objetivo)
        return
    
class NoGracias(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):
        if id_carta not in range(74, 78):
            return False

        # No se puede jugar en respuesta a otra carta propiamente dicha
        if partida.get_largo_stack() != 0:
            return False
        
        #  Si se inició un intercambio, el jugador que lo hizo tendrá
        # guardado el id de la carta a intercambiar
        jugador_ofrecedor = partida.buscar_jugador(id_objetivo)
        if jugador_ofrecedor.get_id_carta_intercambio() == -1:
            return False
        
        return True
    
    def aplicar(self, id_objetivo: int, partida: Partida):
        #  Sólo altero el objetivo del intercambio, ya que después de realizar
        # el mismo sólo queda terminar el turno (como normalmente)
        jugador_ofrecedor = partida.buscar_jugador(id_objetivo)
        jugador_ofrecedor.set_id_carta_intercambio(-1)
        jugador_ofrecedor.set_id_objetivo_intercambio(-1)        
        return
      
class Analisis(CardEffect):

    def verificar(self, id_carta: int, id_jugador: int, 
                  id_objetivo: int, partida: Partida):
        self.id_jugador = id_jugador        
        # Chequeamos que la carta es analisis y que
        # no se este jugando sobre si mismo
        if id_carta not in range(27, 30) or id_jugador == id_objetivo:
            return False
        
        # Chequeamos que el objetivo este en la partida
        if not partida.buscar_jugador(id_objetivo):
            return False
        
        # Chequeamos que el jugador objetivo sea adyacente
        # y que no haya un bloqueo entre ellos
        # Segun las reglas se puede jugar aun estando en cuarentena
        posicion_jugador : int = partida.buscar_jugador(id_jugador).get_posicion()
        posicion_objetivo : int = partida.buscar_jugador(id_objetivo).get_posicion()

        if not partida.son_adyacentes(posicion_jugador, posicion_objetivo): 
            return False
        if partida.hay_bloqueo(posicion_jugador, posicion_objetivo):
            return False
        # Si llegamos hasta aca se puede juger la carta
        return True 

    def aplicar(self, id_objetivo: int, partida: Partida):
        # Obtenemos el jugador objetivo
        objetivo : Jugador = partida.buscar_jugador(id_objetivo)
        # Obtenemos la mano del objetivo
        mano : list = [
            armador_evento_mostrar_cartas(id=carta.get_id(),
                                          name=carta.get_name(),
                                          type=carta.get_type(),
                                          effectDescription=carta.get_effect()
                                          )
            for carta in objetivo.get_mano()
        ] 
        # Enviamos un evento con la mano del objetivo
        
        partida.post_event(id_jugador = self.id_jugador, 
                           event = armador_evento_mostrar_mano(id_objetivo, mano),
                           event_name = 'Cartas_mostrables'
        )
        return

class Whisky(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int,
                   id_objetivo: int, partida: Partida):
        self.id_jugador = id_jugador
        # Chequeamos que la carta es analisis y que
        # el jugador que juega la carta es el mismo que el objetivo
        if id_carta not in range(40, 43) or not id_jugador == id_objetivo:
            return False
        
        # Chequeamos que el objetivo (jugador que juega la carta ) 
        # este en la partida
        if partida.buscar_jugador(id_jugador) == None:
            return False
        return True

    def aplicar(self, id_objetivo: int, partida: Partida):
        # Obtenemos el jugador objetivo
        objetivo : Jugador = partida.buscar_jugador(id_objetivo)
        # Obtenemos la mano del objetivo
        mano : list = [
            armador_evento_mostrar_cartas(id=carta.get_id(),
                                          name=carta.get_name(),
                                          type=carta.get_type(),
                                          effectDescription=carta.get_effect()
                                          )
            for carta in objetivo.get_mano()
        ] 
        # Enviamos un evento con la mano del objetivo a todos los jugadores
        # RECORDAR EVITAR MOSTRAR LAS CARTAS AL JUGADOR!
        partida.broadcast(msg = armador_evento_mostrar_mano(self.id_jugador, mano),
                        event_name = 'Cartas_mostrables'
        )
        return

class Sospecha(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, 
                  id_objetivo: int, partida: Partida):
        self.id_jugador = id_jugador
        # Chequeamos que la carta es analisis y que
        # no se este jugando sobre si mismo
        if id_carta not in range(32, 40) or id_jugador == id_objetivo:
            return False
        
        # Chequeamos que el objetivo este en la partida
        if not partida.buscar_jugador(id_objetivo):
            return False
        
        # Chequeamos que el jugador objetivo sea adyacente
        # y que no haya un bloqueo entre ellos
        # Segun las reglas se puede jugar aun estando en cuarentena
        posicion_jugador : int = partida.buscar_jugador(id_jugador).get_posicion()
        posicion_objetivo : int = partida.buscar_jugador(id_objetivo).get_posicion()

        if (not partida.son_adyacentes(posicion_jugador, posicion_objetivo) 
            or partida.hay_bloqueo(posicion_jugador, posicion_objetivo)):
            return False

        return True 

    def aplicar(self, id_objetivo: int, partida: Partida):
        # Obtenemos el jugador objetivo
        objetivo : Jugador = partida.buscar_jugador(id_objetivo)
        # Obtenemos la mano del objetivo
        mano : list = [
            armador_evento_mostrar_cartas(id=carta.get_id(),
                                          name=carta.get_name(),
                                          type=carta.get_type(),
                                          effectDescription=carta.get_effect()
                                          )
            for carta in objetivo.get_mano()
        ]
        # Formamos una lista con una carta aleatoria de la mano del objetivo
        carta_aleatoria = random.choice(mano)
        mano = [carta_aleatoria]     
        # Enviamos un evento con la mano del objetivo
        partida.post_event(id_jugador = self.id_jugador, 
                           event = armador_evento_mostrar_mano(id_objetivo, mano),
                           event_name = 'Cartas_mostrables'
        )
        return
    
class Vigila(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):

        if id_carta not in range(48, 50):
            return False
        
        return True

    def aplicar(self, id_objetivo: int, partida: Partida):
        # Cambiamos el orden de la ronda
        partida.set_sentido(not partida.get_sentido())
        # Mandamos un evento de log
        armar_broadcast(_partida_=partida,
                msg=armador_evento_log(context="cambiar_sentido"),
                event_name="Log")
        return  

class Posicion(CardEffect):
    def aplicar(self, id_objetivo: int, partida: Partida):
        # Obtenemos a ambos jugadores
        jugador_turno = partida.buscar_jugador_por_posicion(partida.get_turno())
        jugador_objetivo = partida.buscar_jugador(id_objetivo)

        # Chequeamos por cuarentena. Sirve para el caso de la carta de panico.
        # En caso de que haya, la carta esta bien jugada pero no aplica ningun efecto
        if (not jugador_turno.esta_en_cuarentena() 
            and not jugador_objetivo.esta_en_cuarentena()):

            # Intercambiamos sus posiciones
            pos_aux = jugador_turno.get_posicion()
            jugador_turno.set_posicion(jugador_objetivo.get_posicion())
            jugador_objetivo.set_posicion(pos_aux)
            # Seteamos el turno al jugador que tiene el turno
            partida.set_turno(jugador_turno.get_posicion())
            # Mandamos un evento de log
            armar_broadcast(_partida_=partida,
            msg=armador_evento_log(jugador=jugador_turno, 
                                objetivo=jugador_objetivo,
                                context="cambiar_lugar"),
                                    event_name="Log")
        return
    
class CambioLugar(Posicion):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):

        if id_carta not in range(50, 55):
            return False
        
        if id_jugador == id_objetivo:
            return False
        
        jugador = partida.buscar_jugador(id_jugador)
        objetivo = partida.buscar_jugador(id_objetivo)

        # Obtenemos las posiciones de los jugadores
        posicion_jugador = jugador.get_posicion()
        posicion_objetivo = objetivo.get_posicion()

        # Chequeamos si los jugadores son adyacentes
        if not partida.son_adyacentes(posicion_jugador, posicion_objetivo):
            return False

        # Chequear si el jugador objetivo está en cuarentena
        if partida.buscar_jugador(id_jugador=id_objetivo).esta_en_cuarentena():
            return False
        
        # Chequear por puerta atrancada
        if partida.hay_bloqueo(posicion_jugador, posicion_objetivo):
            return False

        return True
    
class MasValeCorras(Posicion):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):

        if id_carta not in range(55, 60):
            return False
        
        if id_jugador == id_objetivo:
            return False

        # Verificar si el jugador objetivo está en cuarentena
        if partida.buscar_jugador(id_jugador=id_objetivo).esta_en_cuarentena():
            return False

        return True
    
    
class AquiEstoyBien(CardEffect):
    def verificar(self, id_carta:int, id_jugador: int, id_objetivo: int, partida: Partida):
        if id_carta not in range(71, 74):
            return False
        
        # Chequeamos que el jugador está jugando la defensa sobre sí mismo
        if id_jugador != id_objetivo:
            return False
        
        # Chequeamos que la última carta jugada es un cambio de lugar o mas vale corras 
        #  y que el objetivo es el jugador de la carta de defensa
        tupla = partida.desapilar()
        id_carta = tupla[0]
        objetivo = tupla[1]
        partida.apilar(tupla)
        if not (id_carta in range(50, 60) and objetivo == id_jugador):
            return False
        
        return True
    
    def aplicar(self, id_objetivo: int, partida: Partida):
        # Si bien asumimos que verificar() se ha llamado antes
        # para asegurar que el desapilar() es procedente, usamos el
        # id del objetivo para chequear lo desapilado pues el aplicar()
        # puede llamarse independientemente del verificar()
        tupla = partida.desapilar()
        if tupla[1] != id_objetivo:
            partida.apilar(tupla)

class PuertaAtrancada(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int,
                  partida: Partida):

        if id_carta not in range(86, 89):
            return False

        # Chequeamos que el jugador objetivo sea adyacente
        
        jugador: Jugador = partida.buscar_jugador(id_jugador)
        objetivo: Jugador = partida.buscar_jugador(id_objetivo)

        posicion_jugador: int = jugador.get_posicion()
        posicion_objetivo: int = objetivo.get_posicion()
            
        if not partida.son_adyacentes(posicion_jugador, posicion_objetivo):
            return False

        return True
    
    def aplicar(self, id_objetivo: int, partida: Partida):
        
        objetivo: Jugador = partida.buscar_jugador(id_objetivo)
        
        posicion_objetivo: int = objetivo.get_posicion()
        posicion_jugador: int = partida.get_turno()

        num_players = partida.get_num_jugadores()
        difference = abs(posicion_jugador - posicion_objetivo)

        if (posicion_jugador > posicion_objetivo
            and difference == 1):
            partida.bloquear_posicion(posicion_objetivo, 1)
            
        elif (posicion_jugador < posicion_objetivo
              and difference == 1):
            partida.bloquear_posicion(posicion_objetivo, 0)
            
        # Casos bordes
        elif (posicion_jugador > posicion_objetivo
              and difference == num_players - 1):
            partida.bloquear_posicion(posicion_objetivo, 0)

        elif (posicion_jugador < posicion_objetivo
              and difference == num_players - 1):
            partida.bloquear_posicion(posicion_objetivo, 1)

        # Guardamos en played cards antes de descartarla
        mazo = partida.get_mazo()
        mano_jugador = partida.buscar_jugador_por_posicion(posicion_jugador).get_mano()
        for card in mano_jugador:
            if card.get_id() in range(86, 89):
                mazo.play_card(card)
                break

class Hacha(CardEffect):

    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):
        
        if id_carta not in range(30, 32):
            return False

        # Chequeamos que el jugador objetivo sea adyacente
        if id_objetivo >= 100:
            id_objetivo -= 100
        jugador: Jugador = partida.buscar_jugador(id_jugador)
        objetivo: Jugador = partida.buscar_jugador(id_objetivo)

        posicion_jugador: int = jugador.get_posicion()
        posicion_objetivo: int = objetivo.get_posicion()
            
        if not (partida.son_adyacentes(posicion_jugador, posicion_objetivo)
                or id_jugador == id_objetivo):
            return False

        # Chequeamos que exista una puerta atrancada entre ambos jugadores
        # o que el objetivo este en cuarentena
        if not (partida.hay_bloqueo(posicion_jugador, posicion_objetivo)
            or partida.buscar_jugador_por_posicion(posicion_objetivo).esta_en_cuarentena()):
            return False
    
        return True
    
    def aplicar(self, id_objetivo: int, partida: Partida):

        puerta_atrancada: bool = id_objetivo >= 100

        posicion_jugador: int = partida.get_turno()
        new_id_objetivo: int = id_objetivo-100 if puerta_atrancada else id_objetivo
        posicion_objetivo: int = partida.buscar_jugador(new_id_objetivo).get_posicion()

        mazo = partida.get_mazo()

        if puerta_atrancada:
            difference = abs(posicion_jugador - posicion_objetivo)
            if difference == 0:

                partida.desbloquear_posicion(posicion_objetivo, 1)
            
            if (posicion_jugador > posicion_objetivo
                and difference == 1):

                partida.desbloquear_posicion(posicion_objetivo, 1)

            elif (posicion_jugador < posicion_objetivo
                and difference == 1):
                
                partida.desbloquear_posicion(posicion_objetivo, 0)
            
            # Casos bordes
            elif (posicion_jugador > posicion_objetivo
                and difference == partida.get_num_jugadores() - 1):
            
                partida.desbloquear_posicion(posicion_objetivo, 0)
            
            elif (posicion_jugador < posicion_objetivo
                and difference == partida.get_num_jugadores() - 1):
            
                partida.desbloquear_posicion(posicion_objetivo, 1) 

            # Descartamos la carta que esta en juego
            mazo.discard_played_card("Puerta atrancada")
        else:
            partida.buscar_jugador(new_id_objetivo).sacar_de_cuarentena()
            # Descartamos la carta que esta en juego
            mazo.discard_played_card("Cuarentena")

class Aterrador(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):
        
        if id_carta not in range(67, 71):
            return False

        # No se puede jugar en respuesta a otra carta propiamente dicho
        if partida.get_largo_stack() != 0:
            return False
        
        #  Si se inició un intercambio, el jugador que lo hizo tendrá
        # guardado el id de la carta a intercambiar
        jugador_ofrecedor = partida.buscar_jugador(id_objetivo)
        if jugador_ofrecedor.get_id_carta_intercambio() == -1:
            return False
        
        # Guardo el id de quien jugó esta carta para después
        self.id_jugador = id_jugador
        
        return True
    
    def aplicar(self, id_objetivo: int, partida: Partida):
        #  Sólo altero el objetivo del intercambio, ya que después de realizar
        # el mismo sólo queda terminar el turno (como normalmente)
        jugador_ofrecedor = partida.buscar_jugador(id_objetivo)
        
        carta_revelada = jugador_ofrecedor.obtener_carta(jugador_ofrecedor.get_id_carta_intercambio())
        evento_carta_revelada = armador_evento_mostrar_cartas(id=carta_revelada.get_id(),
                                                              name=carta_revelada.get_name(),
                                                              type=carta_revelada.get_type(),
                                                              effectDescription=carta_revelada.get_effect())
        
        partida.post_event(id_jugador=self.id_jugador, 
                           event=armador_evento_mostrar_mano(id_jugador=id_objetivo,
                                                             cartas=[evento_carta_revelada]),
                           event_name="Cartas_mostrables")
        
        jugador_ofrecedor.set_id_carta_intercambio(-1)
        return

class Oops(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int,
                   id_objetivo: int, partida: Partida):
        self.id_jugador = id_jugador
        # Chequeamos que la carta es analisis y que
        # el jugador que juega la carta es el mismo que el objetivo
        if id_carta != 105 or not id_jugador == id_objetivo:
            return False
        
        # Chequeamos que el objetivo (jugador que juega la carta ) 
        # este en la partida
        if partida.buscar_jugador(id_jugador) == None:
            return False
        return True

    def aplicar(self, id_objetivo: int, partida: Partida):
        # Obtenemos el jugador objetivo
        objetivo : Jugador = partida.buscar_jugador(id_objetivo)
        # Obtenemos la mano del objetivo
        mano : list = [
            armador_evento_mostrar_cartas(id=carta.get_id(),
                                          name=carta.get_name(),
                                          type=carta.get_type(),
                                          effectDescription=carta.get_effect()
                                          )
            for carta in objetivo.get_mano()
        ] 
        # Enviamos un evento con la mano del objetivo a todos los jugadores
        # RECORDAR EVITAR MOSTRAR LAS CARTAS AL JUGADOR!
        partida.broadcast(msg = armador_evento_mostrar_mano(self.id_jugador, mano),
                        event_name = 'Cartas_mostrables'
        )
        return

class Fallaste(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):
        if id_carta not in range(78, 81):
            return False

        # No se puede jugar en respuesta a otra carta propiamente dicha
        if partida.get_largo_stack() != 0:
            return False
        
        #  Si se inició un intercambio, el jugador que lo hizo tendrá
        # guardado el id de la carta a intercambiar
        jugador_ofrecedor = partida.buscar_jugador(id_objetivo)
        if jugador_ofrecedor.get_id_carta_intercambio() == -1:
            return False

        self.id_jugador = id_jugador
        return True
    
    def aplicar(self, id_objetivo: int, partida: Partida):
        #  Sólo altero el objetivo del intercambio, después procede
        jugador_defensor = partida.buscar_jugador(self.id_jugador)
        #  Como el defensor no va a tener ningun jugador asignado para
        # intercambiar, puedo usar:
        id_jugador_siguiente = obtener_objetivo_intercambio(partida=partida,
                                                            jugador=jugador_defensor)
        jugador_siguiente = partida.buscar_jugador(id_jugador_siguiente)
        jugador_turno = partida.buscar_jugador_por_posicion(partida.get_turno())
        # Chequeo que no haya un bloqueo con el siguiente jugador siguiente,
        # en caso de que lo haya el intercambio no sucede y termina el turno del jugador en turno
        if (partida.hay_bloqueo(jugador_defensor.get_posicion(), jugador_siguiente.get_posicion())):
                # Mandamos log
                armar_broadcast(_partida_=partida,
                                msg=armador_evento_log(jugador=jugador_turno,
                                                       objetivo=jugador_siguiente,
                                                       context="bloqueo"),
                                event_name="Log")
                # Terminamos el turno
                evento_mano : EventoMano = armador_evento_mano(jugador=jugador_turno,
                                                        instancia="Esperar", 
                                                        context="Fin_Turno")
                partida.post_event(id_jugador=jugador_turno.get_id(), 
                         event=evento_mano, 
                         event_name="Mano")
        else:
            # Caso borde: por Seduccion, el jugador siguiente es el jugador ofrecedor
            if id_jugador_siguiente == id_objetivo:
                jugador_ofrecedor: Jugador = partida.buscar_jugador(id_objetivo)
                id_jugador_siguiente = obtener_objetivo_intercambio(partida=partida,
                                                                    jugador=jugador_ofrecedor)
                
            #  Por último, procedo a hacer los preparativos para que el siguiente
            # jugador en la ronda atienda el pedido de intercambio redirigido
            evento_objetivo = EventoObjetivoIntercambio(id_jugador=id_jugador_siguiente)
            partida.post_event(id_objetivo, evento_objetivo, "Objetivo_intercambio")
            
            evento_pedido_intercambio = EventoPedidoIntercambio(id_jugador=id_objetivo)

            partida.post_event(id_jugador=id_jugador_siguiente, 
                            event=evento_pedido_intercambio, 
                            event_name="Pedido_intercambio")

            # Este nuevo objetivo no puede ser infectado en este intercambio
            jugador_siguiente.set_inmunidad(True)
            evento_mano_intercambiables : EventoMano = armador_evento_mano(jugador=jugador_siguiente,
                                                                        instancia="Intercambiar_Defender",
                                                                        context="Intercambiables_defensa")
            partida.post_event(id_jugador=id_jugador_siguiente, 
                            event=evento_mano_intercambiables, 
                            event_name="Mano")

        return

class UnoDos(Posicion):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):

        if id_carta not in range(91, 93):
            return False

        # Verificamos que el jugador objetivo es el tercero,
        # ya sea a la izquierda o a la derecha
        num_jugadores = partida.get_num_jugadores()
        pos_objetivo = partida.buscar_jugador(id_objetivo).get_posicion()
        pos_jugador = partida.buscar_jugador(id_jugador).get_posicion()

        if ((pos_jugador + 3) % num_jugadores != pos_objetivo and 
            (pos_jugador - 3) % num_jugadores != pos_objetivo):
            return False

        return True

class SoloEntreNosotros(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):
        
        if id_carta not in range(106, 108):
            return False
        
        # Chequeamos que el jugador está jugando la defensa sobre sí mismo
        if id_jugador == id_objetivo:
            return False
        
        # Chequeamos que los jugadores son adyacentes
        jugador: Jugador = partida.buscar_jugador(id_jugador)
        objetivo: Jugador = partida.buscar_jugador(id_objetivo)

        posicion_jugador: int = jugador.get_posicion()
        posicion_objetivo: int = objetivo.get_posicion()

        if not partida.son_adyacentes(posicion_jugador, posicion_objetivo):
            return False
        
        return True
    
    def aplicar(self, id_objetivo: int, partida: Partida):
        
        id_jugador : int = partida.get_turno()
        jugador : Jugador = partida.buscar_jugador(id_jugador)
        mano_jugador = jugador.get_mano()

        mano : list = [
            armador_evento_mostrar_cartas(id=carta.get_id(),
                                          name=carta.get_name(),
                                          type=carta.get_type(),
                                          effectDescription=carta.get_effect()
                                          )
            for carta in mano_jugador
        ]
        # Enviamos un evento con la mano del objetivo

        partida.post_event(id_jugador = id_objetivo,
                            event = armador_evento_mostrar_mano(id_jugador, mano),
                            event_name = 'Cartas_mostrables')
        
        return
    
class AquiFiesta(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):
        if id_carta not in range(95, 97):
            return False
        return True
    
    def aplicar(self, id_objetivo: int, partida: Partida):
        # Descarto todas las cartas de puerta atrancada y cuarentena
        mazo = partida.get_mazo()
        mazo.discard_played_cards()

        # Desbloqueamos todas las posiciones
        partida.desbloquear_posiciones()
        # Sacamos de cuarentena a todos los jugadores
        for each in partida.get_jugadores():
            each.sacar_de_cuarentena()

        # Obtenemos id de jugador en turno
        jugador_turno = partida.buscar_jugador_por_posicion(partida.get_turno())
        # Obtenemos la cantidad de jugadores
        num_jugadores = partida.get_num_jugadores()
        # Contador para intercambios
        i = 0
        # Posicion de donde comienza los intercambios
        pos_actual = partida.get_turno()

        while i < partida.get_num_jugadores() // 2:
            # Buscamos el jugador de pos_actual y su siguiente
            jugador1 = partida.buscar_jugador_por_posicion(pos_actual)
            jugador2 = partida.buscar_jugador_por_posicion((pos_actual+1)%num_jugadores)
            # Intercambiamos sus posiciones
            pos_aux = jugador1.get_posicion()
            jugador1.set_posicion(jugador2.get_posicion())
            jugador2.set_posicion(pos_aux)
            # Mandamos un evento de log
            armar_broadcast(_partida_=partida,
            msg=armador_evento_log(jugador=jugador1, 
                                objetivo=jugador2,
                                context="cambiar_lugar"),
            event_name="Log")

            # Sumamos a i, y la posicion
            i += 1
            pos_actual = (pos_actual + 2) % num_jugadores
        
        # Seteamos el turno al jugador que tiene el turno
        partida.set_turno(jugador_turno.get_posicion())

        
class NoPodemosSerAmigos(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):

        if id_carta not in range(101, 103):
            return False
        
        if id_jugador == id_objetivo:
            return False

        # Verificar si el jugador objetivo está en cuarentena
        if partida.buscar_jugador(id_jugador=id_objetivo).esta_en_cuarentena():
            return False

        return True

    def aplicar(self, id_objetivo: int, partida: Partida):
        #  Sólo altero el objetivo del intercambio, ya que después de realizar
        # el mismo sólo queda terminar el turno (como normalmente)
        jugador = partida.buscar_jugador_por_posicion(partida.get_turno())
        jugador.set_id_objetivo_intercambio(id_objetivo)
        # Necesitamos además incrementar el contador de intercambios del
        # jugador de No Podemos Ser Amigos 
        jugador.añadir_accion("intercambios")
        
class Cuarentena(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):
        return id_carta in range(84,86) and id_jugador != id_objetivo
    
    def aplicar(self, id_objetivo: int, partida: Partida, id_jugador: int = None):
        # Ponemos al jugador objetivo en cuarentena
        jugador_objetivo : Jugador = partida.buscar_jugador(id_objetivo)
        jugador_objetivo.poner_en_cuarentena()

        # Ponemos la carta en la pila de en juego
        jugador : Jugador = partida.buscar_jugador(partida.get_turno())
        mano : List[CardSchema]= jugador.get_mano()
        
        for card in mano:
            if card.get_id() == "Cuarentena":
                partida.get_mazo().play_card(card)
                break            
                
        return

class CuerdasPodridas(CardEffect):
  def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):
      return id_carta in range(89, 91) and id_jugador == id_objetivo
  def aplicar(self, id_objetivo: int, partida: Partida, id_jugador: int = None):
      for jugador in partida.get_jugadores():
          if jugador.esta_en_cuarentena():
              jugador.sacar_de_cuarentena()
      partida.mazo.discard_played_card("Cuarentena")
      
class Revelaciones(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):
        if id_carta != 108:
            return False
        return True
    
    def aplicar(self, id_objetivo: int, partida: Partida):
        # Seteamos listo para intercambio a false
        jugador = partida.buscar_jugador_por_posicion(partida.get_turno())
        jugador.set_listo_para_intercambio(False)

        # Mandamos evento de log
        armar_broadcast(_partida_=partida,
                        msg=armador_evento_log(jugador=jugador, 
                                               message="Comienza ronda de Revelaciones"),
                        event_name="Log")

        # Mandamos evento revelar a jugador en turno
        evento_revelar = EventoRevelar(id_jugador=jugador.get_id())
        partida.post_event(jugador.get_id(), evento_revelar, "Revelar")
      
class CitaCiega(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):
        if not (id_jugador == id_objetivo and id_carta in [103, 104]):
            return False
        
        if partida.get_largo_stack() != 0:
            return False
        
        return True
    
    def aplicar(self, id_objetivo: int, partida: Partida, id_jugador: int = None):
        #  -2 es el caso especial de intercambio con el mazo, que se empieza y resuelve
        # en el mismo endpoint
        jugador = partida.buscar_jugador(id_jugador=id_objetivo)
        jugador.set_id_objetivo_intercambio(-2)
        # Este intercambio especial NO reemplaza/abarca el intercambio de fin de turno
        return


class TresCuatro(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):
        return id_carta in range(93,95)
    def aplicar(self, id_objetivo: int, partida: Partida, id_jugador: int = None):
        # Descarto todas las cartas de puerta atrancada y cuarentena
        mazo = partida.get_mazo()
        mazo.discard_played_card("Puerta atrancada")
        partida.mazo = mazo
        # Desbloqueamos todas las posiciones
        partida.desbloquear_posiciones()


class Olvidadizo(CardEffect):

    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):
        valid = id_carta == 98 and id_jugador == id_objetivo
        return valid
    
    def aplicar(self, id_objetivo: int, partida: Partida, id_jugador: int = None):
        jugador = partida.buscar_jugador(id_objetivo)
        jugador.set_accion("robos", 3)
        jugador.set_accion("descartes", 3)
        jugador.set_listo_para_intercambio(False)
        evento_descarte = armador_evento_mano(jugador=jugador, 
                                        instancia="Descartar", 
                                        context="Descartables")
        partida.post_event(id_jugador=id_objetivo, event=evento_descarte, event_name="Mano")
        return

class VueltaYVuelta(CardEffect):
    def verificar(self, id_carta: int, id_jugador: int, id_objetivo: int, partida: Partida):
        valid = (id_carta in [99, 100] and id_jugador == id_objetivo)
        return valid
    
    def aplicar(self, id_objetivo: int, partida: Partida, id_jugador: int = None):
        
        #  Mandar a cada jugador su respectiva mano para el intercambio, con contexto "Vuelta_y_vuelta"
        jugadores: List[Jugador] = partida.obtener_jugadores()
        for each in jugadores:
            mano_vueltera: EventoMano = armador_evento_mano(each, "Intercambiar", "Vuelta_y_vuelta")
            partida.post_event(each.get_id(), mano_vueltera, "Mano")
        
        # El resto se debe resolver en el nuevo endpoint

        #  El jugador no procede al intercambio normal, sino que resuelve el efecto y
        # termina su turno
        jugador_turno: Jugador = partida.buscar_jugador_por_posicion(partida.get_turno())
        jugador_turno.set_listo_para_intercambio(False)
        
        return
