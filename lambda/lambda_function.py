# -*- coding: utf-8 -*-
#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License
# is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
#

# This is a High Low Guess game Alexa Skill.
# The skill serves as a simple sample on how to use the
# persistence attributes and persistence adapter features in the SDK.
import random
import bus

from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name

SKILL_NAME = 'Smart Bus'
sb = StandardSkillBuilder(table_name="Smart-Bus", auto_create_table=True)


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    # Handler for Skill Launch

    # Get the persistence attributes
    attr = handler_input.attributes_manager.persistent_attributes
    if not attr:
        attr['code'] = 0
        attr['station'] = u'None'
        attr['way'] = u'None'

    handler_input.attributes_manager.session_attributes = attr
    handler_input.attributes_manager.save_persistent_attributes()

    speech_text = (
        "Bienvenue sur smart bus ."
        "Smart bus vous permet de connaitre les horraires des prochains passage de votre ligne ."
        "Pour débuter la configuration de smart bus, dites: configurer le bus ... suivi du numéro de votre ligne ."
        "Pour connaitre l heure de passage de votre prochain bus, dites : quand passe mon bus ?"
        )
    reprompt = "Dites quels sont les stations de la ligne 141."

    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    # Handler for Help Intent
    speech_text = (
        "Smart Bus permet de connaitre les prochains passage de votre bus ."
        "Pour cela, il faut configurer smart bus avec le numéro de bus, le nom "
        " de votre arret et le sens de votre ligne ."
        "Pour débuter la configuration de smart bus, dites: configurer le bus ... suivi du numéro de votre ligne ."
        "Pour connaitre l heure de passage de votre prochain bus, dites : quand passe mon bus ?"
        )
    reprompt = (
        "Pour débuter la configuration de smart bus, dites: configurer le bus ... suivi du numéro de votre ligne ."
        "Pour connaitre l heure de passage de votre prochain bus, dites : quand passe mon bus ?"
        )

    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(
    can_handle_func=lambda input:
        is_intent_name("AMAZON.CancelIntent")(input))
def cancel_intent_handler(handler_input):
    # Single handler for Cancel and Stop Intent
    speech_text = "OK!"
    reprompt = (
        "Pour débuter la configuration de smart bus, dites: configurer le bus ... suivi du numéro de votre ligne ."
        "Pour connaitre l heure de passage de votre prochain bus, dites : quand passe mon bus ?"
        )

    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response

@sb.request_handler(
    can_handle_func=lambda input:
        is_intent_name("AMAZON.StopIntent")(input))
def stop_intent_handler(handler_input):
    # Single handler for Cancel and Stop Intent
    speech_text = "A bientôt!"

    handler_input.response_builder.speak(
        speech_text).set_should_end_session(True)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    # Handler for Session End
    print(
        "Session ended with reason: {}".format(
            handler_input.request_envelope.request.reason))
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=lambda input:
                    is_intent_name("GetBusStop")(input))
def get_bus_stop(handler_input):
    # Get all bus stop of the line
    if handler_input.request_envelope.request.intent.slots["busnumber"].value:
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['code'] = handler_input.request_envelope.request.intent.slots["busnumber"].value

        mybus = bus.Bus(session_attr['code'])
        if mybus.query_code == 200:
            speech_text = mybus.getStations()
            reprompt = "Pour configurer la station, dites: configurer la station ... suivi du numéro de station ."
            speech_text += reprompt
        else:
            speech_text = "Numéro de bus inconnu ."
            reprompt = "Pour connaitre les numéros de stations, dites: quels sont les stations de la ligne ... suivi du numéro du bus"
            speech_text += reprompt
    else:
        speech_text = "Vous devez donner le numéro de ligne de bus ."
        reprompt += "Pour connaitre les numéros de stations, dites: quels sont les stations de la ligne ... suivi du numéro du bus"
        speech_text += reprompt

    handler_input.response_builder.speak(speech_text).ask(reprompt)
    handler_input.attributes_manager.persistent_attributes = session_attr
    handler_input.attributes_manager.save_persistent_attributes()
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=lambda input:
                    is_intent_name("Configure")(input))
