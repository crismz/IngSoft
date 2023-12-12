from typing import List
from partidas.utils import armador_evento_mostrar_mano, armador_evento_mostrar_cartas
from partidas.schema import Partida
from partidas.mazo.schema import Mazo
from partidas.mazo.cartas.schema import CardSchema
from partidas.jugadores.schema import Jugador
from partidas.croupier.efectos import *

# El patrón de diseño utilizado es el de Strategy,
# que permite asociar algoritmos a claves y aplicarlos
# en tandem según sea necesario. Esto debería cambiarse
# si a la larga resulta demasiado trabajoso mantener este
# diseño. Para más info:
# https://refactoring.guru/design-patterns/strategy

class Croupier():
    def __init__(self, partida: Partida):
        self.efectos = {}
        self.stack = []
        self.partida = partida
        quemar_range = range(22, 27)
        for each in quemar_range:
            self.efectos[each] = Quemar()
        extintor_range = range(81, 84)
        for each in extintor_range:
            self.efectos[each] = Extintor()
        analisis_range = range(27,30)
        for each in analisis_range:
            self.efectos[each] = Analisis()
        whisky_range = range(40,43)
        for each in whisky_range:
            self.efectos[each] = Whisky()
        sospecha_range = range(32, 40)
        for each in sospecha_range:
            self.efectos[each] = Sospecha()
        seduccion_range = range(60, 67)
        for each in seduccion_range:
            self.efectos[each] = Seducir()
        no_gracias_range = range(74, 78)
        for each in no_gracias_range:
            self.efectos[each] = NoGracias()
        vigila_range = range(48,50)
        for each in vigila_range:
            self.efectos[each] = Vigila()
        cambio_lugar_range = range(50, 55)
        for each in cambio_lugar_range:
            self.efectos[each] = CambioLugar()
        mas_vale_corras_range = range(55, 60)
        for each in mas_vale_corras_range:
            self.efectos[each] = MasValeCorras()
        puerta_atrancada_range = range(86, 89)
        for each in puerta_atrancada_range:
            self.efectos[each] = PuertaAtrancada()
        hacha_range = range(30, 32)
        for each in hacha_range:
            self.efectos[each] = Hacha()
        aqui_estoy_bien_range = range(71,74)
        for each in aqui_estoy_bien_range:
            self.efectos[each] = AquiEstoyBien()
        aterrador_range = range(67, 71)
        for each in aterrador_range:
            self.efectos[each] = Aterrador()
        self.efectos[105] = Oops()
        fallaste_range= range(78, 81)
        for each in fallaste_range:
            self.efectos[each] = Fallaste()
        uno_dos_range = range(91, 93)
        for each in uno_dos_range:
            self.efectos[each] = UnoDos()
        solo_entre_nosotros_range = range(106, 108)
        for each in solo_entre_nosotros_range:
            self.efectos[each] = SoloEntreNosotros()
        fiesta_range = range(95,97)
        for each in fiesta_range:
            self.efectos[each] = AquiFiesta()
        for each in range(84,86):
            self.efectos[each] = Cuarentena()
        for each in range(89, 91):
            self.efectos[each] = CuerdasPodridas()
        self.efectos[108] = Revelaciones()
        for each in [103, 104]:
            self.efectos[each] = CitaCiega()
        amigos_range = range(101,103)
        for each in amigos_range:
            self.efectos[each] = NoPodemosSerAmigos() 
        tres_cuatro_range = range(93,95)
        for each in tres_cuatro_range:
            self.efectos[each] = TresCuatro()
        self.efectos[98] = Olvidadizo()
        for each in [99, 100]:
            self.efectos[each] = VueltaYVuelta()
        

    def carta_es_defendible(self, id_carta: int) -> bool:
        # Lista que incluye todas las cartas que tienen una carta de Defensa que las anula
        # NOTA: FALTAN LAS CARTAS DE PÁNICO "defendibles"
        check_list = [
            22, 23, 24, 25, 26, 
            50, 51, 52, 53, 54,
            55, 56, 57, 58, 59
        ]
        return id_carta in check_list

    def descartar(self, id_carta: int, id_jugador: int):
        owner = self.partida.buscar_jugador(id_jugador)
        mazo = self.partida.get_mazo()
        card = owner.remover_carta_mano(id_carta)
        mazo.discard_card(card)

        if owner.esta_en_cuarentena():
            cards = [armador_evento_mostrar_cartas(
                card.get_id(), card.get_name(), card.get_type(), card.get_effect()
            )]
            self.partida.broadcast(
                msg=armador_evento_mostrar_mano(id_jugador, cards),
                event_name="Cartas_mostrables"
            )
        
    def poner_en_juego(self, id_carta: int, id_jugador: int):
        owner = self.partida.buscar_jugador(id_jugador)
        mazo = self.partida.get_mazo()
        card = owner.remover_carta_mano(id_carta)
        mazo.play_card(card)

    def verificar_efecto(self, id_carta: int, id_jugador: int, id_objetivo: int):
        if id_carta in self.efectos:
            efecto = self.efectos[id_carta]
            resultado = efecto.verificar(id_carta, id_jugador, id_objetivo, self.partida)
            return resultado
        else:
            # El efecto no está en el diccionario del Croupier.
            # Luego esa carta no aplicará efectos, solamente
            # se descartará
            return True

    def aplicar_efecto(self, id_carta:int, id_objetivo: int):
        # El efecto puede aplicarse si está en el diccionario de efectos del Croupier.
        if id_carta in self.efectos:
            # Esto hay que cambiarlo para añadir el stack de ejecución
            efecto = self.efectos[id_carta]
            efecto.aplicar(id_objetivo,self.partida)
        # Si el efecto no está en el diccionario de efectos del Croupier, la carta no
        # surtirá efectos
        
    def stack_card(self, id_carta: int, id_jugador:int, id_objetivo: int):
        self.partida.apilar((id_carta, id_objetivo))
        # Si la carta es puerta atrancada o cuarentena se pone en juego
        if(id_carta in range(84,89)):
            self.poner_en_juego(id_carta, id_jugador)
        else:
            self.descartar(id_carta, id_jugador)

    def execute_stack(self):
        while self.partida.get_largo_stack() != 0:
            tupla = self.partida.desapilar()
            self.aplicar_efecto(tupla[0], tupla[1])

# Los efectos deberían moverse a un archivo aparte cuando crezcan en
# número. Ello implica que tendremos que cambiar la manera en que se
# agregan al diccionario del Croupier.

class DiccionarioCroupier():
    diccionario: dict[int, Croupier] = {}

    def append(self, partida: Partida) -> None:
        id : int = partida.get_id()
        croupier : Croupier = Croupier(partida)
        self.diccionario[id] = croupier
    
    def remove(self, id: int) -> None:
        del self.diccionario[id]
    
    def get_length(self) -> int:
        return len(self.diccionario)
    
    def get_croupier(self, index: int) -> Croupier:
        if index < 0:
            return None
        return self.diccionario[index]
    