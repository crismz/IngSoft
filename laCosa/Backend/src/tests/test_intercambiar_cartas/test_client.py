import sys
sys.path.append("../../..")
from fastapi.testclient import TestClient
from main_test import app, lista_jugadores, partida_ejemplo
from partidas.mazo.cartas.schema import CardSchema

def reiniciar_manos():
    _ = lista_jugadores[0].remover_mano()
    _ = lista_jugadores[1].remover_mano()
    _ = lista_jugadores[2].remover_mano()
    lista_jugadores[0].agregar_carta_mano(CardSchema(id=100, 
                                                 num_players=1, 
                                                 type="Any", 
                                                 name="Ironclads_card", 
                                                 effect="Bore you to death", 
                                                 target="self"))

    lista_jugadores[0].agregar_carta_mano(CardSchema(id=11,
                                                    num_players=4,
                                                    type="Contagio",
                                                    name="Infectado",
                                                    effect="Si recibes esta carta de otro jugador quedas \
                                                        infectado y debes quedarte esta carta hasta el final\
                                                        de la partida",
                                                    target="self"))

    lista_jugadores[1].agregar_carta_mano(CardSchema(id=101, 
                                                    num_players=1, 
                                                    type="Any", 
                                                    name="Silents_card", 
                                                    effect="Bore you to death", 
                                                    target="self"))

    lista_jugadores[2].agregar_carta_mano(CardSchema(id=102, 
                                                    num_players=1, 
                                                    type="Any", 
                                                    name="Defects_card", 
                                                    effect="Bore you to death", 
                                                    target="self"))
    
    lista_jugadores[3].agregar_carta_mano(CardSchema(id=12,
                                                    num_players=4,
                                                    type="Contagio",
                                                    name="Infectado",
                                                    effect="Si recibes esta carta de otro jugador quedas \
                                                        infectado y debes quedarte esta carta hasta el final\
                                                        de la partida",
                                                    target="self"))
    
    lista_jugadores[3].agregar_carta_mano(CardSchema(id=13,
                                                    num_players=4,
                                                    type="Contagio",
                                                    name="Infectado",
                                                    effect="Si recibes esta carta de otro jugador quedas \
                                                        infectado y debes quedarte esta carta hasta el final\
                                                        de la partida",
                                                    target="self"))

    return

def reiniciar_roles():
    lista_jugadores[1].set_rol("Humano")
    lista_jugadores[2].set_rol("Humano")

client = TestClient(app)

def test_intercambio_normal():
    reiniciar_manos()
    reiniciar_roles()

    jugador_0 = lista_jugadores[0]
    jugador_1 = lista_jugadores[1]

    response = client.patch(url="http://localhost:8000/partidas/0/jugadores/0/intercambiar", 
                            json={"id_carta" : 100})
    assert response.status_code == 200
    assert jugador_0.get_id_carta_intercambio() == 100

    response = client.patch(url="http://localhost:8000/partidas/0/jugadores/1/resolver_intercambio", 
                            json={"id_carta" : 101})
    assert response.status_code == 200

    # Resultados
    assert jugador_0.tiene_en_mano(101) and jugador_0.tiene_en_mano(11) and len(jugador_0.get_mano()) == 2
    assert jugador_1.tiene_en_mano(100) and len(jugador_1.get_mano()) == 1
    return

def test_intercambio_infeccioso():
    reiniciar_manos()
    reiniciar_roles()

    jugador_0 = lista_jugadores[0]
    jugador_1 = lista_jugadores[1]

    response = client.patch(url="http://localhost:8000/partidas/0/jugadores/0/intercambiar", 
                            json={"id_carta" : 11})
    assert response.status_code == 200
    assert jugador_0.get_id_carta_intercambio() == 11

    response = client.patch(url="http://localhost:8000/partidas/0/jugadores/1/resolver_intercambio", 
                            json={"id_carta" : 101})
    assert response.status_code == 200
    
    # Resultados
    assert jugador_0.tiene_en_mano(101) and jugador_0.tiene_en_mano(100) and len(jugador_0.get_mano()) == 2
    assert jugador_1.tiene_en_mano(11) and len(jugador_1.get_mano()) == 1
    assert jugador_1.get_rol() == "Infectado"
    return

def test_intercambio_infectado_cosa():
    reiniciar_manos()
    reiniciar_roles()
    partida_ejemplo.set_turno(3)

    jugador_0 = lista_jugadores[0]
    jugador_3 = lista_jugadores[3]
    response = client.patch(url="http://localhost:8000/partidas/0/jugadores/3/intercambiar", 
                            json={"id_carta" : 12})
    assert response.status_code == 200
    assert jugador_3.get_id_carta_intercambio() == 12

    response = client.patch(url="http://localhost:8000/partidas/0/jugadores/0/resolver_intercambio", 
                            json={"id_carta" : 100})
    assert response.status_code == 200

    # Resultados
    assert jugador_0.get_rol() == "La Cosa" and jugador_0.tiene_en_mano(12)
    assert jugador_3.get_rol() == "Infectado" and jugador_3.tiene_en_mano(100)

    partida_ejemplo.set_turno(0)
    return

def test_intercambio_infectado_invalido():
    reiniciar_manos()
    reiniciar_roles()
    partida_ejemplo.set_turno(2)

    jugador_2 = lista_jugadores[2]

    response = client.patch(url="http://localhost:8000/partidas/0/jugadores/2/intercambiar", 
                            json={"id_carta" : 102})
    assert response.status_code == 200
    assert jugador_2.get_id_carta_intercambio() == 102

    response = client.patch(url="http://localhost:8000/partidas/0/jugadores/3/resolver_intercambio", 
                            json={"id_carta" : 12})
    assert response.status_code == 400

    return