def configure_smart_bus(handler_input):
    # Configure bus, station and direction

    # Get the persistence attributes
    attr = handler_input.attributes_manager.persistent_attributes
    if not attr:
        attr['code'] = 0
        attr['station'] = u'None'
        attr['way'] = u'None'
        handler_input.attributes_manager.session_attributes = attr
        handler_input.attributes_manager.save_persistent_attributes()

    session_attr = handler_input.attributes_manager.session_attributes
    what = handler_input.request_envelope.request.intent.slots["what"].value
    
    if what == 'bus':
        if handler_input.request_envelope.request.intent.slots["whatnumber"].value:
            session_attr['code'] = handler_input.request_envelope.request.intent.slots["whatnumber"].value
            session_attr['station'] = u'None'
            session_attr['way'] = u'None'

            mybus = bus.Bus(session_attr['code'])
            if mybus.query_code == 200:
                speech_text = "Vous venez de configurer la ligne de bus numéro {0} .".format(session_attr['code'])
                reprompt = "Pour configurer la station, dites: configurer la station ... suivi du numéro de station ."
                reprompt += "Pour connaitre les numéros de stations, dites: quels sont les stations de la ligne ... suivi du numéro du bus"
                speech_text += reprompt
            else:
                speech_text = "Numéro de bus inconnu ."
                reprompt = "Pour débuter la configuration de smart bus dites: configurer le bus ... suivi du numéro de votre ligne"
                speech_text += reprompt
        else:
            speech_text = "Vous devez donner le numéro de ligne de bus ."
            reprompt = "Pour débuter la configuration de smart bus dites: configurer le bus ... suivi du numéro de votre ligne"
            speech_text += reprompt

    elif what == 'station':
        if handler_input.request_envelope.request.intent.slots["whatnumber"].value:
            if session_attr['code'] != 0:
                mybus = bus.Bus(session_attr['code'])
                stationNumber = int(handler_input.request_envelope.request.intent.slots["whatnumber"].value)
                
                # check station number
                if (stationNumber > 0) & (stationNumber <= len(mybus.stations)):
                    stationName = mybus.stations[stationNumber-1]
                    session_attr['station'] = stationName
                    speech_text = "Vous venez de configurer la station {0} .".format(stationName)
                    reprompt = "Pour configurer la direction, dites: configurer la direction ... suivi de aller ou retour"
                    speech_text += reprompt
                else:
                    speech_text = "Le numéro de station doit être compris entre 1 et {0} .".format(len(mybus.stations))
                    reprompt = "Pour configurer la station, dites: configurer la station ... suivi du numéro de station ."
                    speech_text += reprompt
            else:
                speech_text = "Le numéro de ligne de bus n'a pas été configuré ."
                reprompt = "Pour débuter la configuration de smart bus dites: configurer le bus ... suivi du numéro de votre ligne"
                speech_text += reprompt
        else:
            speech_text = "Vous devez donner le numéro de station ."
            reprompt = "Pour configurer la station, dites: configurer la station ... suivi du numéro de station ."
            speech_text += reprompt

    elif what == 'direction':
        if handler_input.request_envelope.request.intent.slots["whatstring"].value:
            if (session_attr['code'] != 0) & (session_attr['station'] != u'None'):
                direction = handler_input.request_envelope.request.intent.slots["whatstring"].value
                if direction == 'aller':
                    session_attr['way'] = 'A'
                    speech_text = "Vous venez de configurer la direction {0} .".format(direction)
                    speech_text += "Configuration terminer. Pour connaitre l'heure du prochain bus, dites: quand passe mon bus ."
                    reprompt = "Pour connaitre l heure de passage de votre prochain bus, dites : quand passe mon bus ?"
                elif direction == 'retour':
                    session_attr['way'] = 'R'
                    speech_text = "Vous venez de configurer la direction {0} .".format(direction)
                    speech_text += "Configuration terminer. Pour connaitre l'heure du prochain bus, dites: quand passe mon bus ."
                    reprompt = "Pour connaitre l heure de passage de votre prochain bus, dites : quand passe mon bus ?"
                else:
                    print 'Direction inconnue: {0}'.format(direction)
                    speech_text = "Direction {0} inconnue .".format(direction)
                    reprompt = "Pour configurer la direction, dites: configurer la direction ... suivi de: aller ou retour"
                    speech_text += reprompt

            elif session_attr['code'] == 0:
                speech_text = "Le numéro de ligne de bus n'a pas ete configurer ."
                reprompt = "Pour débuter la configuration de smart bus dites: configurer le bus ... suivi du numéro de votre ligne"
                speech_text += reprompt
            else:
                speech_text = "Le numéro de station n'a pas ete configurer ."
                reprompt = "Pour configurer la station, dites: configurer la station ... suivi du numéro de station ."
                speech_text += reprompt
        else:
            speech_text = "Vous devez donner la direction ."
            reprompt = "Pour configurer la direction, dites: configurer la direction ... suivi de: aller ou retour"
            speech_text += reprompt

    else:
        print 'Type de configuration inconnue.'
        speech_text = "Type de configuration inconnue ."
        reprompt = "Pour débuter la configuration de smart bus dites: configurer le bus ... suivi du numéro de votre ligne ."
        reprompt += "Pour configurer la station, dites: configurer la station ... suivi du numéro de station ."
        reprompt += "Pour configurer la direction, dites: configurer la direction ... suivi de: aller ou retour"
        speech_text += reprompt

    handler_input.response_builder.speak(speech_text).ask(reprompt)
    handler_input.attributes_manager.persistent_attributes = session_attr
    handler_input.attributes_manager.save_persistent_attributes()
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=lambda input:
                    is_intent_name("GetNextBus")(input))
def get_next_bus(handler_input):
    # Get the two next time of bus stop
    # Get the persistence attributes
    attr = handler_input.attributes_manager.persistent_attributes
    if not attr:
        attr['code'] = 0
        attr['station'] = u'None'
        attr['way'] = u'None'
        handler_input.attributes_manager.session_attributes = attr
        handler_input.attributes_manager.save_persistent_attributes()

    if (attr['code'] != 0) & (attr['station'] != u'None') & (attr['way'] != u'None'):
        mybus = bus.Bus(attr['code'])
        mybus.setStation(attr['station'])
        mybus.setWay(attr['way'])

        speech_text = mybus.getSchedules()
        handler_input.response_builder.speak(speech_text).set_should_end_session(True)
    else:
        speech_text = "Aucune configuration ou configuration incomplete ."
        reprompt = "Pour débuter la configuration de smart bus dites: configurer le bus ... suivi du numéro de votre ligne"
        speech_text += reprompt
        handler_input.response_builder.speak(speech_text).ask(reprompt)

    return handler_input.response_builder.response

@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    # Catch all exception handler, log exception and
    # respond with custom message
    print("Encountered following exception: {}".format(exception))
    speech_text = "Désolé, il y a eu un problème. Veuillez relancer la configuration ."
    reprompt = "Pour débuter la configuration de smart bus dites: configurer le bus ... suivi du numéro de votre ligne"
    speech_text += reprompt
    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


@sb.global_response_interceptor()
def log_response(handler_input, response):
    print("Response : {}".format(response))


handler = sb.lambda_handler()
