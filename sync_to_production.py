#!/usr/bin/env python3
"""
Script de sincronización de noticias: Local → Render (Producción)

Sincroniza noticias procesadas desde WebIAScrap local (via API)
a la base de datos de producción en Render.com
"""

import os
import sys
import json
import requests
import psycopg2
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

# URLs
LOCAL_API_URL = 'http://localhost:8000/api/apublicar'

# La URL de producción la pediremos al usuario la primera vez
RENDER_DB_FILE = os.path.expanduser('~/.webiascrap_render_db')

def get_render_db_url():
    """Obtiene la URL de la BD de Render (la guarda para uso futuro)"""
    if os.path.exists(RENDER_DB_FILE):
        with open(RENDER_DB_FILE, 'r') as f:
            return f.read().strip()

    print_info("Primera vez usando el sincronizador")
    print_info("Necesito la 'External Database URL' de Render")
    print()
    print("Pasos para obtenerla:")
    print("1. Ve a https://dashboard.render.com")
    print("2. Abre 'n8n-database' (PostgreSQL)")
    print("3. Busca 'External Database URL'")
    print("4. Cópiala y pégala aquí")
    print()
    print("Ejemplo: postgresql://user:pass@dpg-xxx.oregon-postgres.render.com/database")
    print()

    url = input("Pega la External Database URL: ").strip()

    if not url.startswith('postgresql://') and not url.startswith('postgres://'):
        print_error("URL inválida. Debe empezar con 'postgresql://' o 'postgres://'")
        sys.exit(1)

    # Cambiar el nombre de la database a 'webiascrap' si termina en otro nombre
    if '/' in url:
        base_url = url.rsplit('/', 1)[0]
        url = f"{base_url}/webiascrap"

    # Guardar para uso futuro
    with open(RENDER_DB_FILE, 'w') as f:
        f.write(url)

    os.chmod(RENDER_DB_FILE, 0o600)  # Solo lectura/escritura para el usuario
    print_success("URL guardada de forma segura")
    return url

def get_local_news():
    """Obtiene noticias procesadas desde la API local"""
    try:
        response = requests.get(LOCAL_API_URL, timeout=10)
        response.raise_for_status()
        news = response.json()

        # Filtrar solo las procesadas con traducción
        processed = [n for n in news if n.get('procesado') and n.get('titulo_es')]
        return processed
    except requests.exceptions.ConnectionError:
        print_error("No se pudo conectar a WebIAScrap local")
        print_warning("Asegúrate de que WebIAScrap esté corriendo (Docker)")
        print_warning("Prueba abrir: http://localhost:8000")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error al obtener noticias locales: {e}")
        sys.exit(1)

def connect_render(url):
    """Conecta a la base de datos de Render"""
    try:
        conn = psycopg2.connect(url)
        return conn
    except Exception as e:
        print_error(f"No se pudo conectar a Render: {e}")
        print_warning("Verifica que la URL sea correcta")
        print_warning("Puedes eliminar ~/.webiascrap_render_db y volver a intentar")
        sys.exit(1)

