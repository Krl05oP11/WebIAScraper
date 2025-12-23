#!/usr/bin/env python3
"""
Script para limpiar mensajes duplicados en canal de Telegram

Estrategia:
1. Obtener información del canal para saber cuántos mensajes hay
2. Eliminar mensajes desde el más reciente hacia atrás
3. Conservar solo los últimos N mensajes únicos (que no sean duplicados)
"""

import requests
import time
import sys

BOT_TOKEN = "8373359883:AAF41sFLMJDMVVodAKYEQ_jwezrDPimUlo0"
CHANNEL_ID = "-1003454134750"

def get_message_count():
    """Obtener número aproximado de mensajes en el canal"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    params = {"chat_id": CHANNEL_ID}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        print(f"📊 Información del canal:")
        print(f"   Título: {data['result']['title']}")
        print(f"   Username: @{data['result']['username']}")
        return True
    return False

def delete_message(message_id):
    """Eliminar un mensaje específico"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
    params = {
        "chat_id": CHANNEL_ID,
        "message_id": message_id
    }

    response = requests.post(url, json=params)
    result = response.json()

    return result.get('ok', False)

def delete_range(start_id, end_id):
    """Eliminar un rango de mensajes"""
    print(f"\n🗑️  Eliminando mensajes desde ID {start_id} hasta {end_id}...")
    print(f"   Total a eliminar: {end_id - start_id + 1} mensajes\n")

    deleted = 0
    failed = 0

    for msg_id in range(start_id, end_id + 1):
        if delete_message(msg_id):
            deleted += 1
            if deleted % 10 == 0:
                print(f"   ✅ Eliminados: {deleted}/{end_id - start_id + 1}")
        else:
            failed += 1

        # Rate limiting - no más de 20 requests por segundo
        time.sleep(0.05)

    print(f"\n📊 Resumen:")
    print(f"   ✅ Eliminados exitosamente: {deleted}")
    print(f"   ❌ Fallidos: {failed}")

    return deleted

def main():
    print("=" * 70)
    print("🧹 LIMPIEZA DE MENSAJES DUPLICADOS EN TELEGRAM")
    print("=" * 70)

    # Verificar acceso al canal
    if not get_message_count():
        print("❌ Error: No se pudo acceder al canal")
        return

    print("\n" + "=" * 70)
    print("⚠️  OPCIONES DE LIMPIEZA")
    print("=" * 70)

    print("\nEl mensaje pinneado de disclaimer es el ID: 374")
    print("Los mensajes duplicados están DESPUÉS de ese mensaje.\n")

    print("Opciones:")
    print("  1) Eliminar TODOS los mensajes (excepto pinneado)")
    print("  2) Eliminar mensajes desde un ID específico hasta el más reciente")
    print("  3) Eliminar los últimos N mensajes")
    print("  4) Cancelar (no eliminar nada)")

    opcion = input("\nSelecciona una opción (1-4): ").strip()

    if opcion == "1":
        # Eliminar todo excepto el mensaje pinneado (374)
        print("\n⚠️  ADVERTENCIA: Esto eliminará TODOS los mensajes excepto el pinneado (ID 374)")
        confirmacion = input("¿Estás seguro? Escribe 'SI' para continuar: ").strip()

        if confirmacion == "SI":
            # Asumiendo que el último mensaje es ~374 + 300 = 674
            last_id = int(input("¿Cuál es el ID del último mensaje aproximadamente? (ej: 674): "))
            delete_range(375, last_id)  # Desde después del pinneado hasta el final
        else:
            print("❌ Cancelado")

    elif opcion == "2":
        start = int(input("ID del primer mensaje a eliminar: "))
        end = int(input("ID del último mensaje a eliminar: "))

        print(f"\n⚠️  Se eliminarán {end - start + 1} mensajes (ID {start} a {end})")
        confirmacion = input("¿Continuar? Escribe 'SI': ").strip()

        if confirmacion == "SI":
            delete_range(start, end)
        else:
            print("❌ Cancelado")

    elif opcion == "3":
        n = int(input("¿Cuántos mensajes eliminar desde el más reciente?: "))
        last_id = int(input("¿Cuál es el ID del último mensaje aproximadamente?: "))

        start = last_id - n + 1
        print(f"\n⚠️  Se eliminarán {n} mensajes (ID {start} a {last_id})")
        confirmacion = input("¿Continuar? Escribe 'SI': ").strip()

        if confirmacion == "SI":
            delete_range(start, last_id)
        else:
            print("❌ Cancelado")

    else:
        print("❌ Operación cancelada")

    print("\n✅ Proceso completado")
    print("👉 Verifica el canal en: https://t.me/schallerponce")

if __name__ == "__main__":
    main()
