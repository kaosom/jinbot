import requests
import sett
import json
import time

counter = 0


def modificar_counter(step=None):
    global counter
    if step is None:
        counter += 1
    else:
        counter = step


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
        response = requests.post(whatsapp_url,
                                 headers=headers,
                                 data=data)

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


def buttonReply_Message(number, options, body, footer, sedd, messageId):
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


def listReply_Message(number, options, body, footer, sedd, messageId):
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


def document_Message(number, url, caption, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": url,
                "caption": caption,
                "filename": filename
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
    # elif media_type == "image":
    #    media_id = sett.images.get(media_name, None)
    # elif media_type == "video":
    #    media_id = sett.videos.get(media_name, None)
    # elif media_type == "audio":
    #    media_id = sett.audio.get(media_name, None)
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


def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data


def administrar_chatbot(text, number, messageId):
    text = text.lower()  # mensaje que envio el usuario
    list = []
    print("$ ", text)

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    if counter == 0:
        body = "¡Hola! 👋 Bienvenido a ConPasion. ¿Cómo podemos ayudarte hoy?"
        footer = "Equipo Compasion"
        options = ["✅ Manual", "📅 Quienes somos"]

        replyButtonData = buttonReply_Message(
            number, options, body, footer, "sed1", messageId)
        replyReaction = replyReaction_Message(number, messageId, "🫡")
        list.append(replyReaction)
        list.append(replyButtonData)
        modificar_counter()
    elif "manual" in text and len(text.split()) == 2 and counter == 1:
        body = "En el orden que se te vaya pidiendo deberás escribir los siguientes datos:\n1. Nombre del proyecto que requiere un apoyo economico.\n2. Justificacion del proyecto (menos de 100 palabras)\n3.Cantidad de dinero.\n4. Video subido a YT para mostrar el proyecto.\n5. Correo para mandar resultados."
        footer = "ComPasion Contigo."
        options = ["✅ Empezar",
                   "❌ Cancelar"]

        replyButtonData = buttonReply_Message(
            number, options, body, footer, "sed2", messageId)
        sticker = sticker_Message(
            number, get_media_id("perro_traje", "sticker"))

        list.append(replyButtonData)
        list.append(sticker)
        modificar_counter()
    elif "quienes somos" in text and len(text.split()) == 3 and counter == 1:
        pass
    elif "empezar" in text and len(text.split()) == 2 and counter == 2:
        data = text_Message(
            number, "Por favor escribe el nombre del proyecto.😊")
        list.append(data)
        modificar_counter()
    elif counter == 3:
        print('Dato a guardar en la base: ', text)
        body = "Nombre registrado correctamente.\nQuieres modificar el nombre o continuar?"
        footer = "Equipo ComPasion"
        options = ["✅ Continuar", "❌ Modificar"]

        buttonReply = buttonReply_Message(
            number, options, body, footer, "sed3", messageId)
        list.append(buttonReply)
        modificar_counter()
    elif "cancelar" in text and len(text.split()) == 2:
        data = text_Message(
            number, "Operacion cancelada. Que tengas un buen día. 😊")
        list.append(data)
    elif "modificar" in text and len(text.split()) == 2 and counter == 4:
        data = text_Message(
            number, "Escribe nuevamente el nombre. 😊")
        list.append(data)
        modificar_counter(step=3)
    elif "continuar" in text and len(text.split()) == 2 and counter == 4:
        data = text_Message(
            number, "Por favor escribe la justificacion.😊")
        list.append(data)
        modificar_counter()
    elif counter == 5:
        if len(text.split()) > 100:
            data = text_Message(
                number, "Recuerda que tienen que ser menos de 100 palabras. Por favor vuelve a escribirla.😊")
            list.append(data)
        else:
            print('Dato a guardar en la base: ', text)
            body = "Justificacion registrado correctamente.\nQuieres modificar el nombre o continuar?"
            footer = "Equipo ComPasion"
            options = ["✅ Continuar", "❌ Modificar"]

            buttonReply = buttonReply_Message(
                number, options, body, footer, "sed3", messageId)
            list.append(buttonReply)
            modificar_counter()
    elif "modificar" in text and len(text.split()) == 2 and counter == 6:
        data = text_Message(
            number, "Escribe nuevamente la justificacion. 😊")
        list.append(data)
        modificar_counter(step=5)
    elif "continuar" in text and len(text.split()) == 2 and counter == 6:
        data = text_Message(
            number, "Por favor escribe la cantidad de dinero.😊")
        list.append(data)
        modificar_counter()

    elif counter == 7:
        print('Dato a guardar en la base: ', text)
        body = "Cantidad de dinero registrada.\nQuieres modificar la cantidad de dinero o continuar?"
        footer = "Equipo ComPasion"
        options = ["✅ Continuar", "❌ Modificar"]
        buttonReply = buttonReply_Message(
            number, options, body, footer, "sed3", messageId)
        list.append(buttonReply)
        modificar_counter()
    elif "modificar" in text and len(text.split()) == 2 and counter == 8:
        data = text_Message(
            number, "Escribe nuevamente la cantidad de dinero. 😊")
        list.append(data)
        modificar_counter(step=7)
    elif "continuar" in text and len(text.split()) == 2 and counter == 8:
        data = text_Message(
            number, "Ingrese unicamente la URL del video de YouTube.😊")
        list.append(data)
        modificar_counter()

    elif counter == 9:
        if 'https://www.youtube.com/' in text:
            body = "Video registrado.\nQuieres modificar la url o continuar?"
            footer = "Equipo ComPasion"
            options = ["✅ Continuar", "❌ Modificar"]
            buttonReply = buttonReply_Message(
                number, options, body, footer, "sed3", messageId)
            list.append(buttonReply)
            modificar_counter()
            print('Dato a guardar en la base: ', text)
        else:
            data = text_Message(
                number, "Recuerda que tiene que ser un link de YouTube valido.😊")
            list.append(data)
    elif "modificar" in text and len(text.split()) == 2 and counter == 10:
        data = text_Message(
            number, "Escribe nuevamente la URL. 😊")
        list.append(data)
        modificar_counter(step=9)
    elif "continuar" in text and len(text.split()) == 2 and counter == 10:
        data = text_Message(
            number, "Ingrese su correo electronico.")
        list.append(data)
        modificar_counter()

    elif counter == 11:
        if '@' in text:
            print('Dato a guardar en la base: ', text)
            body = "Correo registrado.\nQuieres modificar el correo o continuar?"
            footer = "Equipo ComPasion"
            options = ["✅ Continuar", "❌ Modificar"]
            buttonReply = buttonReply_Message(
                number, options, body, footer, "sed3", messageId)
            list.append(buttonReply)
            modificar_counter()
        else:
            data = text_Message(
                number, "Recuerda que tiene que ser un correo valido.😊")
            list.append(data)
    elif "modificar" in text and len(text.split()) == 2 and counter == 12:
        data = text_Message(
            number, "Escribe nuevamente el correo. 😊")
        list.append(data)
        modificar_counter(step=11)
    elif "continuar" in text and len(text.split()) == 2 and counter == 12:
        data = text_Message(
            number, "Muchas gracias por toda su informacion, se le enviara un correo indicando su status.")
        list.append(data)
        modificar_counter()

    elif counter > 12:
        data = text_Message(
            number, 'Que tengas un gran dia')
        list.append(data)
        modificar_counter(step=0)

    else:
        data = text_Message(
            number, "Por favor ingresa alguna de las opciones indicadas. 😬")
        list.append(data)

    for item in list:
        enviar_Mensaje_whatsapp(item)


def replace_start(s):
    if s.startswith("521"):
        return "52" + s[3:]
    else:
        return s