def sync_news(news, render_conn):
    """Sincroniza noticias a Render (tabla apublicar)"""
    if not news:
        print_warning("No hay noticias procesadas para sincronizar")
        return 0

    print_success(f"Encontradas {len(news)} noticias procesadas")
    print()

    render_cursor = render_conn.cursor()

    # LÍMITE MÁXIMO de noticias en producción
    MAX_NOTICIAS = 30

    # Contar noticias actuales en producción
    render_cursor.execute("SELECT COUNT(*) FROM apublicar WHERE publicada_en_website = TRUE")
    count_result = render_cursor.fetchone()
    noticias_actuales = count_result[0] if count_result else 0

    print_info(f"Noticias actuales en producción: {noticias_actuales}/{MAX_NOTICIAS}")

    # Calcular cuántas noticias nuevas vamos a insertar (sin duplicados)
    urls_nuevas = [n.get('url') for n in news]
    render_cursor.execute(
        "SELECT COUNT(*) FROM apublicar WHERE url = ANY(%s)",
        (urls_nuevas,)
    )
    duplicados = render_cursor.fetchone()[0]
    noticias_a_insertar = len(news) - duplicados

    print_info(f"Noticias nuevas a insertar: {noticias_a_insertar}")

    # Si después de insertar superaríamos el límite, eliminar las más viejas
    total_despues = noticias_actuales + noticias_a_insertar
    if total_despues > MAX_NOTICIAS:
        cantidad_a_eliminar = total_despues - MAX_NOTICIAS
        print_warning(f"Se eliminarán las {cantidad_a_eliminar} noticias más antiguas para mantener límite de {MAX_NOTICIAS}")

        delete_query = """
            DELETE FROM apublicar
            WHERE id IN (
                SELECT id FROM apublicar
                WHERE publicada_en_website = TRUE
                ORDER BY fecha_hora ASC, selected_at ASC
                LIMIT %s
            )
        """
        render_cursor.execute(delete_query, (cantidad_a_eliminar,))
        eliminadas = render_cursor.rowcount
        print_warning(f"  → {eliminadas} noticias antiguas eliminadas")
        render_conn.commit()

    # Insertar/actualizar noticias
    inserted = 0
    updated = 0

    for i, noticia in enumerate(news, 1):
        titulo_display = noticia.get('titulo_es') or noticia.get('titulo') or 'Sin título'
        print_info(f"[{i}/{len(news)}] {titulo_display[:60]}...")

        # Verificar si ya existe (por URL)
        render_cursor.execute("SELECT id FROM apublicar WHERE url = %s", (noticia.get('url'),))
        existing = render_cursor.fetchone()

        if existing:
            # Actualizar (marcar como publicada en website)
            update_query = """
                UPDATE apublicar
                SET titulo = %s, titulo_es = %s, texto = %s, texto_es = %s,
                    resumen_largo = %s, hashtags = %s, categoria = %s, temas = %s,
                    procesado = %s, publicado = %s, processed_at = %s,
                    publicada_en_website = TRUE
                WHERE url = %s
            """
            render_cursor.execute(update_query, (
                noticia.get('titulo'), noticia.get('titulo_es'),
                noticia.get('texto'), noticia.get('texto_es'),
                noticia.get('resumen_largo'), noticia.get('hashtags'),
                noticia.get('categoria'), noticia.get('temas'),
                noticia.get('procesado'), noticia.get('publicado'),
                noticia.get('processed_at'), noticia.get('url')
            ))
            updated += 1
            print_warning(f"  → Actualizada")
        else:
            # Insertar nueva noticia
            insert_query = """
                INSERT INTO apublicar (
                    titulo, titulo_es, texto, texto_es, url, fecha_hora,
                    resumen_largo, hashtags, categoria, temas,
                    procesado, publicado, selected_at, processed_at,
                    publicada_en_website
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE
                )
            """
            try:
                render_cursor.execute(insert_query, (
                    noticia.get('titulo'), noticia.get('titulo_es'),
                    noticia.get('texto'), noticia.get('texto_es'),
                    noticia.get('url'), noticia.get('fecha_hora'),
                    noticia.get('resumen_largo'), noticia.get('hashtags'),
                    noticia.get('categoria'), noticia.get('temas'),
                    noticia.get('procesado'), noticia.get('publicado'),
                    noticia.get('selected_at'), noticia.get('processed_at')
                ))
                inserted += 1
                print_success(f"  → Insertada (nueva)")
            except psycopg2.errors.UniqueViolation:
                render_conn.rollback()
                print_warning(f"  → Ya existe (omitida)")
                continue
            except Exception as e:
                render_conn.rollback()
                print_error(f"  → Error: {e}")
                continue

    render_conn.commit()
    render_cursor.close()

    print()
    print_success("=== SINCRONIZACIÓN COMPLETADA ===")
    print_success(f"✨ Noticias nuevas insertadas: {inserted}")
    if updated > 0:
        print_warning(f"🔄 Noticias actualizadas: {updated}")

    return inserted + updated

def main():
    print()
    print("=" * 70)
    print("  🔄 SINCRONIZADOR DE NOTICIAS: WebIAScrap Local → Render")
    print("=" * 70)
    print()

    # Obtener noticias de la API local
    print_info("Obteniendo noticias procesadas de WebIAScrap local...")
    news = get_local_news()

    # Conectar a Render
    render_url = get_render_db_url()
    print_info("Conectando a Render...")
    render_conn = connect_render(render_url)
    print_success("Conectado a Render")
    print()

    # Sincronizar
    try:
        total = sync_news(news, render_conn)

        if total > 0:
            print()
            print_success(f"✅ Sincronización exitosa: {total} noticias")
            print()
            print_info("🌐 Las noticias ya están disponibles en:")
            print_info("   https://schaller-ponce.com.ar → Menú 'Noticias'")
            print()
        else:
            print()
            print_warning("No se sincronizó ninguna noticia nueva")
            print()
    except Exception as e:
        print_error(f"Error durante la sincronización: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        render_conn.close()

    print_info("✨ ¡Listo! Puedes cerrar esta ventana.")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Sincronización cancelada por el usuario")
        sys.exit(0)
