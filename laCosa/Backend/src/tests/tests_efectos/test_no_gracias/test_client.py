import sys
sys.path.append("../../..")
from fastapi.testclient import TestClient
from main_test import app, lista_jugadores
from partidas.mazo.cartas.schema import CardSchema

def reiniciar_manos():
    _ = lista_jugadores[0].remover_mano()
    _ = lista_jugadores[1].remover_mano()
    lista_jugadores[0].agregar_carta_mano(CardSchema(id=77, 
                                                    num_players=4, 
                                                    type="Defensa", 
                                                    name="¡No, gracias!", 
                                                    effect="Niegate a un ofrecimiento de intercambio de cartas. \
                                                        Roba 1 carta \"¡Alejate!\" en sustitucion de ésta.", 
                                                    target="any"))
    lista_jugadores[0].agregar_carta_mano(CardSchema(id=100, 
                                                    num_players=1, 
                                                    type="Any", 
                                                    name="Ironclads_card", 
                                                    effect="Bore you to death", 
                                                    target="self"))

    lista_jugadores[1].agregar_carta_mano(CardSchema(id=101, 
                                                    num_players=1, 
                                                    type="Any", 
                                                    name="Silents_card", 
                                                    effect="Bore you to death", 
                                                    target="self"))


client = TestClient(app)

# Caso fuera del intercambio
def test_fuera_del_intercambio():
    reiniciar_manos()
    response = client.put(url="http://localhost:8000/partidas/0/jugadores/0/defensa_intercambio", 
                         json={"id_carta" : 77})
    assert response.status_code == 400

# Caso defensa exitosa
def test_jugada_valida():
    reiniciar_manos()
    response = client.patch(url="http://localhost:8000/partidas/0/jugadores/1/intercambiar", 
                         json={"id_carta" : 101})
    assert response.status_code == 200

    response = client.put(url="http://localhost:8000/partidas/0/jugadores/0/defensa_intercambio", 
                         json={"id_carta" : 77})
    assert response.status_code == 200

    assert lista_jugadores[0].get_mano() == [CardSchema(id=100, 
                                                        num_players=1, 
                                                        type="Any", 
                                                        name="Ironclads_card", 
                                                        effect="Bore you to death", 
                                                        target="self")]

    assert lista_jugadores[1].get_mano() == [CardSchema(id=101, 
                                                        num_players=1, 
                                                        type="Any", 
                                                        name="Silents_card", 
                                                        effect="Bore you to death", 
                                                        target="self")]
    
    assert lista_jugadores[1].get_id_carta_intercambio() == -1