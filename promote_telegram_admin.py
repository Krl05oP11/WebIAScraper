#!/usr/bin/env python3
"""
Script para promover usuario a administrador del canal de Telegram

Uso:
    python3 promote_telegram_admin.py YOUR_USER_ID
"""

import requests
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.social_publisher')

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

if not BOT_TOKEN or not CHANNEL_ID:
    print("❌ Error: TELEGRAM_BOT_TOKEN o TELEGRAM_CHANNEL_ID no encontrados")
    exit(1)

if len(sys.argv) < 2:
    print("❌ Error: Debes proporcionar tu USER_ID")
    print("Uso: python3 promote_telegram_admin.py YOUR_USER_ID")
    exit(1)

user_id = sys.argv[1]

print(f"\n🔧 Promoviendo usuario {user_id} como administrador del canal {CHANNEL_ID}...\n")

# API endpoint
url = f"https://api.telegram.org/bot{BOT_TOKEN}/promoteChatMember"

# Parámetros con TODOS los permisos de administrador
params = {
    'chat_id': CHANNEL_ID,
    'user_id': user_id,
    'can_manage_chat': True,
    'can_post_messages': True,
    'can_edit_messages': True,
    'can_delete_messages': True,
    'can_manage_video_chats': True,
    'can_restrict_members': True,
    'can_promote_members': True,
    'can_change_info': True,
    'can_invite_users': True,
    'can_pin_messages': True,
}

# Hacer la solicitud
response = requests.post(url, json=params)

if response.status_code == 200:
    result = response.json()

    if result.get('ok'):
        print("✅ ¡Éxito! Usuario promovido a administrador con todos los permisos")
        print("\nPermisos otorgados:")
        print("  ✅ Gestionar chat")
        print("  ✅ Publicar mensajes")
        print("  ✅ Editar mensajes")
        print("  ✅ Eliminar mensajes")
        print("  ✅ Gestionar videochats")
        print("  ✅ Restringir miembros")
        print("  ✅ Promover miembros")
        print("  ✅ Cambiar info del canal")
        print("  ✅ Invitar usuarios")
        print("  ✅ Fijar mensajes")
        print("\n👉 Ahora puedes configurar la descripción del canal desde tu app de Telegram")
    else:
        print(f"❌ Error en la respuesta: {result.get('description', 'Unknown error')}")
        print(f"Detalles: {result}")
else:
    print(f"❌ Error HTTP {response.status_code}")
    print(response.text)
