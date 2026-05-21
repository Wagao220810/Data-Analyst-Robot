import os
import subprocess
import sys

# Garante que os comandos do git rodem na pasta onde o script está salvo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def executar_comando(comando, ignorar_erro=False):
    """Executa um comando no terminal e exibe o resultado."""
    try:
        resultado = subprocess.run(comando, shell=True, check=True, text=True, capture_output=True, cwd=BASE_DIR)
        if resultado.stdout.strip():
            print(resultado.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        if not ignorar_erro:
            print(f"❌ Erro ao executar '{comando}':\n{e.stderr.strip()}")
        return False

def main():
    print("🚀 Iniciando automação de atualização no GitHub...\n")
    
    print("📋 Arquivos modificados (git status):")
    executar_comando("git status -s")
    
    if len(sys.argv) > 1:
        mensagem = " ".join(sys.argv[1:])
        print(f"\n✏️ Mensagem do commit (via comando): {mensagem}")
    else:
        mensagem = input("\n✏️ Digite a mensagem do commit (ou pressione Enter para usar a padrão): ").strip()
        
    if not mensagem:
        mensagem = "Atualizando o projeto com novos recursos e testes"

    branch = input("\n🌿 Digite o nome da nova branch (ou pressione Enter para continuar na atual): ").strip()
    if branch:
        print(f"\n🔀 Criando e mudando para a nova branch '{branch}'...")
        if not executar_comando(f"git checkout -b {branch}"):
            return

    arquivos_robo = "data_analyst_robot.py compilar_robo.py atualizar_github.py src/ tests/ .gitignore"
    print("\n Adicionando somente arquivos do robô e testes...")
    if not executar_comando(f"git add {arquivos_robo}"):
        return

    print(f"💾 Fazendo o commit (git commit -m \"{mensagem}\")...")
    # Ignora o erro no commit pois pode não haver arquivos novos para commitar
    executar_comando(f'git commit -m "{mensagem}"', ignorar_erro=True)
    
    print("\n☁️ Enviando alterações para o GitHub (git push)...")
    comando_push = f"git push -u origin {branch}" if branch else "git push"
    if executar_comando(comando_push):
        print("\n✅ Projeto atualizado com sucesso no GitHub!")
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()