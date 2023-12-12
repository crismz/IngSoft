from pony.orm import db_session
from random import randint

from partidas.mazo.cartas.models import Card

def populate_with_cards():
    all_cards = [
        (1, "La cosa", "Contagio", 1, "La cosa", "self"),
        (2, "Infectado", "Contagio", 4, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (3, "Infectado", "Contagio", 4, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (4, "Infectado", "Contagio", 4, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (5, "Infectado", "Contagio", 4, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (6, "Infectado", "Contagio", 4, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (7, "Infectado", "Contagio", 4, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (8, "Infectado", "Contagio", 4, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (9, "Infectado", "Contagio", 4, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (10, "Infectado", "Contagio", 6, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (11, "Infectado", "Contagio", 6, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (12, "Infectado", "Contagio", 7, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (13, "Infectado", "Contagio", 7, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (14, "Infectado", "Contagio", 8, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (15, "Infectado", "Contagio", 9, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (16, "Infectado", "Contagio", 9, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (17, "Infectado", "Contagio", 10, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (18, "Infectado", "Contagio", 10, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (19, "Infectado", "Contagio", 11, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (20, "Infectado", "Contagio", 11, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (21, "Infectado", "Contagio", 11, "Si recibes esta carta de otro jugador quedas "\
         "infectado y debes quedarte esta carta hasta el final de la partida", "self"),
        (22, "Lanzallamas", "Accion", 4, "Elimina de la partida a un jugador adyacente", "neighbour"),
        (23, "Lanzallamas", "Accion", 4, "Elimina de la partida a un jugador adyacente", "neighbour"),
        (24, "Lanzallamas", "Accion", 6, "Elimina de la partida a un jugador adyacente", "neighbour"),
        (25, "Lanzallamas", "Accion", 9, "Elimina de la partida a un jugador adyacente", "neighbour"),
        (26, "Lanzallamas", "Accion", 1, "Elimina de la partida a un jugador adyacente", "neighbour"),
        (27, "Analisis", "Accion", 5, "Mira la mano de cartas de un jugador adyacente", "neighbour"),
        (28, "Analisis", "Accion", 6, "Mira la mano de cartas de un jugador adyacente", "neighbour"),
        (29, "Analisis", "Accion", 9, "Mira la mano de cartas de un jugador adyacente", "neighbour"),
        (30, "Hacha", "Accion", 4, "Retira una carta \"Puerta Atrancada\" o \"Cuarentena\""\
         " de un jugador adyacente", "quarantine_door"),
        (31, "Hacha", "Accion", 9,"Retira una carta \"Puerta Atrancada\" o \"Cuarentena\""\
         " de un jugador adyacente", "quarantine_door"),
        (32, "Sospecha", "Accion", 4,"Mira 1 carta aleatoria de la mano de un jugador adyacente", "neighbour"),
        (33, "Sospecha", "Accion", 4, "Mira 1 carta aleatoria de la mano de un jugador adyacente", "neighbour"),
        (34, "Sospecha", "Accion", 4, "Mira 1 carta aleatoria de la mano de un jugador adyacente", "neighbour"),
        (35, "Sospecha", "Accion", 4, "Mira 1 carta aleatoria de la mano de un jugador adyacente", "neighbour"),
        (36, "Sospecha", "Accion", 7, "Mira 1 carta aleatoria de la mano de un jugador adyacente", "neighbour"),
        (37, "Sospecha", "Accion", 8, "Mira 1 carta aleatoria de la mano de un jugador adyacente", "neighbour"),
        (38, "Sospecha", "Accion", 9, "Mira 1 carta aleatoria de la mano de un jugador adyacente", "neighbour"),
        (39, "Sospecha", "Accion", 10, "Mira 1 carta aleatoria de la mano de un jugador adyacente", "neighbour"),
        (40, "Whisky", "Accion", 4, "Muestra todas tus cartas a todos los jugadores. Solo puedes jugar"\
         " esta carta sobre ti mismo", "self"),
        (41, "Whisky", "Accion", 6, "Muestra todas tus cartas a todos los jugadores. Solo puedes jugar"\
         " esta carta sobre ti mismo", "self"),
        (42, "Whisky", "Accion", 10, "Muestra todas tus cartas a todos los jugadores. Solo puedes jugar"\
         " esta carta sobre ti mismo", "self"),
        #(43, "Determinacion", "Accion", 4, "Roba 3 cartas \"¡Alejate!\", elige 1 para quedartela y descarta"\
        # " las demas. A continuacion, juega o descarta 1 carta.", "self"),
        #(44, "Determinacion", "Accion", 4, "Roba 3 cartas \"¡Alejate!\", elige 1 para quedartela y descarta"\
        # " las demas. A continuacion, juega o descarta 1 carta.", "self"),
        #(45, "Determinacion", "Accion", 6, "Roba 3 cartas \"¡Alejate!\", elige 1 para quedartela y descarta"\
        # " las demas. A continuacion, juega o descarta 1 carta.", "self"),
        #(46, "Determinacion", "Accion", 9, "Roba 3 cartas \"¡Alejate!\", elige 1 para quedartela y descarta"\
        # " las demas. A continuacion, juega o descarta 1 carta.", "self"),
        #(47, "Determinacion", "Accion", 10, "Roba 3 cartas \"¡Alejate!\", elige 1 para quedartela y descarta"\
        # " las demas. A continuacion, juega o descarta 1 carta.", "self"),
        (48, "Vigila tus espaldas", "Accion", 4, "Invierte el orden de juego. Ahora, tanto el orden de turnos"\
         " como los intercambios de cartas van en sentido contrario", "self"),
        (49, "Vigila tus espaldas", "Accion", 9, "Invierte el orden de juego. Ahora, tanto el orden de turnos"\
         " como los intercambios de cartas van en sentido contrario", "self"),
        (50, "¡Cambio de lugar!", "Accion", 4, "Cambiate de sitio con un jugador adyacente que no este en"\
         " Cuarentena o tras una Puerta atrancada", "neighbour"),
        (51, "¡Cambio de lugar!", "Accion", 4, "Cambiate de sitio con un jugador adyacente que no este en"\
         " Cuarentena o tras una Puerta atrancada", "neighbour"),
        (52, "¡Cambio de lugar!", "Accion", 7, "Cambiate de sitio con un jugador adyacente que no este en"\
         " Cuarentena o tras una Puerta atrancada", "neighbour"),
        (53, "¡Cambio de lugar!", "Accion", 9, "Cambiate de sitio con un jugador adyacente que no este en"\
         " Cuarentena o tras una Puerta atrancada", "neighbour"), 
        (54, "¡Cambio de lugar!", "Accion", 11, "Cambiate de sitio con un jugador adyacente que no este en"\
         " Cuarentena o tras una Puerta atrancada", "neighbour"),
        (55, "¡Mas vale que corras!", "Accion", 4, "Cambiate de sitio con cualquier jugador de tu eleccion"\
         " que no este en Cuarentena, ignorando cualquier Puerta atrancada.", "any"),
        (56, "¡Mas vale que corras!", "Accion", 4, "Cambiate de sitio con cualquier jugador de tu eleccion"\
         " que no este en Cuarentena, ignorando cualquier Puerta atrancada.", "any"),
        (57, "¡Mas vale que corras!", "Accion", 7, "Cambiate de sitio con cualquier jugador de tu eleccion"\
         " que no este en Cuarentena, ignorando cualquier Puerta atrancada.", "any"),
        (58, "¡Mas vale que corras!", "Accion", 8, "Cambiate de sitio con cualquier jugador de tu eleccion"\
         " que no este en Cuarentena, ignorando cualquier Puerta atrancada.", "any"),
        (59, "¡Mas vale que corras!", "Accion", 11, "Cambiate de sitio con cualquier jugador de tu eleccion"\
         " que no este en Cuarentena, ignorando cualquier Puerta atrancada.", "any"),
        (60, "Seduccion", "Accion", 4, "Intercambia una carta con cualquier jugador de tu eleccion que no este"\
         " en Cuarentena. Tu turno termina", "any"),
        (61, "Seduccion", "Accion", 4, "Intercambia una carta con cualquier jugador de tu eleccion que no este"\
         " en Cuarentena. Tu turno termina", "any"),
        (62, "Seduccion", "Accion", 6, "Intercambia una carta con cualquier jugador de tu eleccion que no este"\
         " en Cuarentena. Tu turno termina", "any"),
        (63, "Seduccion", "Accion", 7, "Intercambia una carta con cualquier jugador de tu eleccion que no este"\
         " en Cuarentena. Tu turno termina", "any"),
        (64, "Seduccion", "Accion", 8, "Intercambia una carta con cualquier jugador de tu eleccion que no este"\
         " en Cuarentena. Tu turno termina", "any"),
        (65, "Seduccion", "Accion", 10, "Intercambia una carta con cualquier jugador de tu eleccion que no este"\
         " en Cuarentena. Tu turno termina", "any"),
        (66, "Seduccion", "Accion", 11, "Intercambia una carta con cualquier jugador de tu eleccion que no este"\
         " en Cuarentena. Tu turno termina", "any"),
        (67, "Aterrador", "Defensa", 5, "Niegate a un ofrecimiento de intercambio de cartas y mira la carta que"\
         " te has negado a recibir. Roba 1 carta \"¡Alejate!\" en sustitucion de esta.", "self"),
        (68, "Aterrador", "Defensa", 6, "Niegate a un ofrecimiento de intercambio de cartas y mira la carta que"\
         " te has negado a recibir. Roba 1 carta \"¡Alejate!\" en sustitucion de esta.", "self"),
        (69, "Aterrador", "Defensa", 8, "Niegate a un ofrecimiento de intercambio de cartas y mira la carta que"\
         " te has negado a recibir. Roba 1 carta \"¡Alejate!\" en sustitucion de esta.", "self"),
        (70, "Aterrador", "Defensa", 11, "Niegate a un ofrecimiento de intercambio de cartas y mira la carta que"\
         " te has negado a recibir. Roba 1 carta \"¡Alejate!\" en sustitucion de esta.", "self"),
        (71, "Aqui estoy bien", "Defensa", 4, "Cancela una carta de \"¡Cambio de lugar!\" o \"¡Mas vale que corras!\""\
         " de la que seas objetivo. Roba 1 carta \"¡Alejate!\" en sustitucion de esta.", "self"),
        (72, "Aqui estoy bien", "Defensa", 6, "Cancela una carta de \"¡Cambio de lugar!\" o \"¡Mas vale que corras!\""\
         " de la que seas objetivo. Roba 1 carta \"¡Alejate!\" en sustitucion de esta.", "self"),
        (73, "Aqui estoy bien", "Defensa", 11, "Cancela una carta de \"¡Cambio de lugar!\" o \"¡Mas vale que corras!\""\
         " de la que seas objetivo. Roba 1 carta \"¡Alejate!\" en sustitucion de esta.", "self"),
        (74, "¡No, gracias!", "Defensa", 4, "Niegate a un ofrecimiento de intercambio de cartas. Roba 1 carta"\
         " \"¡Alejate!\" en sustitucion de esta.", "self"),
        (75, "¡No, gracias!", "Defensa", 6, "Niegate a un ofrecimiento de intercambio de cartas. Roba 1 carta"\
         " \"¡Alejate!\" en sustitucion de esta.", "self"),
        (76, "¡No, gracias!", "Defensa", 8, "Niegate a un ofrecimiento de intercambio de cartas. Roba 1 carta"\
         " \"¡Alejate!\" en sustitucion de esta.", "self"),
        (77, "¡No, gracias!", "Defensa", 11, "Niegate a un ofrecimiento de intercambio de cartas. Roba 1 carta"\
         " \"¡Alejate!\" en sustitucion de esta.", "self"),
        (78, "¡Fallaste!", "Defensa", 4, "El siguiente jugador despues de ti realiza el intercamibio de cartas"\
         " en lugar de hacerlo tu. No queda Infectado si recibe una carta \"¡Infectado!\". Roba una carta \"¡Alejate!\""\
         " en sustitucion de esta.", "self"),
        (79, "¡Fallaste!", "Defensa", 6, "El siguiente jugador despues de ti realiza el intercamibio de cartas"\
         " en lugar de hacerlo tu. No queda Infectado si recibe una carta \"¡Infectado!\". Roba una carta \"¡Alejate!\""\
         " en sustitucion de esta.", "self"),
        (80, "¡Fallaste!", "Defensa", 11, "El siguiente jugador despues de ti realiza el intercamibio de cartas"\
         " en lugar de hacerlo tu. No queda Infectado si recibe una carta \"¡Infectado!\". Roba una carta \"¡Alejate!\""\
         " en sustitucion de esta.", "self"),
        (81, "¡Nada de barbacoas!", "Defensa", 4, "Cancela una carta \"Lanzallamas\" que te tenga como objetivo. Roba"\
         " 1 carta \"¡Alejate!\" en sustitucion de esta.", "self"),
        (82, "¡Nada de barbacoas!", "Defensa", 6, "Cancela una carta \"Lanzallamas\" que te tenga como objetivo. Roba"\
         " 1 carta \"¡Alejate!\" en sustitucion de esta.", "self"),
        (83, "¡Nada de barbacoas!", "Defensa", 11, "Cancela una carta \"Lanzallamas\" que te tenga como objetivo. Roba"\
         " 1 carta \"¡Alejate!\" en sustitucion de esta.", "self"),
        (84, "Cuarentena", "Obstaculo", 5, "Durante 2 rondas, un jugador adyacente debe robar, descartar e intercambiar cartas"\
         " boca arriba. No puede eliminar jugadores ni cambiar de sitio.", "neighbour"),
        (85, "Cuarentena", "Obstaculo", 9, "Durante 2 rondas, un jugador adyacente debe robar, descartar e intercambiar cartas"\
         " boca arriba. No puede eliminar jugadores ni cambiar de sitio.", "neighbour"),
        (86, "Puerta atrancada", "Obstaculo", 4, "Coloca esta carta entre un jugador adyancete y tu. No se permiten acciones entre"\
         " este jugador y tu.", "neighbour"),
        (87, "Puerta atrancada", "Obstaculo", 7, "Coloca esta carta entre un jugador adyancete y tu. No se permiten acciones entre"\
         " este jugador y tu.", "neighbour"),
        (88, "Puerta atrancada", "Obstaculo", 11, "Coloca esta carta entre un jugador adyancete y tu. No se permiten acciones entre"\
         " este jugador y tu.", "neighbour"),
        (89, "Cuerdas podridas", "Panico", 6, "¡Las viejas cuerdas que usaste son faciles de romper! Todas las cartas \"Cuarentena\""\
        " que haya en juego son descartadas.", "self"),
        (90, "Cuerdas podridas", "Panico", 9, "¡Las viejas cuerdas que usaste son faciles de romper! Todas las cartas \"Cuarentena\""\
        " que haya en juego son descartadas.", "self"),
        (91, "Uno, dos...", "Panico", 5, "...con La Cosa ve diciendo adios. Cambiate de sitio con el tercer jugador que tengas a tu"\
         " izquierda o a tu derecha (a tu eleccion), ignorando cualquier carta, \"Puerta atrancada\" que haya en juego."\
         " Si tu o ese jugador estais en Cuarentena, el cambio no tiene lugar.", "direction"),
        (92, "Uno, dos...", "Panico", 9, "...con La Cosa ve diciendo adios. Cambiate de sitio con el tercer jugador que tengas a tu"\
         " izquierda o a tu derecha (a tu eleccion), ignorando cualquier carta, \"Puerta atrancada\" que haya en juego."\
         " Si tu o ese jugador estais en Cuarentena, el cambio no tiene lugar.", "direction"),
        (93, "Tres, cuatro...", "Panico", 4, "...se cuela sin trabajo. Todas las cartas \"Puerta atrancada\" que haya en juego son descartadas\".", "self"),
        (94, "Tres, cuatro...", "Panico", 9, "...se cuela sin trabajo. Todas las cartas \"Puerta atrancada\" que haya en juego son descartadas\".", "self"),
        (95, "¿Es aqui la fiesta?", "Panico", 5, "Descarta todas las cartas \"Cuarentena\" y \"Puerta atrancada\" que haya en juego. A continuacion"\
         ", empezando por ti, todos los jugadores cambian de sitio por parejas en el sentido de las agujas del reloj. Si hay un numero impar de jugadores"\
         " el ultimo jugador no se mueve.", "self"),
        (96, "¿Es aqui la fiesta?", "Panico", 9, "Descarta todas las cartas \"Cuarentena\" y \"Puerta atrancada\" que haya en juego. A continuacion"\
         ", empezando por ti, todos los jugadores cambian de sitio por parejas en el sentido de las agujas del reloj. Si hay un numero impar de jugadores"\
         " el ultimo jugador no se mueve.", "self"),
        #(97, "¡Sal de aqui!", "Panico", 5, "Cambiate de sitio con cualquier jugador de tu eleccion que no este en cuarentena.", "any"),
        (98, "Olvidadizo", "Panico", 4, "Descarta 3 cartas de tu mano y roba 3 nuevas cartas \"¡Alejate!\", descartando cualquier carta de \"Panico\""\
         " robada.", "self"),
        (99, "Vuelta y vuelta", "Panico", 4, "Todos los jugadores deben darle 1 carta al siguiente jugador que tengan al lado, simultaneamente y en el sentido"\
         " de juego actual, ignorando cualquier carta \"Puerta atrancada\" y \"Cuarentena\" que haya en juego. No puedes usar ninguna carta para evitar este intercambio."\
         " La Cosa puede infectar a otro jugador de esta forma, pasandole una carta \"¡Infectado!\". Tu turno termina.", "self"),
        (100, "Vuelta y vuelta", "Panico", 9, "Todos los jugadores deben darle 1 carta al siguiente jugador que tengan al lado, simultaneamente y en el sentido"\
         " de juego actual, ignorando cualquier carta \"Puerta atrancada\" y \"Cuarentena\" que haya en juego. No puedes usar ninguna carta para evitar este intercambio."\
         " La Cosa puede infectar a otro jugador de esta forma, pasandole una carta \"¡Infectado!\". Tu turno termina.", "self"),
        (101, "¿No podemos ser amigos?", "Panico", 7, "Intercambia 1 carta con cualquier jugador de tu eleccion que no este en Cuarentena.", "any"),
        (102, "¿No podemos ser amigos?", "Panico", 9, "Intercambia 1 carta con cualquier jugador de tu eleccion que no este en Cuarentena.", "any"),
        (103, "Cita a ciegas", "Panico", 4, "Intercambia una carta de tu mano con la primera carta del mazo, descartando cualquier carta de \"Panico\" robada. Tu turno termina", "self"),
        (104, "Cita a ciegas", "Panico", 9, "Intercambia una carta de tu mano con la primera carta del mazo, descartando cualquier carta de \"Panico\" robada. Tu turno termina", "self"),
        (105, "¡Ups!", "Panico", 10, "Muestrales todas las cartas de tu mano a todos los jugadores.", "self"),
        (106, "Que quede entre nosotros", "Panico", 7, "Muestrale todas las cartas de tu mano a un jugador adyacente de tu eleccion.", "neighbour"),
        (107, "Que quede entre nosotros", "Panico", 9, "Muestrale todas las cartas de tu mano a un jugador adyacente de tu eleccion.", "neighbour"),
        (108, "Revelaciones", "Panico", 8, "Empezando por tu y siguiendo el orden de juego, cada jugador elige si revela o no su mano. La ronda de \"Revelaciones\" termina cuando"\
         " un jugador muestre una carta \"¡Infectado!\", sin que tenga que revelar el resto de su mano.", "self"),
        # No pude encontrar la ultima carta
        (109, "?", "?", 15, "?", "any")
    ]
    # Llenar base de datos con las cartas lanzallamas y cartas que no hacen nada
    with db_session:
        for id, name, type, num_players, effect, target in all_cards:
            #print(f"\n\n\n\n\n\n\" {id} \n\n\n\n\n\n\n\n")
            Card(id=id,name=name,num_players=num_players,type=type,effect=effect,target=target)