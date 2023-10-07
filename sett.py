import mysql.connector

token = 'compasion'

whatsapp_token = 'EAAJS5K3iTeQBOw8AAbGlT0x3GE3jsKWcQExGusSh4uPACRZAl1OXJ63WioBiVEK68NJzmCYYgMI6cktZC3ZCFFLWfXurkhydZBWM65XbugqPCegIRLiZCZCdIhmRL0wxrNdP89X4m20IzCPFtxXTI28E6YPz3PJHqpta4SP0wpjjCfUqVPPZCgSDlHqfS6Qo1XT3GxjWHpZAvqFQXeEOd5sZD'

whatsapp_url = 'https://graph.facebook.com/v17.0/129471620252420/messages'

stickers = {
    "poyo_feliz": 984778742532668,
    "perro_traje": 1009219236749949,
    "perro_triste": 982264672785815,
    "pedro_pascal_love": 801721017874258,
    "pelfet": 3127736384038169,
    "anotado": 24039533498978939,
    "gato_festejando": 1736736493414401,
    "okis": 268811655677102,
    "cachetada": 275511571531644,
    "gato_juzgando": 107235069063072,
    "chicorita": 3431648470417135,
    "gato_triste": 210492141865964,
    "gato_cansado": 1021308728970759
}

document_url = "https://www.africau.edu/images/default/sample.pdf"


connection = mysql.connector.connect(
    host="mysql-javiertevillo.alwaysdata.net",
    user="324312",
    password="Mecatr0nica",
    database='javiertevillo_chat'
)
