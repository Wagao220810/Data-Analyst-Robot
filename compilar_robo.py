import os
import shutil
import subprocess
import sys

# Descobre o caminho absoluto da pasta onde este script está (Desktop)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rodar_testes():
    """Roda a suíte de testes antes de compilar (Workflow Fail-Fast)."""
    print("🧪 Executando testes automatizados...")
    resultado = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=BASE_DIR)
    if resultado.returncode != 0:
        print("\n❌ ERRO: Alguns testes falharam! Compilação abortada para não gerar um executável quebrado.")
        sys.exit(1)
    print("✅ Todos os testes passaram! Prosseguindo...\n")

def limpar_pastas():
    """Remove as pastas de compilação antigas para evitar cache."""
    for pasta in ['build', 'dist']:
        caminho = os.path.join(BASE_DIR, pasta)
        if os.path.exists(caminho):
            print(f"🧹 Limpando cache antigo: {pasta}/")
            try:
                shutil.rmtree(caminho)
            except Exception as e:
                print(f"⚠️ Aviso: Não foi possível apagar {pasta}: {e}")

def compilar():
    rodar_testes()
    limpar_pastas()
    print("🚀 Iniciando compilação do Robô (com IA e metadados)...")
    
    comando = [
        sys.executable, "-m", "PyInstaller", 
        "--onefile", "--clean",
        "--name", "Robo_Analista_IA",
        "--collect-all", "customtkinter",
        "--collect-all", "google.generativeai",
        "--collect-all", "google.ai.generativelanguage",
        "--collect-all", "grpc",
        "--collect-all", "pydantic",
        "--collect-all", "google.protobuf",
        "--copy-metadata", "google-generativeai",
        "--copy-metadata", "google-api-core",
        # Adicione novos arquivos da pasta 'src' usando a flag --hidden-import abaixo:
        "--hidden-import", "src",
        "--hidden-import", "src.ia",
        "--hidden-import", "src.dados",
        "--hidden-import", "src.visualizacao",
        "--hidden-import", "sweetviz",
        "data_analyst_robot.py"
    ]
    
    subprocess.run(comando, cwd=BASE_DIR)
    print("\n✅ Compilação finalizada! Abra a pasta 'dist' e execute o arquivo 'Robo_Analista_IA.exe'")

if __name__ == "__main__":
    compilar()