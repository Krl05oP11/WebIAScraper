#!/usr/bin/env python3
"""
Script de migración de noticias de PostgreSQL local a Supabase
Migra todas las noticias procesadas de la base de datos local a Supabase vía REST API
"""

import os
import sys
import json
import requests
from datetime import datetime

# Colores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

# Cargar credenciales de Supabase
def load_supabase_config():
    """Carga las credenciales de Supabase desde el archivo de configuración"""
    config_file = os.path.expanduser('~/.webiascrap_supabase_config')

    if not os.path.exists(config_file):
        print_error("Archivo de configuración de Supabase no encontrado")
        print_warning(f"Se esperaba: {config_file}")
        sys.exit(1)

    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                config[key] = value

    return config

# URLs
LOCAL_API_URL = 'http://localhost:8001/api/apublicar'

def get_local_news():
    """Obtiene noticias procesadas desde la API local"""
    try:
        print_info("Obteniendo noticias procesadas de WebIAScrap local...")
        response = requests.get(LOCAL_API_URL, timeout=10)
        response.raise_for_status()
        news = response.json()

        # Filtrar solo las procesadas con traducción
        processed = [n for n in news if n.get('procesado') and n.get('titulo_es')]
        print_success(f"Encontradas {len(processed)} noticias procesadas")
        return processed
    except requests.exceptions.ConnectionError:
        print_error("No se pudo conectar a WebIAScrap local")
        print_warning("Asegúrate de que WebIAScrap esté corriendo en http://localhost:8001")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error al obtener noticias locales: {e}")
        sys.exit(1)

def prepare_news_for_supabase(noticia):
    """Convierte una noticia del formato local al formato Supabase"""
    # Convertir temas de lista a array PostgreSQL si es necesario
    temas = noticia.get('temas', [])
    if not isinstance(temas, list):
        temas = []

    return {
        'titulo': noticia.get('titulo'),
        'texto': noticia.get('texto'),
        'url': noticia.get('url'),
        'fecha_hora': noticia.get('fecha_hora'),
        'temas': temas,
        'noticia_id': noticia.get('noticia_id'),
        'titulo_es': noticia.get('titulo_es'),
        'texto_es': noticia.get('texto_es'),
        'resumen_corto': noticia.get('resumen_corto'),
        'resumen_medio': noticia.get('resumen_medio'),
        'resumen_largo': noticia.get('resumen_largo'),
        'hashtags': noticia.get('hashtags'),
        'categoria': noticia.get('categoria'),
        'procesado': noticia.get('procesado', False),
        'publicado': noticia.get('publicado', False),
        'plataformas_seleccionadas': noticia.get('plataformas_seleccionadas'),
        'plataformas_publicadas': noticia.get('plataformas_publicadas'),
        'intentos_publicacion': noticia.get('intentos_publicacion', 0),
        'ultimo_error': noticia.get('ultimo_error'),
        'fase': noticia.get('fase', 'pendiente'),
        'contador_reintentos': noticia.get('contador_reintentos', 0),
        'ultimo_intento': noticia.get('ultimo_intento'),
        'proximo_reintento': noticia.get('proximo_reintento'),
        'selected_at': noticia.get('selected_at'),
        'processed_at': noticia.get('processed_at'),
        'published_at': noticia.get('published_at'),
        'expires_at': noticia.get('expires_at'),
        'publicada_en_website': True  # Marcar como publicada en website
    }

def migrate_to_supabase(news, config):
    """Migra noticias a Supabase usando la REST API"""
    if not news:
        print_warning("No hay noticias para migrar")
        return 0

    supabase_url = config['SUPABASE_URL']
    service_key = config['SUPABASE_SERVICE_KEY']

    print()
    print_info(f"Migrando {len(news)} noticias a Supabase...")
    print()

    inserted = 0
    updated = 0
    errors = 0

    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
    }

    for i, noticia in enumerate(news, 1):
        titulo_display = noticia.get('titulo_es') or noticia.get('titulo') or 'Sin título'
        print_info(f"[{i}/{len(news)}] {titulo_display[:60]}...")

        # Preparar datos
        data = prepare_news_for_supabase(noticia)

        try:
            # Primero verificar si existe
            check_url = f"{supabase_url}/rest/v1/apublicar?url=eq.{requests.utils.quote(noticia['url'])}&select=id"
            check_response = requests.get(check_url, headers=headers)

            if check_response.status_code == 200 and check_response.json():
                # Actualizar existente
                existing_id = check_response.json()[0]['id']
                update_url = f"{supabase_url}/rest/v1/apublicar?id=eq.{existing_id}"
                response = requests.patch(update_url, headers=headers, json=data)

                if response.status_code in [200, 204]:
                    updated += 1
                    print_warning(f"  → Actualizada")
                else:
                    print_error(f"  → Error al actualizar: {response.status_code} - {response.text[:100]}")
                    errors += 1
            else:
                # Insertar nueva
                insert_url = f"{supabase_url}/rest/v1/apublicar"
                response = requests.post(insert_url, headers=headers, json=data)

                if response.status_code in [200, 201]:
                    inserted += 1
                    print_success(f"  → Insertada (nueva)")
                else:
                    print_error(f"  → Error al insertar: {response.status_code} - {response.text[:100]}")
                    errors += 1

        except Exception as e:
            print_error(f"  → Error: {e}")
            errors += 1
            continue

    print()
    print_success("=== MIGRACIÓN COMPLETADA ===")
    print_success(f"✨ Noticias nuevas insertadas: {inserted}")
    if updated > 0:
        print_warning(f"🔄 Noticias actualizadas: {updated}")
    if errors > 0:
        print_error(f"❌ Errores: {errors}")

    return inserted + updated

def main():
    print()
    print("=" * 70)
    print("  🔄 MIGRACIÓN DE NOTICIAS: WebIAScrap Local → Supabase")
    print("=" * 70)
    print()

    # Cargar configuración de Supabase
    config = load_supabase_config()
    print_success("Configuración de Supabase cargada")

    # Obtener noticias de la API local
    news = get_local_news()

    # Migrar
    try:
        total = migrate_to_supabase(news, config)

        if total > 0:
            print()
            print_success(f"✅ Migración exitosa: {total} noticias")
            print()
            print_info("🌐 Las noticias ya están disponibles en Supabase")
            print_info("   Próximo paso: Actualizar el frontend del website")
            print()
        else:
            print()
            print_warning("No se migró ninguna noticia nueva")
            print()
    except Exception as e:
        print_error(f"Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print_info("✨ ¡Listo! Puedes cerrar esta ventana.")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Migración cancelada por el usuario")
        sys.exit(0)
