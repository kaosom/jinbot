'''
    Logica dentras de los mensajes, seguir el flujo de la conversacion. 
'''

import json
import requests
import re
from .database import DB
from . import sett
from .sett import TOTAL_SOLICITUDES


def obtener_mensaje_whatsapp(message):
    '''
        Verficicamos que sea un mensaje valido. 
    '''
    if 'type' not in message:
        text = 'mensaje no reconocido'
        return text

    type_message = message['type']
    if type_message == 'text':
        text = message['text']['body']
    elif type_message == 'button':
        text = message['button']['text']
    elif type_message == 'interactive' and message['interactive']['type'] == 'lista_reply':
        text = message['interactive']['lista_reply']['title']
    elif type_message == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    else:
        text = 'mensaje no procesado'

    return text


def enviar_mensaje_whatsapp(data):
    '''
        Logica detras de enviar el mensaje con toda la informacion. 
    '''
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        response = requests.post(whatsapp_url, headers=headers, data=data, timeout=10)

        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e, 403


def text_message(number, text):
    '''
        Se le da el fomato de json a nuestra variable data para poder 
        trabajar con ella. 
    '''
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                    "body": text
            }
        }
    )
    return data


def button_reply_message(number, options, body, footer, sedd):
    '''
        Funcion para poder asignar los botones. 
    '''
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": sedd + "_btn_" + str(i+1),
                    "title": option
                }
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data


def reply_reaction_message(number, message_id, emoji):
    '''
        Asignar una reaccion al mensaje enviado de acuerdo a su id. 
    '''
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": message_id,
                "emoji": emoji
            }
        }
    )
    return data


def replytext_message(number, message_id, text):
    '''
        Respondemos al chat una vez seleccionado un boton.
    '''
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": {"message_id": message_id},
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data


def replace_start(s):
    '''
        En el formato original los numeros aparecen con 521 y se 
        cambia para que solamente tenga el 52. 
    '''
    if s.startswith("521"):
        return "52" + s[3:]
    else:
        return s


def mark_read_message(message_id):
    '''
        Marcamos como leido el mensake. 
    '''
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  message_id
        }
    )
    return data


def send_resultados(datos):
    '''
        Logica detras de enviar los resultados por chat a todos los usuarios.
    '''
    mensaje = '<-- EQUIPO COMPASION - RESULTADOS -->\n'
    for dato in datos:
        number = dato[1]
        name = dato[2]
        justification = dato[3]
        dinero = dato[4]
        link = dato[5]
        email = dato[6]
        status = dato[8] 
        if status:
            mensaje += '🎉 FELICIDADES, HAS SIDO SELECCIONADO PARA LA BECA! 🎓'
        else:
            mensaje += '😔 LAMENTAMOS INFORMARTE QUE NO HAS SIDO SELECCIONADO PARA LA BECA. 📚'
        mensaje += f"\n\nDatos ingresados:\n\nNombre: {name}\nJustificación: {justification}\nMonto solicitado: {dinero}\nEnlace: {link}\nCorreo Electrónico: {email}"
        enviar_mensaje_whatsapp(text_message(number, mensaje))




