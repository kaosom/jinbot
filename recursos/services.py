import smtplib
import json
import requests
from .database import DB
from . import sett
from .sett import TOTAL_SOLICITUDES


def obtener_Mensaje_whatsapp(message):
    if 'type' not in message:
        text = 'mensaje no reconocido'
        return text

    typeMessage = message['type']
    if typeMessage == 'text':
        text = message['text']['body']
    elif typeMessage == 'button':
        text = message['button']['text']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    else:
        text = 'mensaje no procesado'

    return text


def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        print("se envia ", data)
        response = requests.post(whatsapp_url, headers=headers, data=data)

        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e, 403


def text_Message(number, text):
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


def buttonReply_Message(number, options, body, footer, sedd):
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


def listReply_Message(number, options, body, footer, sedd):
    rows = []
    for i, option in enumerate(options):
        rows.append(
            {
                "id": sedd + "_row_" + str(i+1),
                "title": option,
                "description": ""
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Secciones",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )
    return data


def sticker_Message(number, sticker_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "sticker",
            "sticker": {
                "id": sticker_id
            }
        }
    )
    return data


def get_media_id(media_name, media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = sett.stickers.get(media_name, None)
    return media_id


def replyReaction_Message(number, messageId, emoji):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": messageId,
                "emoji": emoji
            }
        }
    )
    return data


