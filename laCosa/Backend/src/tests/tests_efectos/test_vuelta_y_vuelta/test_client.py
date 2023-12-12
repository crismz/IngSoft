import sys
sys.path.append("../../..")
from fastapi.testclient import TestClient
from main_test import app, partida_ejemplo, lista_jugadores
from partidas.mazo.cartas.schema import CardSchema

def reiniciar_manos():
    for each in lista_jugadores:
        _ = each.remover_mano()
    # Mano jugador con id = 0
    lista_jugadores[0].agregar_carta_mano(CardSchema(id=99, 
                                                    num_players=4, 
                                                    type="Panico", 
                                                    name="Vuelta y vuelta", 
                                                    effect="Todos los jugadores deben darle 1 carta al \
                                                        siguiente jugador que tengan al lado, simultaneamente \
                                                        y en el sentido de juego actual, ignorando cualquier \
                                                        carta \"Puerta atrancada\" y \"Cuarentena\" que haya en juego. \
                                                        No puedes usar ninguna carta para evitar este intercambio. \
                                                        La Cosa puede infectar a otro jugador de esta forma, \
                                                        pasandole una carta \"¡Infectado!\". Tu turno termina.", 
                                                    target="self"))

    lista_jugadores[0].agregar_carta_mano(CardSchema(id=11,
                                                    num_players=4,
                                                    type="Contagio",
                                                    name="Infectado",
                                                    effect="Si recibes esta carta de otro jugador quedas \
                                                        infectado y debes quedarte esta carta hasta el final\
                                                        de la partida",
                                                    target="self"))

    # Mano jugador con id = 1
    lista_jugadores[1].agregar_carta_mano(CardSchema(id=1001, 
                                                    num_players=1, 
                                                    type="Any", 
                                                    name="Silents_card", 
                                                    effect="*Sigh*", 
                                                    target="self"))

    # Mano jugador con id = 2
    lista_jugadores[2].agregar_carta_mano(CardSchema(id=1002, 
                                                    num_players=1, 
                                                    type="Any", 
                                                    name="Defects_card", 
                                                    effect="*Sigh*", 
                                                    target="self"))

    lista_jugadores[2].agregar_carta_mano(CardSchema(id=12,
                                                    num_players=4,
                                                    type="Contagio",
                                                    name="Infectado",
                                                    effect="Si recibes esta carta de otro jugador quedas \
                                                        infectado y debes quedarte esta carta hasta el final\
                                                        de la partida",
                                                    target="self"))

    # Mano jugador con id = 3
    lista_jugadores[3].agregar_carta_mano(CardSchema(id=1003, 
                                                    num_players=1, 
                                                    type="Any", 
                                                    name="Neows_card", 
                                                    effect="*Sigh*", 
                                                    target="self"))
    return

client = TestClient(app)

def test_objetivo_invalido():
    reiniciar_manos()
    response = client.put(url="/partidas/0/jugadores/0/jugar", 
                          json={"id_carta": 99,
                                "id_objetivo": 1})
    assert response.status_code == 400

########################################################################

def test_entregar_carta_invalida():
    reiniciar_manos()
    response = client.put(url="/partidas/0/jugadores/0/jugar", 
                          json={"id_carta": 99,
                                "id_objetivo": 0})
    assert response.status_code == 200

    # Un Infectado trata de darle una carta de Contagio a un Humano
    response = client.patch(url="/partidas/0/jugadores/2/vuelta_y_vuelta", 
                          json={"id_carta": 12})
    assert response.status_code == 400

########################################################################

def test_jugada_valida():
    reiniciar_manos()
    response = client.put(url="/partidas/0/jugadores/0/jugar", 
                          json={"id_carta": 99,
                                "id_objetivo": 0})
    assert response.status_code == 200
    
    # Jugador id = 0
    response = client.patch(url="/partidas/0/jugadores/0/vuelta_y_vuelta", 
                          json={"id_carta": 11})
    assert response.status_code == 200
    
    # Jugador id = 1
    response = client.patch(url="/partidas/0/jugadores/1/vuelta_y_vuelta", 
                          json={"id_carta": 1001})
    assert response.status_code == 200

    # Jugador id = 2
    response = client.patch(url="/partidas/0/jugadores/2/vuelta_y_vuelta", 
                          json={"id_carta": 1002})
    assert response.status_code == 200

    # Jugador id = 3
    response = client.patch(url="/partidas/0/jugadores/3/vuelta_y_vuelta", 
                          json={"id_carta": 1003})
    assert response.status_code == 200

    # Resultados
    for each in lista_jugadores:
        if each.get_id() == 2:
            assert len(each.get_mano()) == 2
        else:
            assert len(each.get_mano()) == 1
    assert lista_jugadores[0].tiene_en_mano(1003)
    assert (lista_jugadores[1].tiene_en_mano(11) and 
            lista_jugadores[1].get_rol() == "Infectado")
    assert lista_jugadores[2].tiene_en_mano(1001)
    assert lista_jugadores[3].tiene_en_mano(1002)
    assert partida_ejemplo.jugadores_listos == 0

    return

########################################################################