def administrar_chatbot(text, number, message_id):
    '''
        Logica detras del envio de mensajes. 
    '''
    # Definimos las variables iniciales
    base = DB()
    counter = base.recuperar_posicion(number) or 0
    total = base.get_total() or 0
    admin_mode = base.get_status_encuesta_finalizada() or 0
    # Se le da formato al texto.
    text = text.lower().strip()
    #Comandos para reiniciar los valores
    if 'reiniciar.mecatr0nica.database' in text:
        base.formatear_database()
        return
    if 'reiniciar.mecatr0nica.evaluadores' in text:
        base.formatear_evaluadores()
        return
    if 'reiniciar.mecatr0nica.datos_globales' in text:
        base.formatear_datos_globales()
        return
    if 'reiniciar.mecatr0nica.global' in text:
        # Todos los anteriores
        base.formatear_global()
        return
    # print('Counter -> ', counter)
    # print('Mensaje -> ', text)
    lista = []
    # Marcamos el mensaje como leido
    mark_read = mark_read_message(message_id)
    lista.append(mark_read)
    if total <= TOTAL_SOLICITUDES and not admin_mode:
        if counter == 0:
            body = "¡Hola! 👋 Bienvenido a ConPasion. ¿Cómo podemos ayudarte hoy?"
            footer = "Equipo Compasion"
            options = ["✅ Manual", "🤲 Quienes somos"]

            reply_button_data = button_reply_message(
                number, options, body, footer, "sed1")
            replyReaction = reply_reaction_message(number, message_id, "🫡")
            lista.append(replyReaction)
            lista.append(reply_button_data)
            base.modificar_posicion(number, counter)
        elif "manual" in text and len(text.split()) == 2 and counter == 1 :
            body = "En el orden que se te vaya pidiendo deberás escribir los siguientes datos:\n1. Nombre del proyecto que requiere un apoyo economico.\n2. Justificacion del proyecto (menos de 100 palabras)\n3.Cantidad de dinero.\n4. Video subido a YT para mostrar el proyecto.\n5. Correo para mandar resultados."
            footer = "ComPasion Contigo."
            options = ["✅ Empezar",
                       "❌ Cancelar"]

            reply_button_data = button_reply_message(
                number, options, body, footer, "sed2")
            lista.append(reply_button_data)
            base.modificar_posicion(number, counter)
        elif "quienes somos" in text and len(text.split()) == 3 and counter == 1:
            body = "Somos Canico, una empresa dedicada a la innovación y excelencia en el desarrollo de software 👌. A través de nuestro proyecto de ayuda comunitaria 💟'conpasión'💟, nos esforzamos por hacer una diferencia positiva en la sociedad 💁🏻. Nuestra misión es crear software innovador que cumpla con los más altos estándares de calidad, seguridad y rendimiento, proporcionando herramientas a nuestros clientes para agilizar procesos administrativos, mejorando su eficiencia y productividad 😎.Nuestra visión es ser líderes en el mercado, reconocidos por nuestra excelencia en el desarrollo de soluciones tecnológicas vanguardistas que permiten la recopilación de información de manera normativa y responsable 😀. Nos dedicamos a apoyar a organizaciones de diversos sectores, brindándoles soluciones para capturar, analizar y recopilar información, fomentando la innovación y promoviendo la confianza en la era digital👾."
            footer = "ComPasion Contigo."
            options = ["✅ Manual"]

            reply_button_data = button_reply_message(
                number, options, body, footer, "sed2")

            lista.append(reply_button_data)
        elif "empezar" in text and len(text.split()) == 2 and counter == 2:
            data = text_message(
                number, "Por favor escribe el nombre del proyecto.😊")
            lista.append(data)
            base.modificar_posicion(number, counter)
        elif counter == 3:
            # print('Dato a guardar en la base: ', text)
            base.insertar(number, text, 'nombre')
            body = "Nombre registrado correctamente.\n¿Quieres modificar el nombre o continuar? 👀"
            footer = "Equipo ComPasion"
            options = ["✅ Continuar", "❌ Modificar"]

            button_reply = button_reply_message(
                number, options, body, footer, "sed3")
            lista.append(button_reply)
            base.modificar_posicion(number, counter)
        elif "cancelar" in text and len(text.split()) == 2:
            data = text_message(
                number, "Operacion cancelada. Que tengas un buen día. 😊")
            lista.append(data)
            base.modificar_posicion(number, counter, position= 0)
        elif "modificar" in text and len(text.split()) == 2 and counter == 4:
            data = text_message(
                number, "Escribe nuevamente el nombre. 😊")
            lista.append(data)
            base.modificar_posicion(number, counter, position=3)
        elif "continuar" in text and len(text.split()) == 2 and counter == 4:
            data = text_message(
                number, "Por favor escribe la justificacion.😊")
            lista.append(data)
            base.modificar_posicion(number, counter)
        elif counter == 5:
            if len(text.split()) > 100:
                data = text_message(
                    number, "Recuerda que tienen que ser menos de 100 palabras. Por favor vuelve a escribirla.😊")
                lista.append(data)
            else:
                # print('Dato a guardar en la base: ', text)
                base.insertar(number, text, 'justificacion')
                body = "Justificacion registrado correctamente.\n¿Quieres modificar el nombre o continuar? 👀"
                footer = "Equipo ComPasion"
                options = ["✅ Continuar", "❌ Modificar"]

                button_reply = button_reply_message(
                    number, options, body, footer, "sed3")
                lista.append(button_reply)
                base.modificar_posicion(number, counter)
        elif "modificar" in text and len(text.split()) == 2 and counter == 6:
            data = text_message(
                number, "Escribe nuevamente la justificacion. 😊")
            lista.append(data)
            base.modificar_posicion(number, counter, position=5)
        elif "continuar" in text and len(text.split()) == 2 and counter == 6:
            data = text_message(
                number, "Por favor escribe la cantidad de dinero.😊")
            lista.append(data)
            base.modificar_posicion(number, counter)

        elif counter == 7:
            # print('Dato a guardar en la base: ', text)
            base.insertar(number, text, 'dinero')
            body = "Cantidad de dinero registrada.\n¿Quieres modificar la cantidad de dinero o continuar? 👀"
            footer = "Equipo ComPasion"
            options = ["✅ Continuar", "❌ Modificar"]
            button_reply = button_reply_message(
                number, options, body, footer, "sed3")
            lista.append(button_reply)
            base.modificar_posicion(number, counter)
        elif "modificar" in text and len(text.split()) == 2 and counter == 8:
            data = text_message(
                number, "Escribe nuevamente la cantidad de dinero. 😊")
            lista.append(data)
            base.modificar_posicion(number, counter, position=7)
        elif "continuar" in text and len(text.split()) == 2 and counter == 8:
            data = text_message(
                number, "Ingrese unicamente la URL del video de YouTube.😊\nPor favor asegurese que incluya 'youtube.com' dentro del link para validarlo. 😌")
            lista.append(data)
            base.modificar_posicion(number, counter)

        elif counter == 9:
            if 'youtube.com' in text:
                body = "Video registrado.\n¿Quieres modificar la url o continuar? 👀"
                footer = "Equipo ComPasion"
                options = ["✅ Continuar", "❌ Modificar"]
                button_reply = button_reply_message(
                    number, options, body, footer, "sed3")
                lista.append(button_reply)
                base.modificar_posicion(number, counter)
                # print('Dato a guardar en la base: ', text)
                base.insertar(number, text, 'video')
            else:
                data = text_message(
                    number, "Recuerda que tiene que ser un link de YouTube valido.😊")
                lista.append(data)
        elif "modificar" in text and len(text.split()) == 2 and counter == 10:
            data = text_message(
                number, "Escribe nuevamente la URL. 😊")
            lista.append(data)
            base.modificar_posicion(number, counter, position=9)
        elif "continuar" in text and len(text.split()) == 2 and counter == 10:
            data = text_message(
                number, "Ingrese su correo electronico. 📧")
            lista.append(data)
            base.modificar_posicion(number, counter)

        elif counter == 11:
            pattern = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")
            if re.match(pattern, text):
                # print('Dato a guardar en la base: ', text)
                base.insertar(number, text, 'correo')
                body = "Correo registrado correctamente.\n¿Quieres modificar el correo o continuar? 👀"
                footer = "Equipo ComPasion"
                options = ["✅ Continuar", "❌ Modificar"]
                button_reply = button_reply_message(
                    number, options, body, footer, "sed3")
                lista.append(button_reply)
                base.modificar_posicion(number, counter)
            else:
                data = text_message(
                    number, "Recuerda que tiene que ser un correo valido.😊")
                lista.append(data)
        elif "modificar" in text and len(text.split()) == 2 and counter == 12:
            data = text_message(
                number, "Escribe nuevamente el correo. 😊")
            lista.append(data)
            base.modificar_posicion(number, counter, position=11)
        elif "continuar" in text and len(text.split()) == 2 and counter == 12:
            data = text_message(
                number, "Muchas gracias por toda su informacion, se le enviara un correo indicando su status. 🕛")
            lista.append(data)
            if total == TOTAL_SOLICITUDES:
                # Aqui cambiamos el admin_mode
                base.set_status_encuesta_finalizada()
                for admin in sett.administradores:
                    # print(f"Emviando mensaje a -> {admin}")
                    message = "Iniciamos con la valoracion de solicitudes. Por favor escribe la palabra 'empezar' para comenzar."
                    enviar_mensaje_whatsapp(text_message(admin, message))
            base.modificar_posicion(number, counter)
        else:
            data = text_message(
                number, "Por favor selecciona una opción valida. 👀")
            lista.append(data)
    else:
        if number in sett.administradores and not base.get_status_evaluador(number):
            #Aqui se agrega la conficion que su estatus no este terminado
            # En esta parte es cuando se les manda el menasje sobre la propuesta
            limite_inferior, limite_superior = base.get_rango_de_evaluacion(number)
            # print(f'De {limite_inferior} a {limite_superior}')
            indice_dentro_del_rango = base.get_indice_dentro_del_rango(number)
            # print(f"Indice dentro del rango -> {indice_dentro_del_rango}")
               # Mantenemos las inspecciones dentro del rango indicado.
            if limite_superior > indice_dentro_del_rango:
                if 'empezar' in text:
                    # print(indice_dentro_del_rango)
                    body = base.get_solo_una_informacion(
                    indice_dentro_del_rango)
                    footer = f"Propuesta No. {indice_dentro_del_rango}"
                    options = ["✅ Aceptar", "❌ Rechazar"]
                    reply_button_data = button_reply_message(
                    number, options, body, footer, "sed1")
                    lista.append(reply_button_data)
                elif 'continuar' in text:
                    # print(indice_dentro_del_rango)
                    body = base.get_solo_una_informacion(
                    indice_dentro_del_rango + 1)
                    footer = f"Propuesta No. {indice_dentro_del_rango + 1}"
                    options = ["✅ Aceptar", "❌ Rechazar"]
                    reply_button_data = button_reply_message(number, options, body, footer, "sed1")
                    lista.append(reply_button_data)
                    base.update_indices(
                    number, indice_dentro_del_rango + 1)

                elif 'aceptar' in text:
                    # print(indice_dentro_del_rango + 1)
                    base.update_indices(number, indice_dentro_del_rango)
                    base.set_status(indice_dentro_del_rango, 1)
                    body = 'Siguiente propuesta.'
                    footer = f"Propuesta No. {indice_dentro_del_rango}"
                    options = ["✅ Continuar"]
                    reply_button_data = button_reply_message(number, options, body, footer, "sed1")
                    lista.append(reply_button_data)
                elif 'rechazar' in text:
                    base.update_indices(
                    number, indice_dentro_del_rango + 1)
                    base.set_status(indice_dentro_del_rango, 0)
                    body = 'Presiona continuar para ver la siguiente propuesta.'
                    footer = f"Propuesta No. {indice_dentro_del_rango}"
                    options = ["✅ Continuar"]
                    reply_button_data = button_reply_message(number, options, body, footer, "sed1")
                    lista.append(reply_button_data)
            else:
                message = "Gracias por resolver tu parte de la evulación. Ha acabado tu trabajo 👀."
                enviar_mensaje_whatsapp(text_message(number, message))
                # Se cambia el estado del evaluadador para saber que ya termino.
                base.set_status_evaluador(number)
                if base.get_status_total_evaluadores() and not base.get_evaluacion_finalizada():
                    base.set_evaluacion_finalizada()
                    # Enviamos los resultados. 
                    datos = base.get_all_information()
                    send_resultados(datos)
    for item in lista:
        # print(item)
        enviar_mensaje_whatsapp(item)