def replyText_Message(number, messageId, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": {"message_id": messageId},
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data


def replace_start(s):
    if s.startswith("521"):
        return "52" + s[3:]
    else:
        return s


def mark_read_Message(messageId):

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data


def send_mail(datos):
    name_account = "ComPasion"
    email_account = "compasion.work@gmail.com"
    password_account = "yrtrzrhvtovtaqlt"

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(email_account, password_account)

    subject = 'Status de convocatoria ComPasion.'
    for dato in datos:
        number = dato[0]
        name = dato[1]
        justification = dato[2]
        dinero = dato[3]
        link = dato[4]
        email = dato[5]
        status = dato[7]

        if status:
            message = "Felicidades!! Has conseguido el apoyo economico por parte de ComPasion."
        else:
            message = "Lamentamos informarte que tu apoyo por parte de ComPasion ha sido rechazado."

        message += f'Tu informacion registrada fue la siguiente:\nNumero: {number}\nNombre del Proyecto: {name}\nJustificacion: {justification}\nCantidad de dinero: {dinero}\nLink a video de YouTube: {link}'
        sent_email = ("From: {0} <{1}>\n"
                      "To: {2} <{3}>\n"
                      "Subject: {4}\n\n"
                      "{5}"
                      .format(name_account, email_account, name, email, subject, message))
        print(sent_email)
        try:
            server.sendmail(email_account, [email], sent_email)
        except Exception:
            print('Could not send email to {}. Error: {}\n'.format(
                email, str(Exception)))

    # Close smtp server
    server.close()


def administrar_chatbot(text, number, messageId):
    base = DB()
    # Definimos las variables iniciales
    counter = base.recuperar_posicion(number) or 0
    total = base.get_total() or 0
    admin_mode = base.get_status_encuesta_finalizada() or 0
    # Se le da formato al texto. 
    text = text.lower().strip()
    list = []
    # Marcamos el mensaje como leido
    mark_read = mark_read_Message(messageId)
    list.append(mark_read)
    if total <= TOTAL_SOLICITUDES and not admin_mode:

        if total == TOTAL_SOLICITUDES:
            # Aqui cambiamos el admin_mode
            base.set_status_encuesta_finalizada()
            #Insertamos a los administradores
            datos = base.get_all_information()
            i = 0
            datos_por_administrador = len(datos) / len(sett.administradores)
            for admin in sett.administradores:
                print(admin)
                # Asigna los rangos en los que se va a mandar los mensajes asi como inserta los admins
                base.set_datos_administradores(admin, i + 1, i + datos_por_administrador)
                i += datos_por_administrador
                message = "Iniciamos con la valoracion de solicitudes. Por favor escribe la palabra 'empezar' para comenzar."
                enviar_Mensaje_whatsapp(text_Message(admin, message))
            
        if counter == 0:
            body = "¡Hola! 👋 Bienvenido a ConPasion. ¿Cómo podemos ayudarte hoy?"
            footer = "Equipo Compasion"
            options = ["✅ Manual", "📅 Quienes somos"]

            replyButtonData = buttonReply_Message(
                number, options, body, footer, "sed1")
            replyReaction = replyReaction_Message(number, messageId, "🫡")
            list.append(replyReaction)
            list.append(replyButtonData)
            base.modificar_posicion(number, counter)
            print("counter", counter)
        elif "manual" in text and len(text.split()) == 2 and counter == 1:
            body = "En el orden que se te vaya pidiendo deberás escribir los siguientes datos:\n1. Nombre del proyecto que requiere un apoyo economico.\n2. Justificacion del proyecto (menos de 100 palabras)\n3.Cantidad de dinero.\n4. Video subido a YT para mostrar el proyecto.\n5. Correo para mandar resultados."
            footer = "ComPasion Contigo."
            options = ["✅ Empezar",
                       "❌ Cancelar"]

            replyButtonData = buttonReply_Message(
                number, options, body, footer, "sed2")
            sticker = sticker_Message(
                number, get_media_id("perro_traje", "sticker"))

            list.append(replyButtonData)
            list.append(sticker)
            base.modificar_posicion(number, counter)
        elif "quienes somos" in text and len(text.split()) == 3 and counter == 1:
            pass
        elif "empezar" in text and len(text.split()) == 2 and counter == 2:
            data = text_Message(
                number, "Por favor escribe el nombre del proyecto.😊")
            list.append(data)
            base.modificar_posicion(number, counter)
        elif counter == 3:
            print('Dato a guardar en la base: ', text)
            base.insertar(number, text, 'nombre')
            body = "Nombre registrado correctamente.\nQuieres modificar el nombre o continuar?"
            footer = "Equipo ComPasion"
            options = ["✅ Continuar", "❌ Modificar"]

            buttonReply = buttonReply_Message(
                number, options, body, footer, "sed3")
            list.append(buttonReply)
            base.modificar_posicion(number, counter)
        elif "cancelar" in text and len(text.split()) == 2:
            data = text_Message(
                number, "Operacion cancelada. Que tengas un buen día. 😊")
            list.append(data)
        elif "modificar" in text and len(text.split()) == 2 and counter == 4:
            data = text_Message(
                number, "Escribe nuevamente el nombre. 😊")
            list.append(data)
            base.modificar_posicion(number, counter, position=3)
        elif "continuar" in text and len(text.split()) == 2 and counter == 4:
            data = text_Message(
                number, "Por favor escribe la justificacion.😊")
            list.append(data)
            base.modificar_posicion(number, counter)
        elif counter == 5:
            if len(text.split()) > 100:
                data = text_Message(
                    number, "Recuerda que tienen que ser menos de 100 palabras. Por favor vuelve a escribirla.😊")
                list.append(data)
            else:
                print('Dato a guardar en la base: ', text)
                base.insertar(number, text, 'justificacion')
                body = "Justificacion registrado correctamente.\nQuieres modificar el nombre o continuar?"
                footer = "Equipo ComPasion"
                options = ["✅ Continuar", "❌ Modificar"]

                buttonReply = buttonReply_Message(
                    number, options, body, footer, "sed3")
                list.append(buttonReply)
                base.modificar_posicion(number, counter)
        elif "modificar" in text and len(text.split()) == 2 and counter == 6:
            data = text_Message(
                number, "Escribe nuevamente la justificacion. 😊")
            list.append(data)
            base.modificar_posicion(number, counter, position=5)
        elif "continuar" in text and len(text.split()) == 2 and counter == 6:
            data = text_Message(
                number, "Por favor escribe la cantidad de dinero.😊")
            list.append(data)
            base.modificar_posicion(number, counter)

        elif counter == 7:
            print('Dato a guardar en la base: ', text)
            base.insertar(number, text, 'dinero')
            body = "Cantidad de dinero registrada.\nQuieres modificar la cantidad de dinero o continuar?"
            footer = "Equipo ComPasion"
            options = ["✅ Continuar", "❌ Modificar"]
            buttonReply = buttonReply_Message(
                number, options, body, footer, "sed3")
            list.append(buttonReply)
            base.modificar_posicion(number, counter)
        elif "modificar" in text and len(text.split()) == 2 and counter == 8:
            data = text_Message(
                number, "Escribe nuevamente la cantidad de dinero. 😊")
            list.append(data)
            base.modificar_posicion(number, counter, position=7)
        elif "continuar" in text and len(text.split()) == 2 and counter == 8:
            data = text_Message(
                number, "Ingrese unicamente la URL del video de YouTube.😊")
            list.append(data)
            base.modificar_posicion(number, counter)

        elif counter == 9:
            if 'www.you' in text:
                body = "Video registrado.\nQuieres modificar la url o continuar?"
                footer = "Equipo ComPasion"
                options = ["✅ Continuar", "❌ Modificar"]
                buttonReply = buttonReply_Message(
                    number, options, body, footer, "sed3")
                list.append(buttonReply)
                base.modificar_posicion(number, counter)
                print('Dato a guardar en la base: ', text)
                base.insertar(number, text, 'video')
            else:
                data = text_Message(
                    number, "Recuerda que tiene que ser un link de YouTube valido.😊")
                list.append(data)
        elif "modificar" in text and len(text.split()) == 2 and counter == 10:
            data = text_Message(
                number, "Escribe nuevamente la URL. 😊")
            list.append(data)
            base.modificar_posicion(number, counter, position=9)
        elif "continuar" in text and len(text.split()) == 2 and counter == 10:
            data = text_Message(
                number, "Ingrese su correo electronico.")
            list.append(data)
            base.modificar_posicion(number, counter)

        elif counter == 11:
            if '@' in text:
                print('Dato a guardar en la base: ', text)
                base.insertar(number, text, 'correo')
                body = "Correo registrado.\nQuieres modificar el correo o continuar?"
                footer = "Equipo ComPasion"
                options = ["✅ Continuar", "❌ Modificar"]
                buttonReply = buttonReply_Message(
                    number, options, body, footer, "sed3")
                list.append(buttonReply)
                base.modificar_posicion(number, counter)
            else:
                data = text_Message(
                    number, "Recuerda que tiene que ser un correo valido.😊")
                list.append(data)
        elif "modificar" in text and len(text.split()) == 2 and counter == 12:
            data = text_Message(
                number, "Escribe nuevamente el correo. 😊")
            list.append(data)
            base.modificar_posicion(number, counter, position=11)
        elif "continuar" in text and len(text.split()) == 2 and counter == 12:
            data = text_Message(
                number, "Muchas gracias por toda su informacion, se le enviara un correo indicando su status.")
            list.append(data)
            base.modificar_posicion(number, counter)
        else:
            data = text_Message(
                number, "Solamente se puede ingresar una solicitud por numero de telefono. 😁")
            list.append(data)
    else:
        if number in sett.administradores:
            # Recuperamos el counter de admin para saber en que paso se encuentra
            admin_counter = base.get_counter_admin_mode(number)
            print('admin counter: ', admin_counter)
            if admin_counter == 0:
                # En esta parte es cuando se les manda el menasje sobre la propuesta
                limite_inferior, limite_superior = base.get_rango_de_evaluacion(
                    number)
                print('inf', limite_inferior, limite_superior)
                indice = base.get_indice_dentro_del_rango(
                    number, limite_inferior)
                print('indiece', indice)
                # Mantenemos las inspecciones dentro del rango indicado.
                if (limite_superior - limite_inferior) + 1 >= indice:

                    if 'empezar' in text:
                        print(indice)
                        body = base.get_solo_una_informacion(indice + 1)
                        footer = f"Propuesta No. {indice}"
                        options = ["✅ Aceptar", "❌ Rechazar"]
                        replyButtonData = buttonReply_Message(
                            number, options, body, footer, "sed1")
                        list.append(replyButtonData)

                    elif 'continuar' in text:
                        print(indice)
                        body = base.get_solo_una_informacion(indice + 1)
                        footer = f"Propuesta No. {indice}"
                        options = ["✅ Aceptar", "❌ Rechazar"]
                        replyButtonData = buttonReply_Message(
                            number, options, body, footer, "sed1")
                        list.append(replyButtonData)

                    if 'aceptar' in text:
                        print(indice + 1)
                        base.update_indices(number, indice + 1)
                        base.set_status(indice, 1)
                        body = 'Siguiente propuesta.'
                        footer = f"Propuesta No. {indice}"
                        options = ["✅ Continuar"]
                        replyButtonData = buttonReply_Message(
                            number, options, body, footer, "sed1")
                        list.append(replyButtonData)
                        # Aqui se cambia el estatus en caso de ser aceptado 
                    if 'rechazar' in text:
                        base.update_indices(number, indice + 1)
                        base.set_status(indice, 0)
                        body = 'Presiona continuar para ver la siguiente propuesta.'
                        footer = f"Propuesta No. {indice}"
                        options = ["✅ Continuar"]
                        replyButtonData = buttonReply_Message(
                            number, options, body, footer, "sed1")
                        list.append(replyButtonData)
                else:
                    message = "Gracias por resolver tu parte del trabajo."
                    enviar_Mensaje_whatsapp(text_Message(number, message))
            else: 
                # Se le suma uno al counter del admin
                base.set_counter_admin_mode(number, admin_counter)
    for item in list:
        print(item)
        enviar_Mensaje_whatsapp(item)
