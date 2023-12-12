import sys
sys.path.append("../../..")
from tests.test_mazo import main_test
from pony.orm import db_session, select
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.schema import CardSchema
from partidas.mazo.cartas.db import db

def test_cards_not_null_and_quantity():
    with db_session:
        assert select(c for c in Card if c != None).count() == 103

def test_cards_fields_not_null():
    with db_session:
        assert select(c for c in Card if (c.id != None and 
                                          c.name != None and 
                                          c.type != None and
                                          c.num_players != None and
                                          c.effect != None and
                                          c.target != None)).count() == 103

def test_cards_quantity_per_type():
    with db_session:
        assert (
            select(c for c in Card if c.type == "Accion").count() == 40 and
            select(c for c in Card if c.type == "Defensa").count() == 17 and
            select(c for c in Card if c.type == "Contagio").count() == 21 and
            select(c for c in Card if c.type == "Obstaculo").count() == 5 and
            select(c for c in Card if c.type == "Panico").count() == 19 and
            # La carta misteriosa
            select(c for c in Card if c.type == "?").count() == 1            
        )

def test_cardschema_is_created():
    with db_session:
        cards : list[CardSchema] = [
            CardSchema(
                id=card.id,
                num_players=card.num_players,
                type=card.type,
                name=card.name,
                effect=card.effect,
                target=card.target
            ) for card in select(c for c in Card)
        ]
        for card in cards:
            assert (
                card is not None and
                card.id is not None and
                card.num_players is not None and
                card.type is not None and
                card.name is not None and
                card.effect is not None and
                card.target in ["any", "neighbour", "self", 
                                "quarantine_door", "direction"]
            )
        assert len(cards) == 103