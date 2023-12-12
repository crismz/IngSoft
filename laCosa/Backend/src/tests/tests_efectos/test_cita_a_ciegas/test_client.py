import sys
sys.path.append("../../..")
from fastapi.testclient import TestClient
from main_test import lista_jugadores, app, partida_ejemplo
from partidas.mazo.cartas.schema import CardSchema

client = TestClient(app=app)

def test_play():
    response = client.put(url="/partidas/0/jugadores/0/jugar", 
                          json={"id_carta": 103,
                                "id_objetivo": 0})
    
    assert response.status_code == 200
    response = client.patch(url="/partidas/0/jugadores/0/intercambiar",
                            json={"id_carta": 1000})
    
    assert response.status_code == 200

    player_hand = lista_jugadores[0].get_mano()
    assert len(player_hand) == 1

    assert player_hand[0].get_name() != "Ironclads_card"

    assert player_hand[0].get_type() != "Panico"

    assert partida_ejemplo.get_mazo().take_card() == CardSchema(id=1000, 
                                                                num_players=1, 
                                                                type="Any", 
                                                                name="Ironclads_card", 
                                                                effect="Bore you to death", 
                                                                target="self")