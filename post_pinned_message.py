#!/usr/bin/env python3
"""
Script para publicar mensaje pinneado en Telegram
"""
import requests
import json

BOT_TOKEN = "8373359883:AAF41sFLMJDMVVodAKYEQ_jwezrDPimUlo0"
CHANNEL_ID = "-1003454134750"

# Mensaje de disclaimer (formato HTML)
mensaje = """⚠️ <b>AVISO IMPORTANTE - LEE ESTO PRIMERO</b> ⚠️

Este canal publica <b>RESÚMENES AUTOMÁTICOS</b> generados por IA de noticias sobre Inteligencia Artificial.

<b>✅ SÍ hacemos:</b>
• Resumir noticias con Claude AI
• Traducir al español
• Dar crédito completo a la fuente
• Incluir link al artículo original

<b>❌ NO hacemos:</b>
• Contenido original
• Garantizar 100% precisión
• Sustituir el artículo completo
• Infringir derechos de autor

📋 <b>SIEMPRE lee el artículo original</b> para información precisa y completa.

Disclaimer legal completo:
https://github.com/Krl05oP11/WebIAScraper/blob/main/LEGAL_DISCLAIMER.md

Si eres creador de contenido y no quieres aparecer aquí, escríbenos a:
<b>schaller.ponce@gmail.com</b>
Responderemos en 24-48h y eliminaremos tu contenido inmediatamente."""

# 1. Publicar el mensaje
print("📤 Publicando mensaje pinneado...")
url_send = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload_send = {
    "chat_id": CHANNEL_ID,
    "text": mensaje,
    "parse_mode": "HTML",
    "disable_web_page_preview": True
}

response = requests.post(url_send, json=payload_send)
result = response.json()

if result.get('ok'):
    message_id = result['result']['message_id']
    print(f"✅ Mensaje publicado con ID: {message_id}")

    # 2. Pinear el mensaje
    print("📌 Pineando mensaje...")
    url_pin = f"https://api.telegram.org/bot{BOT_TOKEN}/pinChatMessage"
    payload_pin = {
        "chat_id": CHANNEL_ID,
        "message_id": message_id,
        "disable_notification": False  # Notificar a suscriptores
    }

    response_pin = requests.post(url_pin, json=payload_pin)
    result_pin = response_pin.json()

    if result_pin.get('ok'):
        print("✅ Mensaje pinneado exitosamente")
        print(f"\n👉 Verifica en: https://t.me/schallerponce")
    else:
        print(f"❌ Error al pinear: {result_pin.get('description')}")
else:
    print(f"❌ Error al publicar: {result.get('description')}")
    print(json.dumps(result, indent=2))
