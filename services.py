import requests
import sett
import json
import time
import mysql.connector


class DB:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="mysql-javiertevillo.alwaysdata.net",
            user="324312",
            password="Mecatr0nica",
            database='javiertevillo_chat'
        )

        self.cursor = self.connection.cursor()
        print("Conexion exitosa.")

    def get_total(self):
        self.sql = "SELECT max(id) FROM database"
        try:
            self.cursor.execute(self.sql)
            self.value = self.cursor.fetchone()
            return self.value
        except Exception as e:
            print("Excepcion: ", e)

    def verificar_existencia(self, telefono):
        try:
            # Utiliza una consulta parametrizada para evitar la inyección SQL
            sql = "SELECT telefono FROM `database` WHERE telefono = %s"
            self.cursor.execute(sql, (telefono,))
            value = self.cursor.fetchone()

            # Si no se encuentra ningún registro, retorna False; de lo contrario, retorna True
            return value is not None
        except Exception as e:
            print("Excepción en verificar existencia:", e)
            return False  # Retorna False en caso de error

    def recuperar_posicion(self, telefono):
        if self.verificar_existencia(telefono):
            try:
                self.sql = f"SELECT counter FROM `database` WHERE telefono = %s"
                self.cursor.execute(self.sql, (telefono,))
                self.value = self.cursor.fetchone()
                if self.value is not None:
                    return self.value[0]
                else:
                    return 0
            except Exception as e:
                print("Exception en recuperar posicion: ", e)
        else:
            print("Retorno cero")
            return 0

    def modificar_posicion(self, telefono, counter, position=None):
        if position is None:
            if counter is not None:
                counter += 1
            self.insertar(telefono, counter, 'counter')
        else:
            counter = position
            self.insertar(telefono, position, 'counter')

    def insertar(self, telefono: str, valor, columna: str):
        if self.verificar_existencia(telefono):
            # Corregir la columna 'numero' a 'telefono'
            sql = f"UPDATE `database` SET {columna} = %s WHERE telefono = %s"
            # Usar 'sql' en lugar de 'self.sql'
            self.cursor.execute(sql, (valor, telefono))
        else:
            # Corregir la sintaxis de la inserción
            sql = f"INSERT INTO `database` (telefono, {columna}) VALUES (%s, %s)"
            # Intercambiar 'telefono' y 'valor' en la tupla de valores
            self.cursor.execute(sql, (telefono, valor))

        self.connection.commit()


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
    base = DB()
    counter = base.recuperar_posicion(number)
    if counter is None:
        counter = 0
    text = text.lower()  # mensaje que envio el usuario
    list = []
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
        base.modificar_posicion(number, counter)
        print("counter", counter)
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
            number, options, body, footer, "sed3", messageId)
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
                number, options, body, footer, "sed3", messageId)
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
            number, options, body, footer, "sed3", messageId)
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
        if 'https://www.youtube.com/' in text:
            body = "Video registrado.\nQuieres modificar la url o continuar?"
            footer = "Equipo ComPasion"
            options = ["✅ Continuar", "❌ Modificar"]
            buttonReply = buttonReply_Message(
                number, options, body, footer, "sed3", messageId)
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
                number, options, body, footer, "sed3", messageId)
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
            number, "Recuerda que solamente es una solicitud por numero de telefono.😬")
        list.append(data)

    for item in list:
        enviar_Mensaje_whatsapp(item)


def replace_start(s):
    if s.startswith("521"):
        return "52" + s[3:]
    else:
        return s
