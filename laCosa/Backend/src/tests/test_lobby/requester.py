import sys
import requests as req

chat_input_malo_id_jugador = {
    "mensaje": "How did I end up here?"
}

chat_input_malo_mensaje = {
    "id_jugador": 0,
}

chat_input_muy_largo ={
    "id_jugador" : 0, 
    "mensaje": "But do we see respectable psychologists, \
        philosophers and clergymen boldly descending into \
        those odd and sometimes malodorous wells, at the \
        bottom of which poor Truth is so often condemned \
        to sit? Yet once more the answer is, No."
}

def case_chat_input_malo():
    response = req.post(url="http://localhost:8000/partidas/0/chat", 
                    json=chat_input_malo_id_jugador)
    assert response.status_code == 422

    response = req.post(url="http://localhost:8000/partidas/0/chat", 
                    json=chat_input_malo_mensaje)
    assert response.status_code == 422
    print("\t* 'case_chat_input_malo' passed")


def case_chat_partida_inexistente():
    response = req.post(url="http://localhost:8000/partidas/43/chat", 
                    json=chat_input_muy_largo)
    assert response.status_code == 404
    print("\t* 'case_chat_partida_inexistente' passed")

def case_chat_mensaje_muy_largo():
    response = req.post(url="http://localhost:8000/partidas/0/chat", 
                    json=chat_input_muy_largo)
    assert response.status_code == 413
    print("\t* 'case_chat_mensaje muy largo' passed")

def case_every_failure():
    print("*****Testing every failure testcase*****")
    case_chat_input_malo()
    case_chat_partida_inexistente()
    case_chat_mensaje_muy_largo()
    print("*****All failure testcases passed*****")

def case_correct_message(jugador: int):
    chat_input_correcto = {
    "id_jugador" : jugador, 
    "mensaje": "The simple truth is that interstellar distances will not fit into the human imagination."
    }
    response = req.post(url="http://localhost:8000/partidas/0/chat", 
                    json=chat_input_correcto)
    assert response.status_code == 200

def case_every_correct_message():
    print("*****Testing every correct message testcase*****")
    for each in range(0,4):
        case_correct_message(each)
    print("*****All correct messages testcases passed*****")

def case_chat_tests():
    case_every_failure()
    case_every_correct_message()

def case_trigger_match():
    print("*****Testing match start trigger testcase*****")
    response = req.patch(url="http://localhost:8000/partidas/0/jugadores/0/send_events")
    assert response.status_code == 200
    print("*****Match start trigger testcase passed*****")

def case_trigger_death(jugador: int):
    response = req.delete(url=f"http://localhost:8000/partidas/0/jugadores/{jugador}/send_events")
    assert response.status_code == 200

def case_trigger_every_death():
    print("*****Testing every death trigger testcase*****")
    for each in range(0,4):
        case_trigger_death(each)
    print("*****All death trigger testcases passed*****")

# Cada caso del requester DEBE correrse con corridas independientes del server

reqs_dict = {"0": case_chat_tests,
             "1": case_trigger_match,
             "2": case_trigger_every_death}

if __name__ == "__main__":
    func = reqs_dict.get(sys.argv[1])
    func()