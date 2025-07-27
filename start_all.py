#!/usr/bin/env python
"""
Script para iniciar tanto el bot como el panel de administración Flask
"""
import asyncio
import subprocess
import sys
import os
import time
from threading import Thread

def start_panel():
    """Inicia el panel de administración Flask"""
    try:
        print("🚀 Iniciando Panel de Administración Flask...")
        subprocess.run([sys.executable, "panel_admin.py"], check=True)
    except KeyboardInterrupt:
        print("🛑 Panel detenido")
    except Exception as e:
        print(f"❌ Error iniciando panel: {e}")

def start_bot():
    """Inicia el bot de Telegram"""
    try:
        print("🤖 Iniciando Bot de Telegram...")
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("🛑 Bot detenido")
    except Exception as e:
        print(f"❌ Error iniciando bot: {e}")

def main():
    """Función principal"""
    print("🐉 Mundo Mítico - Sistema Completo (Flask)")
    print("=" * 50)
    
    # Verificar que estamos en el entorno virtual
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Advertencia: No estás en un entorno virtual")
        print("   Se recomienda activar el entorno virtual primero")
        input("   Presiona Enter para continuar...")
    
    print("\n📋 Opciones disponibles:")
    print("1. Iniciar solo el Bot")
    print("2. Iniciar solo el Panel Admin (Flask)")
    print("3. Iniciar ambos (Bot + Panel)")
    print("4. Salir")
    
    while True:
        try:
            opcion = input("\nSelecciona una opción (1-4): ").strip()
            
            if opcion == "1":
                print("\n🤖 Iniciando solo el Bot...")
                start_bot()
                break
                
            elif opcion == "2":
                print("\n🚀 Iniciando solo el Panel Admin Flask...")
                start_panel()
                break
                
            elif opcion == "3":
                print("\n🚀 Iniciando Bot + Panel Admin Flask...")
                print("📊 Panel Admin: http://localhost:8000")
                print("🤖 Bot: Ejecutándose en segundo plano")
                
                # Iniciar panel en un hilo separado
                panel_thread = Thread(target=start_panel, daemon=True)
                panel_thread.start()
                
                # Esperar un poco para que el panel inicie
                time.sleep(3)
                
                # Iniciar bot en el hilo principal
                start_bot()
                break
                
            elif opcion == "4":
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción inválida. Selecciona 1, 2, 3 o 4.")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 