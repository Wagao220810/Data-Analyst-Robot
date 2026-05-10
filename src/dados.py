import os
import io
from datetime import datetime

try:
    import pandas as pd
    from pandas.io.clipboard import clipboard_get
except ImportError:
    pass

def carregar_arquivo():
    """Carrega arquivo de dados CSV, Excel ou JSON."""
    caminho_input = input("\n📂 Digite o caminho do arquivo (CSV/Excel/JSON): ")
    arquivo = caminho_input.strip(' "\'')
    
    if not os.path.exists(arquivo):
        print("❌ Arquivo não encontrado!")
        return None
    
    try:
        extensao = os.path.splitext(arquivo)[1].lower()
        readers = {
            '.csv': pd.read_csv,
            '.xlsx': pd.read_excel,
            '.xls': pd.read_excel,
            '.json': pd.read_json,
        }
        
        reader_func = readers.get(extensao)
        if not reader_func:
            print(f"⚠️ Extensão '{extensao}' não reconhecida. Tentando carregar como CSV por padrão...")
            reader_func = pd.read_csv
        
        return reader_func(arquivo)
    except Exception as e:
        print(f"❌ Erro ao carregar: {e}")
        return None

def carregar_area_transferencia():
    """Carrega dados diretamente da área de transferência (clipboard)."""
    print("\n📋 Tentando carregar dados da área de transferência...")
    try:
        return pd.read_clipboard()
    except Exception:
        print("⚠️ Formato tabular padrão falhou. Analisando o conteúdo copiado...")
        try:
            texto_copiado = clipboard_get()
            texto_limpo = texto_copiado.strip()
            
            if texto_limpo.startswith(('{', '[')):
                print("🔍 Formato JSON detectado na área de transferência!")
                return pd.read_json(io.StringIO(texto_limpo))
            else:
                sep = input("🔍 Não foi possível identificar as colunas automaticamente.\nDigite o separador usado (ex: ',', ';', '|' ou deixe em branco para abortar): ")
                if not sep:
                    return None
                return pd.read_clipboard(sep=sep)
        except Exception as e2:
            print("❌ Erro definitivo ao carregar da área de transferência.")
            print(f"   Dica: Certifique-se de ter copiado dados estruturados válidos. Detalhe: {e2}")
            return None

def carregar_url():
    """Carrega dados diretamente de uma URL."""
    url_input = input("\n🔗 Digite a URL do arquivo (CSV/Excel/JSON): ")
    url = url_input.strip(' "\'')
    
    if not url.startswith(('http://', 'https://')):
        print("❌ URL inválida! Certifique-se de que ela comece com http:// ou https://")
        return None
        
    print(f"⏳ Baixando dados de: {url} ...")
    try:
        if '.json' in url.lower():
            return pd.read_json(url)
        elif '.xls' in url.lower():
            return pd.read_excel(url)
        else:
            return pd.read_csv(url)
    except Exception as e:
        print(f"❌ Erro ao carregar da URL: {e}")
        print("   Dica: Verifique se o link é público e aponta diretamente para o arquivo bruto (raw).")
        return None

def carregar_banco_dados():
    """Carrega dados diretamente de um banco de dados SQL."""
    print("\n🗄️ CONEXÃO COM BANCO DE DADOS")
    print("Suporta: SQLite, PostgreSQL, MySQL, SQL Server, Oracle, etc.")
    
    try:
        from sqlalchemy import create_engine
    except ImportError:
        print("❌ ERRO: A biblioteca 'SQLAlchemy' não está instalada.")
        print("   Rode no terminal: pip install sqlalchemy")
        return None

    conexao_input = input("\n🔗 Digite a string de conexão (Ex: sqlite:///dados.db ou postgresql://user:pass@localhost/db): ")
    string_conexao = conexao_input.strip(' "\'')
    if not string_conexao: return None
        
    query = input("📝 Digite a Query SQL para extrair os dados (Ex: SELECT * FROM clientes): ").strip()
    if not query: return None

    print("⏳ Conectando e executando query...")
    try:
        engine = create_engine(string_conexao)
        return pd.read_sql(query, engine)
    except Exception as e:
        print(f"❌ Erro ao conectar ou consultar o banco: {e}")
        return None

def exportar_dados(df, output_dir):
    """Exporta os dados carregados para um arquivo CSV ou Excel."""
    print("\n💾 EXPORTAR DADOS (PREPARAÇÃO PARA POWER BI)")
    print("="*50)
    print("Escolha o formato de exportação:")
    print("1. Excel (.xlsx)\n2. CSV (.csv)")
    
    opcao = input("Opção (1-2): ").strip()
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    
    try:
        if opcao == '1':
            filepath = os.path.join(output_dir or '.', f'dados_tratados_{timestamp}.xlsx')
            df.to_excel(filepath, index=False)
            print(f"✅ Arquivo Excel exportado com sucesso em: '{filepath}'")
            print("💡 Dica para o Power BI: Vá em 'Obter Dados' -> 'Pasta de Trabalho do Excel' e selecione este arquivo!")
            return True
        elif opcao == '2':
            filepath = os.path.join(output_dir or '.', f'dados_tratados_{timestamp}.csv')
            df.to_csv(filepath, index=False, sep=';')
            print(f"✅ Arquivo CSV exportado com sucesso em: '{filepath}'")
            print("💡 Dica para o Power BI: Vá em 'Obter Dados' -> 'Texto/CSV' e selecione este arquivo!")
            return True
        else:
            print("❌ Opção inválida!")
            return False
    except Exception as e:
        print(f"❌ Erro ao exportar dados: {e}")
        return False