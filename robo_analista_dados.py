import sys
import io
import os
from functools import wraps
from datetime import datetime

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    from pandas.io.clipboard import clipboard_get, clipboard_set
    from dotenv import load_dotenv
    
    # Carrega variáveis de ambiente de um arquivo .env automaticamente
    load_dotenv()
except ImportError as e:
    print("\n❌ ERRO: Dependências ausentes!")
    print(f"   Detalhe: {e}")
    print("   Por favor, instale as bibliotecas necessárias com o comando:")
    print("   pip install pandas matplotlib seaborn openpyxl python-dotenv")
    sys.exit(1)

def dados_carregados_required(func):
    """Decorator para verificar se o DataFrame foi carregado antes de executar uma função."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.df is None:
            print("\n❌ ERRO: Nenhum dado foi carregado. Use a opção '1' para carregar um arquivo primeiro.")
            return
        return func(self, *args, **kwargs)
    return wrapper


class RoboAnalistaDados:
    def __init__(self):
        self.df: pd.DataFrame | None = None
        self.output_dir: str | None = None
        print("🤖 Robô Analista de dados INICIADO!")
        print("📊 Suporta CSV, Excel (.xlsx) e JSON")
    
    def _criar_diretorio_saida(self):
        """Cria um diretório de saída único para os resultados da análise."""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        self.output_dir = f"analise_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"📂 Os resultados serão salvos em: '{self.output_dir}'")

    def _abrir_pasta_saida(self):
        """Abre a pasta de saída no explorador de arquivos automaticamente (Windows, Mac, Linux)."""
        if not self.output_dir:
            return
        try:
            if sys.platform == 'win32':
                os.startfile(self.output_dir)
            elif sys.platform == 'darwin':
                import subprocess; subprocess.Popen(['open', self.output_dir])
            else:
                import subprocess; subprocess.Popen(['xdg-open', self.output_dir])
        except Exception:
            pass

    def carregar_dados(self):
        """Carrega arquivo de dados"""
        caminho_input = input("\n📂 Digite o caminho do arquivo (CSV/Excel/JSON): ")
        
        # Remove espaços em branco e aspas ao redor do caminho
        arquivo = caminho_input.strip(' "\'')
        
        if not os.path.exists(arquivo):
            print("❌ Arquivo não encontrado!")
            return False
        
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
            
            self.df = reader_func(arquivo)
            self._criar_diretorio_saida() # Cria o diretório após o carregamento bem-sucedido

            print(f"✅ Dados carregados! {self.df.shape[0]} linhas, {self.df.shape[1]} colunas")
            print("\n📋 Primeiras 5 linhas:")
            print(self.df.head())
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar: {e}")
            return False

    def carregar_area_transferencia(self):
        """Carrega dados diretamente da área de transferência (clipboard)."""
        print("\n📋 Tentando carregar dados da área de transferência...")
        try:
            # Tenta o carregamento padrão (tabelas do Excel, web, tabulações)
            self.df = pd.read_clipboard()
            self._criar_diretorio_saida()
            
            print(f"✅ Dados carregados do clipboard! {self.df.shape[0]} linhas, {self.df.shape[1]} colunas")
            print("\n📋 Primeiras 5 linhas:")
            print(self.df.head())
            return True
        except Exception as e:
            print(f"⚠️ Formato tabular padrão falhou. Analisando o conteúdo copiado...")
            try:
                texto_copiado = clipboard_get()
                texto_limpo = texto_copiado.strip()
                
                # Se o texto começar com chaves ou colchetes, tenta ler como JSON
                if texto_limpo.startswith(('{', '[')):
                    print("🔍 Formato JSON detectado na área de transferência!")
                    self.df = pd.read_json(io.StringIO(texto_limpo))
                else:
                    # Pede um separador manual para o usuário caso seja um CSV estranho
                    sep = input("🔍 Não foi possível identificar as colunas automaticamente.\nDigite o separador usado (ex: ',', ';', '|' ou deixe em branco para abortar): ")
                    if not sep:
                        return False
                    self.df = pd.read_clipboard(sep=sep)
                
                self._criar_diretorio_saida()
                print(f"✅ Dados carregados com sucesso! {self.df.shape[0]} linhas, {self.df.shape[1]} colunas")
                print("\n📋 Primeiras 5 linhas:")
                print(self.df.head())
                return True
                
            except Exception as e2:
                print(f"❌ Erro definitivo ao carregar da área de transferência.")
                print(f"   Dica: Certifique-se de ter copiado dados estruturados válidos. Detalhe: {e2}")
                return False

    def carregar_url(self):
        """Carrega dados diretamente de uma URL."""
        url_input = input("\n🔗 Digite a URL do arquivo (CSV/Excel/JSON): ")
        url = url_input.strip(' "\'')
        
        if not url.startswith(('http://', 'https://')):
            print("❌ URL inválida! Certifique-se de que ela comece com http:// ou https://")
            return False
            
        print(f"⏳ Baixando dados de: {url} ...")
        try:
            # Tenta inferir o tipo de arquivo pela extensão na URL
            if '.json' in url.lower():
                self.df = pd.read_json(url)
            elif '.xls' in url.lower():
                self.df = pd.read_excel(url)
            else:
                self.df = pd.read_csv(url)
                
            self._criar_diretorio_saida()
            
            print(f"✅ Dados carregados com sucesso da URL! {self.df.shape[0]} linhas, {self.df.shape[1]} colunas")
            print("\n📋 Primeiras 5 linhas:")
            print(self.df.head())
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar da URL: {e}")
            print("   Dica: Verifique se o link é público e aponta diretamente para o arquivo bruto (raw).")
            return False
    
    def carregar_banco_dados(self):
        """Carrega dados diretamente de um banco de dados SQL."""
        print("\n🗄️ CONEXÃO COM BANCO DE DADOS")
        print("Suporta: SQLite, PostgreSQL, MySQL, SQL Server, Oracle, etc.")
        
        try:
            from sqlalchemy import create_engine
        except ImportError:
            print("❌ ERRO: A biblioteca 'SQLAlchemy' não está instalada.")
            print("   Rode no terminal: pip install sqlalchemy")
            print("   (Lembre-se também de instalar o driver do banco, ex: psycopg2 para Postgres, pymysql para MySQL)")
            return False

        conexao_input = input("\n🔗 Digite a string de conexão (Ex: sqlite:///dados.db ou postgresql://user:pass@localhost/db): ")
        string_conexao = conexao_input.strip(' "\'')
        
        if not string_conexao:
            print("❌ Conexão cancelada.")
            return False
            
        query = input("📝 Digite a Query SQL para extrair os dados (Ex: SELECT * FROM clientes): ").strip()
        
        if not query:
            print("❌ Nenhuma query fornecida.")
            return False

        print(f"⏳ Conectando e executando query...")
        try:
            engine = create_engine(string_conexao)
            self.df = pd.read_sql(query, engine)
            self._criar_diretorio_saida()
            
            print(f"✅ Dados carregados com sucesso do banco! {self.df.shape[0]} linhas, {self.df.shape[1]} colunas")
            print("\n📋 Primeiras 5 linhas:")
            print(self.df.head())
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar ou consultar o banco: {e}")
            print("   Dica: Verifique sua string de conexão, se o banco está rodando e se a tabela existe.")
            return False

    @dados_carregados_required
    def estatisticas_descritivas(self):
        """Estatísticas básicas"""
        print("\n📈 ESTATÍSTICAS DESCRITIVAS")
        print("="*50)
        print(self.df.describe())
    
    @dados_carregados_required
    def info_dados(self):
        """Informações do dataset"""
        print("\nℹ️  INFORMAÇÕES DO DATASET")
        print("="*50)
        # self.df.info() imprime diretamente na saída, para capturar como string seria mais complexo.
        # Para um script de console, o comportamento padrão é aceitável.
        self.df.info()
        print(f"\nValores ausentes:\n{self.df.isnull().sum()}")
    
    @dados_carregados_required
    def graficos(self):
        """Gera gráficos automáticos"""
        print("\n📊 GERANDO GRÁFICOS...")
        plt.style.use('default')
        sns.set_palette("husl")
        
        self._gerar_histogramas()
        self._gerar_heatmap_correlacao()
        self._gerar_graficos_barras()

    def _gerar_histogramas(self):
        """Gera e salva histogramas para colunas numéricas."""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if not numeric_cols.empty:
            self.df[numeric_cols].hist(figsize=(12, 8))
            plt.tight_layout()
            filepath = os.path.join(self.output_dir, 'histograma_geral.png')
            plt.savefig(filepath)
            plt.show()
            print(f"✅ Histograma salvo em '{filepath}'")

    def _gerar_heatmap_correlacao(self):
        """Gera e salva um heatmap de correlação para colunas numéricas."""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            plt.figure(figsize=(10, 8))
            sns.heatmap(self.df[numeric_cols].corr(), annot=True, cmap='coolwarm', center=0)
            plt.title('Matriz de Correlação')
            plt.tight_layout()
            filepath = os.path.join(self.output_dir, 'correlacao_heatmap.png')
            plt.savefig(filepath)
            plt.show()
            print(f"✅ Heatmap de correlação salvo em '{filepath}'")

    def _gerar_graficos_barras(self):
        """Gera e salva gráficos de barras para colunas categóricas."""
        cat_cols = self.df.select_dtypes(include=['object']).columns
        for col in cat_cols[:5]:  # Limita para as 5 primeiras colunas categóricas para não sobrecarregar
            if self.df[col].nunique() < 20:  # Se não tiver muitos valores únicos
                plt.figure(figsize=(10, 6))
                self.df[col].value_counts().plot(kind='bar')
                plt.title(f'Distribuição - {col}')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                filepath = os.path.join(self.output_dir, f'barras_{col}.png')
                plt.savefig(filepath)
                plt.show()
                print(f"✅ Gráfico de barras para '{col}' salvo em '{filepath}'")

    @dados_carregados_required
    def detectar_anomalias(self):
        """Detecta outliers simples"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        print("\n🔍 DETECÇÃO DE ANOMALIAS (Outliers)")
        print("="*50)
        
        anomalias_resumo = {}
        
        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            limite_inf = Q1 - 1.5 * IQR
            limite_sup = Q3 + 1.5 * IQR
            
            outliers = self.df[(self.df[col] < limite_inf) | (self.df[col] > limite_sup)][col]
            
            print(f"\n{col}:")
            print(f"  Limites: [{limite_inf:.2f}, {limite_sup:.2f}]")
            print(f"  Outliers encontrados: {len(outliers)}")
            if not outliers.empty:
                print(f"  Valores: {outliers.tolist()}")
                anomalias_resumo[col] = {
                    "quantidade": len(outliers),
                    "limites_normais": f"[{limite_inf:.2f}, {limite_sup:.2f}]",
                    "amostra_valores": outliers.tolist()[:10] # Envia no max 10 valores para não sobrecarregar a IA
                }
                
        if anomalias_resumo:
            resp = input("\n🤖 Deseja que o Gemini analise e sugira causas para essas anomalias? (s/n): ").strip().lower()
            if resp == 's':
                self._explicar_anomalias_com_ia(anomalias_resumo)

    def _explicar_anomalias_com_ia(self, anomalias_resumo):
        """Usa a API do Gemini para interpretar os outliers detectados."""
        try:
            import google.generativeai as genai
        except ImportError:
            print("❌ ERRO: A biblioteca 'google-generativeai' não está instalada.")
            return

        # ⚠️ AVISO DE SEGURANÇA: Chave salva diretamente no código.
        # Nunca compartilhe este arquivo ou suba no GitHub com essa chave exposta!
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            api_key = input("🔑 Cole sua API Key do Google Gemini (ou Enter para cancelar): ").strip()
            if not api_key:
                return
            
        try:
            genai.configure(api_key=api_key)
            
            prompt = f"Você é um Cientista de Dados Sênior. Encontramos as seguintes anomalias (outliers) no dataset:\n{anomalias_resumo}\n\nPor favor, sugira possíveis motivos no mundo real que explicariam o aparecimento dessas anomalias nestas colunas. Seja direto, criativo e analítico."
            
            print("⏳ Investigando anomalias com o Gemini...\n")
            
            # Busca dinamicamente qual modelo está disponível para a sua chave
            modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if not modelos_disponiveis:
                raise Exception("Sua API Key não tem acesso a nenhum modelo de geração de texto.")
                
            modelo_escolhido = modelos_disponiveis[0]
            for m in modelos_disponiveis:
                if '1.5-flash' in m:
                    modelo_escolhido = m
                    break
                    
            print(f"⚙️ Modelo selecionado automaticamente: {modelo_escolhido}")
            model = genai.GenerativeModel(modelo_escolhido)
            response = model.generate_content(prompt)
            
            print("✨ ANÁLISE DE ANOMALIAS PELO GEMINI ✨")
            print("-" * 50)
            print(response.text)
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Erro ao comunicar com a API do Gemini: {e}")

    @dados_carregados_required
    def exportar_dados(self):
        """Exporta os dados carregados para um arquivo (ideal para Power BI)."""
        print("\n💾 EXPORTAR DADOS (PREPARAÇÃO PARA POWER BI)")
        print("="*50)
        print("Escolha o formato de exportação:")
        print("1. Excel (.xlsx)")
        print("2. CSV (.csv)")
        
        opcao = input("Opção (1-2): ").strip()
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        
        try:
            if opcao == '1':
                filepath = os.path.join(self.output_dir or '.', f'dados_tratados_{timestamp}.xlsx')
                self.df.to_excel(filepath, index=False)
                print(f"✅ Arquivo Excel exportado com sucesso em: '{filepath}'")
                print("💡 Dica para o Power BI: Vá em 'Obter Dados' -> 'Pasta de Trabalho do Excel' e selecione este arquivo!")
            elif opcao == '2':
                filepath = os.path.join(self.output_dir or '.', f'dados_tratados_{timestamp}.csv')
                self.df.to_csv(filepath, index=False, sep=';')
                print(f"✅ Arquivo CSV exportado com sucesso em: '{filepath}'")
                print("💡 Dica para o Power BI: Vá em 'Obter Dados' -> 'Texto/CSV' e selecione este arquivo!")
            else:
                print("❌ Opção inválida!")
                
            self._abrir_pasta_saida()
        except Exception as e:
            print(f"❌ Erro ao exportar dados: {e}")

    @dados_carregados_required
    def gerar_scripts_powerbi(self):
        """Gera scripts Python prontos para Visuais do Power BI."""
        print("\n🪄 GERADOR DE DASHBOARD INTERATIVO PARA POWER BI (Nível Sênior)")
        print("="*50)
        
        script_pbi = '''# --- VISUAL PYTHON PARA POWER BI: DASHBOARD INTERATIVO SÊNIOR ---
# 1. Adicione um "Visual de script Python" no Power BI.
# 2. Arraste colunas (numéricas e categóricas) para a área de "Valores".
# 3. Cole este código abaixo e execute:

import plotly.express as px
import pandas as pd

# Fallback inteligente: se rodar fora do Power BI (ex: localmente no VS Code), gera dados de teste
try:
    dataset
except NameError:
    import numpy as np
    print("⚠️ Executando fora do Power BI! Gerando dados de demonstração...")
    dataset = pd.DataFrame({
        'Indicador X': np.random.randn(100), 'Indicador Y': np.random.randn(100),
        'Peso': np.random.rand(100) * 20, 'Categoria': np.random.choice(['Grupo A', 'Grupo B', 'Grupo C'], 100)
    })

# O Power BI agrupa os dados selecionados na variável 'dataset'
df_limpo = dataset.dropna()

num_cols = df_limpo.select_dtypes(include='number').columns.tolist()
cat_cols = df_limpo.select_dtypes(exclude='number').columns.tolist()

if len(num_cols) >= 2:
    fig = px.scatter(
        df_limpo, 
        x=num_cols[0], y=num_cols[1], 
        color=cat_cols[0] if len(cat_cols) > 0 else None,
        size=num_cols[2] if len(num_cols) > 2 else None,
        hover_data=df_limpo.columns.tolist(),
        title=f"Visão Sênior Interativa: {num_cols[0]} vs {num_cols[1]}",
        template="plotly_dark"
    )
    fig.show() # Renderiza interativamente no Power BI!
else:
    import matplotlib.pyplot as plt
    plt.text(0.5, 0.5, "Adicione ao menos 2 colunas numéricas", ha='center')
    plt.axis('off')
    plt.show()
'''
        
        try:
            filepath = os.path.join(self.output_dir or '.', 'script_pbi_interativo.py')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(script_pbi)
            
            # Automação Mágica: Copia o código para o clipboard do usuário!
            clipboard_set(script_pbi)
            
            print(f"✅ Script de Dashboard Interativo gerado em: '{filepath}'")
            print("✨ SCRIPT COPIADO AUTOMATICAMENTE PARA SUA ÁREA DE TRANSFERÊNCIA! ✨")
            print("\n💡 DICA SÊNIOR PARA O POWER BI:")
            print("   O Power BI suporta gráficos 100% interativos nativamente usando a biblioteca Plotly!")
            print("   0. Abra o CMD e instale o pacote (se não tiver): pip install plotly")
            print("   1. No Power BI, clique no ícone 'Py' (Visual de script Python).")
            print("   2. Arraste suas colunas, clique no editor de script e aperte Ctrl+V.")
            print("   Seus dados vão virar um gráfico interativo com zoom, hover e filtros automáticos!")
            
            self._abrir_pasta_saida()
            
        except Exception as e:
            print(f"❌ Erro ao gerar scripts: {e}")

    @dados_carregados_required
    def gerar_dashboard_html(self):
        """Gera um dashboard HTML interativo estilo Tableau/Power BI usando PyGWalker."""
        print("\n🚀 GERANDO DASHBOARD INTERATIVO (ESTILO POWER BI)")
        print("="*50)
        try:
            import pygwalker as pyg
            import webbrowser
            
            print("⏳ Construindo a interface visual de arrastar e soltar (isso pode levar alguns segundos)...")
            
            filepath = os.path.join(self.output_dir or '.', 'dashboard_powerbi_style.html')
            
            # Gera o HTML interativo com o PyGWalker
            html_code = pyg.to_html(self.df)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_code)
            
            print(f"✅ Dashboard profissional gerado com sucesso!")
            print("🌐 Abrindo no seu navegador...")
            
            # Abre o arquivo HTML no navegador padrão
            path_absoluto = os.path.abspath(filepath)
            webbrowser.open(f'file://{path_absoluto}')
        except ImportError:
            print("❌ ERRO: A biblioteca 'pygwalker' não está instalada.")
            print("   Rode no terminal: pip install pygwalker")
        except Exception as e:
            print(f"❌ Erro ao gerar dashboard: {e}")

    @dados_carregados_required
    def obter_insights_ia(self):
        """Gera insights textuais usando a API do Gemini."""
        print("\n🧠 GERANDO INSIGHTS COM INTELIGÊNCIA ARTIFICIAL (GEMINI)")
        print("="*50)
        
        try:
            import google.generativeai as genai
        except ImportError:
            print("❌ ERRO: A biblioteca 'google-generativeai' não está instalada.")
            print("   Rode no terminal: pip install google-generativeai")
            return

        # ⚠️ AVISO DE SEGURANÇA: Chave salva diretamente no código.
        # Nunca compartilhe este arquivo ou suba no GitHub com essa chave exposta!
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            api_key = input("🔑 Cole sua API Key do Google Gemini (ou Enter para cancelar): ").strip()
            if not api_key:
                return
            
        try:
            genai.configure(api_key=api_key)
            
            # Prepara uma versão em string das estatísticas e dos primeiros dados
            estatisticas = self.df.describe().to_string()
            amostra = self.df.head().to_string()
            
            prompt = f"Você é um Analista de Dados Sênior. Analise as estatísticas descritivas e a amostra dos dados abaixo. Forneça um resumo executivo com os 3 principais insights de negócios. Seja direto, claro e use linguagem profissional de negócios.\n\nEstatísticas:\n{estatisticas}\n\nAmostra de Dados:\n{amostra}"
            
            print("⏳ Analisando dados com o Gemini... (isso pode levar alguns segundos)\n")
            
            # Busca dinamicamente qual modelo está disponível para a sua chave
            modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if not modelos_disponiveis:
                raise Exception("Sua API Key não tem acesso a nenhum modelo de geração de texto.")
                
            modelo_escolhido = modelos_disponiveis[0]
            for m in modelos_disponiveis:
                if '1.5-flash' in m:
                    modelo_escolhido = m
                    break
                    
            print(f"⚙️ Modelo selecionado automaticamente: {modelo_escolhido}")
            model = genai.GenerativeModel(modelo_escolhido)
            response = model.generate_content(prompt)
            
            print("✨ INSIGHTS GERADOS PELO GEMINI ✨")
            print("-" * 50)
            print(response.text)
            print("-" * 50)
            
            # Salva o resultado no diretório de saída
            if self.output_dir:
                filepath = os.path.join(self.output_dir, 'insights_gemini.txt')
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"✅ Insights textuais salvos em: '{filepath}'")
                
        except Exception as e:
            print(f"❌ Erro ao comunicar com a API do Gemini: {e}")

    @dados_carregados_required
    def analise_automatizada_ia(self):
        """Executa uma análise completa (Auto-Pilot) do dataset usando o Gemini."""
        print("\n🚀 INICIANDO AUTO-PILOT: ANÁLISE COMPLETA COM IA...")
        print("="*50)
        
        print("⚙️ 1/3 Extraindo contexto total dos dados (Estatísticas, Nulos, Estrutura)...")
        buffer_info = io.StringIO()
        self.df.info(buf=buffer_info)
        info_str = buffer_info.getvalue()
        
        estatisticas = self.df.describe().to_string()
        amostra = self.df.head().to_string()
        nulos = self.df.isnull().sum().to_string()
        
        print("🧠 2/3 Preparando o cérebro da IA...")
        try:
            import google.generativeai as genai
        except ImportError:
            print("❌ ERRO: A biblioteca 'google-generativeai' não está instalada.")
            return

        # ⚠️ AVISO DE SEGURANÇA: Chave salva diretamente no código.
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            api_key = input("🔑 Cole sua API Key do Google Gemini: ").strip()
            if not api_key: return
            
        try:
            genai.configure(api_key=api_key)
            prompt = f"""Você é um Cientista de Dados Sênior Autônomo.
Sua missão é atuar como um "Piloto Automático" e realizar a análise completa deste dataset.
Vou fornecer o contexto estrutural e estatístico. Sua saída deve ser um relatório definitivo, analítico e extremamente profissional formatado em Markdown.

INFORMAÇÕES DO DATASET:
--- INFORMAÇÕES GERAIS E TIPOS ---
{info_str}
--- VALORES NULOS (MISSING DATA) ---
{nulos}
--- ESTATÍSTICAS DESCRITIVAS ---
{estatisticas}
--- AMOSTRA DOS DADOS (PRIMEIRAS LINHAS) ---
{amostra}

Crie um relatório rico focado em negócios, contendo obrigatoriamente:
# 📊 Relatório Analítico Executivo
1. **Visão Geral e Qualidade dos Dados:** O que este dataset representa? Os dados estão limpos? Existem nulos problemáticos?
2. **Principais Insights Estatísticos:** Padrões interessantes, médias e variações que chamam a atenção.
3. **Detecção de Anomalias:** Possíveis outliers e comportamentos anormais.
4. **Próximos Passos e Ações de Negócio:** Recomendações práticas do que fazer com base nesses números.
"""
            print("⏳ 3/3 O Gemini está redigindo o Relatório Executivo (isso pode demorar uns 15 segundos)...")
            
            modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if not modelos_disponiveis:
                raise Exception("Sua API Key não tem acesso a modelos de geração de texto.")
                
            modelo_escolhido = modelos_disponiveis[0]
            for m in modelos_disponiveis:
                if '1.5-pro' in m: 
                    modelo_escolhido = m
                    break
                elif '1.5-flash' in m: 
                    modelo_escolhido = m
                    
            print(f"🤖 Modelo selecionado automaticamente: {modelo_escolhido}")
            model = genai.GenerativeModel(modelo_escolhido)
            response = model.generate_content(prompt)
            
            filepath = os.path.join(self.output_dir or '.', 'Relatorio_Completo_AutoPilot_Gemini.md')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
                
            print("\n✨ RELATÓRIO COMPLETADO COM SUCESSO ✨")
            print(f"✅ Arquivo salvo em: '{filepath}'")
            print("💡 DICA: Abra o arquivo .md gerado no VS Code (ou em qualquer leitor de Markdown) para ver a formatação!")
            
            self._abrir_pasta_saida()
            
        except Exception as e:
            print(f"❌ Erro ao gerar análise automatizada: {e}")

    def menu(self):
        while True:
            print("\n" + "="*60)
            print("🤖 Robô Analista de dados")
            print("="*60)
            print("1. 📂 Carregar dataset (Arquivo)")
            print("2. 📋 Carregar dataset (Área de Transferência)")
            print("3. 🔗 Carregar dataset (URL)")
            print("4. 🗄️ Carregar dataset (Banco de Dados SQL)")
            print("5. 📈 Estatísticas descritivas")
            print("6. ℹ️  Informações do dataset")
            print("7. 📊 Gerar gráficos")
            print("8. 🔍 Detectar anomalias")
            print("9. 💾 Exportar dados (Para BI)")
            print("10. 🪄  Gerar Scripts Visuais Power BI")
            print("11. 🚀 Gerar Dashboard HTML (Estilo Power BI)")
            print("12. 🧠 Gerar Insights com IA (Gemini)")
            print("13. 🤖 Analisar Tudo Automaticamente com IA (Auto-Pilot)")
            print("14. 🚪 Sair")
            print("="*60)
            
            opcao = input("Escolha (1-14): ").strip()
            
            # Padrão Clean Code: Dispatch Dictionary (Tabela de Despacho)
            acoes = {
                '1': self.carregar_dados,
                '2': self.carregar_area_transferencia,
                '3': self.carregar_url,
                '4': self.carregar_banco_dados,
                '5': self.estatisticas_descritivas,
                '6': self.info_dados,
                '7': self.graficos,
                '8': self.detectar_anomalias,
                '9': self.exportar_dados,
                '10': self.gerar_scripts_powerbi,
                '11': self.gerar_dashboard_html,
                '12': self.obter_insights_ia,
                '13': self.analise_automatizada_ia
            }
            
            if opcao in acoes:
                acoes[opcao]()  # Executa a função correspondente
            elif opcao == '14':
                print("\n🤖 Robô finalizado. Tenha um ótimo dia!")
                break
            else:
                print("❌ Opção inválida!")
            
            input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    try:
        robo = RoboAnalistaDados()
        robo.menu()
    except Exception as e:
        print(f"\n❌ Ocorreu um erro inesperado: {e}")
