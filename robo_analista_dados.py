import sys
import os
from functools import wraps
from datetime import datetime

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    from dotenv import load_dotenv
    
    # Tenta importar da pasta 'src' (ideal), se falhar, tenta da mesma pasta
    try:
        from src import ia, visualizacao, dados
    except ImportError:
        import ia
        import visualizacao
        import dados

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

    def _processar_novo_df(self, novo_df, mensagem_sucesso="✅ Dados carregados!"):
        """Processa e exibe o novo DataFrame carregado."""
        if novo_df is not None:
            self.df = novo_df
            self._criar_diretorio_saida()
            print(f"{mensagem_sucesso} {self.df.shape[0]} linhas, {self.df.shape[1]} colunas")
            print("\n📋 Primeiras 5 linhas:")
            print(self.df.head())
            return True
        return False

    def carregar_dados(self):
        """Carrega arquivo de dados"""
        novo_df = dados.carregar_arquivo()
        return self._processar_novo_df(novo_df, "✅ Dados carregados!")

    def carregar_area_transferencia(self):
        """Carrega dados diretamente da área de transferência (clipboard)."""
        novo_df = dados.carregar_area_transferencia()
        return self._processar_novo_df(novo_df, "✅ Dados carregados da área de transferência!")

    def carregar_url(self):
        """Carrega dados diretamente de uma URL."""
        novo_df = dados.carregar_url()
        return self._processar_novo_df(novo_df, "✅ Dados carregados com sucesso da URL!")
    
    def carregar_banco_dados(self):
        """Carrega dados diretamente de um banco de dados SQL."""
        novo_df = dados.carregar_banco_dados()
        return self._processar_novo_df(novo_df, "✅ Dados carregados com sucesso do banco!")

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
        visualizacao.gerar_graficos_basicos(self.df, self.output_dir)

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
                ia.explicar_anomalias(anomalias_resumo)

    @dados_carregados_required
    def exportar_dados(self):
        """Exporta os dados carregados para um arquivo (ideal para Power BI)."""
        sucesso = dados.exportar_dados(self.df, self.output_dir)
        if sucesso:
            self._abrir_pasta_saida()

    @dados_carregados_required
    def gerar_scripts_powerbi(self):
        """Gera scripts Python prontos para Visuais do Power BI."""
        sucesso = visualizacao.gerar_scripts_powerbi(self.output_dir)
        if sucesso:
            print("\n💡 DICA SÊNIOR PARA O POWER BI:")
            print("   O Power BI suporta gráficos 100% interativos nativamente usando a biblioteca Plotly!")
            print("   0. Abra o CMD e instale o pacote (se não tiver): pip install plotly")
            print("   1. No Power BI, clique no ícone 'Py' (Visual de script Python).")
            print("   2. Arraste suas colunas, clique no editor de script e aperte Ctrl+V.")
            print("   Seus dados vão virar um gráfico interativo com zoom, hover e filtros automáticos!")
            self._abrir_pasta_saida()

    @dados_carregados_required
    def gerar_dashboard_html(self):
        """Gera um dashboard HTML interativo estilo Tableau/Power BI usando PyGWalker."""
        visualizacao.gerar_dashboard_html(self.df, self.output_dir)

    @dados_carregados_required
    def obter_insights_ia(self):
        """Gera insights textuais usando a API do Gemini."""
        print("\n🧠 GERANDO INSIGHTS COM INTELIGÊNCIA ARTIFICIAL (GEMINI)")
        print("="*50)
        
        ia.obter_insights(self.df, self.output_dir)

    @dados_carregados_required
    def analise_automatizada_ia(self):
        """Executa uma análise completa (Auto-Pilot) do dataset usando o Gemini."""
        print("\n🚀 INICIANDO AUTO-PILOT: ANÁLISE COMPLETA COM IA...")
        print("="*50)
        
        sucesso = ia.analise_automatizada(self.df, self.output_dir)
        if sucesso:
            self._abrir_pasta_saida()

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
