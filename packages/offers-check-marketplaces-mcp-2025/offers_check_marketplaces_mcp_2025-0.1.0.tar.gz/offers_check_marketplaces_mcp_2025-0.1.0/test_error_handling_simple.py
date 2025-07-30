"""
Простой тест обработки ошибок лицензии
"""
import os
import sys
import subprocess
from pathlib import Path

def test_license_error_handling():
    """Быстрый тест обработки ошибок лицензии"""
    
    print("=" * 60)
    print("ТЕСТ ОБРАБОТКИ ОШИБОК ЛИЦЕНЗИИ")
    print("=" * 60)
    
    # Тест 1: Без лицензионного ключа
    print("\n1. Тест без лицензионного ключа...")
    
    try:
        env = os.environ.copy()
        if 'LICENSE_KEY' in env:
            del env['LICENSE_KEY']
        
        result = subprocess.run([
            sys.executable, "-c", 
            "from offers_check_marketplaces.server import initialize_components; "
            "import asyncio; "
            "asyncio.run(initialize_components())"
        ], 
        env=env,
        capture_output=True,
        text=True,
        timeout=10
        )
        
        print(f"   Код завершения: {result.returncode}")
        
        if result.returncode == 1:
            print("✅ Программа корректно завершилась с кодом 1")
        else:
            print(f"❌ Неожиданный код завершения: {result.returncode}")
            print(f"   STDOUT: {result.stdout}")
            print(f"   STDERR: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Таймаут выполнения")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: С недействительным ключом
    print("\n2. Тест с недействительным ключом...")
    
    try:
        env = os.environ.copy()
        env['LICENSE_KEY'] = "invalid-key-12345"
        
        result = subprocess.run([
            sys.executable, "-c", 
            "from offers_check_marketplaces.server import initialize_components; "
            "import asyncio; "
            "asyncio.run(initialize_components())"
        ], 
        env=env,
        capture_output=True,
        text=True,
        timeout=15  # Увеличиваем таймаут для HTTP запроса
        )
        
        print(f"   Код завершения: {result.returncode}")
        
        if result.returncode == 1:
            print("✅ Программа корректно завершилась с кодом 1")
        else:
            print(f"❌ Неожиданный код завершения: {result.returncode}")
            print(f"   STDOUT: {result.stdout}")
            print(f"   STDERR: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Таймаут выполнения (возможно, долгий HTTP запрос)")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 3: С действительным ключом
    print("\n3. Тест с действительным ключом...")
    
    try:
        env = os.environ.copy()
        env['LICENSE_KEY'] = "743017d6-221c-4e0a-93ed-e417ae006db2"
        
        result = subprocess.run([
            sys.executable, "-c", 
            "from offers_check_marketplaces.server import initialize_components; "
            "import asyncio; "
            "asyncio.run(initialize_components()); "
            "print('SUCCESS: Components initialized')"
        ], 
        env=env,
        capture_output=True,
        text=True,
        timeout=15
        )
        
        print(f"   Код завершения: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Компоненты успешно инициализированы")
            if "SUCCESS: Components initialized" in result.stdout:
                print("✅ Инициализация завершена успешно")
        else:
            print(f"❌ Неожиданный код завершения: {result.returncode}")
            print(f"   STDOUT: {result.stdout}")
            print(f"   STDERR: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Таймаут выполнения")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 60)

if __name__ == "__main__":
    test_license_error_handling()