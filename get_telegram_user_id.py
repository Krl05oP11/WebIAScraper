#!/usr/bin/env python3
"""
Script para obtener el user_id de Telegram
Instrucciones:
1. Envía un mensaje a tu bot @WebIAScrapperBot
2. Ejecuta este script
3. Verás tu user_id
"""

import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.social_publisher')

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ Error: TELEGRAM_BOT_TOKEN no encontrado en .env.social_publisher")
    exit(1)

# Obtener las últimas actualizaciones (mensajes)
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    if data['result']:
        print("\n📨 Últimos mensajes recibidos por el bot:\n")

        for update in data['result'][-5:]:  # Últimos 5
            if 'message' in update:
                msg = update['message']
                user = msg.get('from', {})

                print(f"👤 Usuario: {user.get('first_name', '')} {user.get('last_name', '')}")
                print(f"   Username: @{user.get('username', 'N/A')}")
                print(f"   🆔 USER ID: {user.get('id')}")
                print(f"   Mensaje: {msg.get('text', 'N/A')}")
                print("-" * 60)
    else:
        print("⚠️  No hay mensajes recientes.")
        print("👉 Envía un mensaje a @WebIAScrapperBot y vuelve a ejecutar este script")
else:
    print(f"❌ Error al obtener actualizaciones: {response.status_code}")
    print(response.text)
