from fastapi.testclient import TestClient
from main_test import CardSchema, app, lista_jugadores

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

    lista_jugadores[1].agregar_carta_mano(CardSchema(id=79, 
                                                    num_players=4, 
                                                    type="Defensa", 
                                                    name="¡Fallaste!", 
                                                    effect="El siguiente jugador despues de ti realiza el intercamibio \
                                                        de cartas en lugar de hacerlo tu. No queda Infectado si recibe \
                                                        una carta \"¡Infectado!\". Roba una carta \"¡Alejate!\" en \
                                                        sustitucion de ésta.", 
                                                    target="self"))

    lista_jugadores[2].agregar_carta_mano(CardSchema(id=102, 
                                                    num_players=1, 
                                                    type="Any", 
                                                    name="Defects_card", 
                                                    effect="Bore you to death", 
                                                    target="self"))

    return


client = TestClient(app)

def test_fuera_de_intercambio():
    reiniciar_manos()
    response = client.put(url="http://localhost:8000/partidas/0/jugadores/1/defensa_intercambio", 
                         json={"id_carta" : 79})
    assert response.status_code == 400

#####################################################################

def test_jugada_valida_normal():
    reiniciar_manos()
    response = client.patch(url="http://localhost:8000/partidas/0/jugadores/0/intercambiar", 
                            json={"id_carta" : 100})
    assert response.status_code == 200

    response = client.put(url="http://localhost:8000/partidas/0/jugadores/1/defensa_intercambio", 
                          json={"id_carta" : 79})
    assert response.status_code == 200
    assert lista_jugadores[2].get_inmunidad()

    response = client.patch(url="http://localhost:8000/partidas/0/jugadores/2/resolver_intercambio", 
                            json={"id_carta" : 102})
    assert response.status_code == 200
    assert not lista_jugadores[2].get_inmunidad()

    # Resultados
    assert lista_jugadores[0].tiene_en_mano(102)
    assert lista_jugadores[2].tiene_en_mano (100)
    assert lista_jugadores[1].get_mano() == []
    return

#####################################################################

def test_jugada_valida_con_infeccion_negada():
    reiniciar_manos()
    response = client.patch(url="http://localhost:8000/partidas/0/jugadores/0/intercambiar", 
                            json={"id_carta" : 11})

    response = client.put(url="http://localhost:8000/partidas/0/jugadores/1/defensa_intercambio", 
                          json={"id_carta" : 79})
    assert response.status_code == 200

    response = client.patch(url="http://localhost:8000/partidas/0/jugadores/2/resolver_intercambio", 
                            json={"id_carta" : 102})
    assert response.status_code == 200
    
    # Resultados
    assert lista_jugadores[0].tiene_en_mano(102)
    assert lista_jugadores[2].tiene_en_mano (11) and lista_jugadores[2].get_rol() == "Humano"
    assert lista_jugadores[1].get_mano() == []

    return

#####################################################################