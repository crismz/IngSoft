import random
from pydantic import BaseModel 
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.schema import CardSchema
from pony.orm import db_session, select

class Mazo(BaseModel):
    id_partida: int = 0
    cards: list[CardSchema] = []
    discarded_cards: list[CardSchema] = []
    played_cards: list[CardSchema] = []

    def create_deck(self, id_partida: int, number_of_players: int):
        self.id_partida = id_partida
        self.cards = []
        self.discarded_cards = []
        aux : list[CardSchema] = []
        cosa: list[CardSchema] = []

        with db_session:

            cards = select(c for c in Card if c.num_players <= number_of_players)
            
            for card in cards:
                # Ponemos las cartas a repartir en la lista del mazo 
                if card.id == 1:
                    cosa.append(CardSchema(id=card.id,name=card.name,type=card.type,
                            num_players=card.num_players,effect=card.effect,target=card.target))
                # El resto de cartas las ponemos en una lista auxiliar
                elif card.type == "Panico":
                    aux.append(CardSchema(id=card.id,name=card.name,type=card.type,
                            num_players=card.num_players,effect=card.effect,target=card.target))
                elif card.name == "Infectado":
                    aux.append(CardSchema(id=card.id,name=card.name,type=card.type,
                                                 num_players=card.num_players,effect=card.effect,target=card.target))
                else:
                    self.cards.append(CardSchema(id=card.id,name=card.name,type=card.type,
                            num_players=card.num_players,effect=card.effect,target=card.target))
            
        # Mezclamos ambas listas
        self.shuffle_cards()
        random.shuffle(aux)
        # Concatenamos
        self.cards = cosa + self.cards + aux

    def swap(self, i: int, j: int) -> None:
        self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    def len(self) -> int:
        return len(self.cards)

    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def take_card(self) -> CardSchema:
        if len(self.cards) == 0:
            self.reshuffle()
        return self.cards.pop(0)

    def discard_card(self, card : CardSchema):
        self.discarded_cards.append(card)

    def play_card(self, card : CardSchema):
        self.played_cards.append(card)

    def discard_played_card(self, name: str):
        for card in self.played_cards:
            if card.name == name:
                self.discarded_cards.append(card)
                self.played_cards.remove(card)
                return
    
    def discard_played_cards(self):
        for card in self.played_cards:
            self.discarded_cards.append(card)
        self.played_cards = []

    def shuffle_cards(self):
        random.shuffle(self.cards)

    def get_first_card_type(self):
        if len(self.cards) == 0:
            self.reshuffle()
        return self.cards[0].get_type()

    def reshuffle(self):
        if len(self.cards) != 0:
            return
        random.shuffle(self.discarded_cards)
        self.cards = self.discarded_cards
        self.discarded_cards = []

    def place_on_top(self, card: CardSchema):
        self.cards.insert(0, card)
        return

class RoboIn(BaseModel):
    id_jugador: int
    robo_inicio_turno: bool
    

class RoboOut(BaseModel):
    id_carta: int
    tipo_carta: str
    descripcion_carta: str
    nombre_carta: str