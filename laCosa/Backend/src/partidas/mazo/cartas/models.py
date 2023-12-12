from pony.orm import Required, PrimaryKey, Optional

from partidas.mazo.cartas.db import db

class Card(db.Entity):
    id =  PrimaryKey(int)
    num_players = Required(int)
    type = Required(str)
    name = Required(str)
    effect = Required(str)
    target = Optional(str)