from pony.orm import Optional, PrimaryKey, Required

from partidas.dbPartida import db

"""
Representa una partida

"""
 
class PartidaDB(db.Entity):
    partida_id = PrimaryKey(int, auto=True) 
    nombre = Required(str)
    contraseña = Optional(str)
    max_jugadores = Required(int)
    min_jugadores = Required(int)
    iniciada = Required(bool)


# Conecta a la base de datos SQLite en el archivo 'database.sqlite'
db.bind(provider='sqlite', filename="dbPartida.sqlite", create_db=True)

# Genera las tablas en la base de datos
db.generate_mapping(create_tables=True)