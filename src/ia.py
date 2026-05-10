import os
import io

def _configurar_gemini():
    """Configura a API do Gemini e retorna o módulo genai."""
    try:
        import google.generativeai as genai
    except ImportError:
        print("❌ ERRO: A biblioteca 'google-generativeai' não está instalada.")
        return None

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        api_key = input("🔑 Cole sua API Key do Google Gemini (ou Enter para cancelar): ").strip()
        if not api_key:
            return None
        os.environ["GEMINI_API_KEY"] = api_key
        
    genai.configure(api_key=api_key)
    return genai

def _obter_modelo(genai, preferencia="flash"):
    """Busca o modelo adequado disponível na API."""
    modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if not modelos_disponiveis:
        raise Exception("Sua API Key não tem acesso a nenhum modelo de geração de texto.")
        
    modelo_escolhido = modelos_disponiveis[0]
    for m in modelos_disponiveis:
        if preferencia in m:
            modelo_escolhido = m
            break
    return genai.GenerativeModel(modelo_escolhido), modelo_escolhido

def explicar_anomalias(anomalias_resumo):
    """Usa a API do Gemini para interpretar os outliers detectados."""
    genai = _configurar_gemini()
    if not genai: return
        
    try:
        prompt = f"Você é um Cientista de Dados Sênior. Encontramos as seguintes anomalias (outliers) no dataset:\n{anomalias_resumo}\n\nPor favor, sugira possíveis motivos no mundo real que explicariam o aparecimento dessas anomalias nestas colunas. Seja direto, criativo e analítico."
        print("⏳ Investigando anomalias com o Gemini...\n")
        
        model, nome_modelo = _obter_modelo(genai, "flash")
        print(f"⚙️ Modelo selecionado automaticamente: {nome_modelo}")
        response = model.generate_content(prompt)
        
        print("✨ ANÁLISE DE ANOMALIAS PELO GEMINI ✨")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
    except Exception as e:
        print(f"❌ Erro ao comunicar com a API do Gemini: {e}")

def obter_insights(df, output_dir):
    """Gera insights textuais usando a API do Gemini."""
    genai = _configurar_gemini()
    if not genai: return
        
    try:
        estatisticas = df.describe().to_string()
        amostra = df.head().to_string()
        prompt = f"Você é um Analista de Dados Sênior. Analise as estatísticas descritivas e a amostra dos dados abaixo. Forneça um resumo executivo com os 3 principais insights de negócios. Seja direto, claro e use linguagem profissional de negócios.\n\nEstatísticas:\n{estatisticas}\n\nAmostra de Dados:\n{amostra}"
        
        print("⏳ Analisando dados com o Gemini... (isso pode levar alguns segundos)\n")
        
        model, nome_modelo = _obter_modelo(genai, "flash")
        print(f"⚙️ Modelo selecionado automaticamente: {nome_modelo}")
        response = model.generate_content(prompt)
        
        print("✨ INSIGHTS GERADOS PELO GEMINI ✨")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        
        if output_dir:
            filepath = os.path.join(output_dir, 'insights_gemini.txt')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"✅ Insights textuais salvos em: '{filepath}'")
    except Exception as e:
        print(f"❌ Erro ao comunicar com a API do Gemini: {e}")

def analise_automatizada(df, output_dir):
    """Executa uma análise completa (Auto-Pilot) do dataset usando o Gemini."""
    print("⚙️ 1/3 Extraindo contexto total dos dados (Estatísticas, Nulos, Estrutura)...")
    buffer_info = io.StringIO()
    df.info(buf=buffer_info)
    info_str = buffer_info.getvalue()
    
    estatisticas = df.describe().to_string()
    amostra = df.head().to_string()
    nulos = df.isnull().sum().to_string()
    
    print("🧠 2/3 Preparando o cérebro da IA...")
    genai = _configurar_gemini()
    if not genai: return False
        
    try:
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
        
        model, nome_modelo = _obter_modelo(genai, "pro")
        print(f"🤖 Modelo selecionado automaticamente: {nome_modelo}")
        response = model.generate_content(prompt)
        
        filepath = os.path.join(output_dir or '.', 'Relatorio_Completo_AutoPilot_Gemini.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print("\n✨ RELATÓRIO COMPLETADO COM SUCESSO ✨")
        print(f"✅ Arquivo salvo em: '{filepath}'")
        print("💡 DICA: Abra o arquivo .md gerado no VS Code (ou em qualquer leitor de Markdown) para ver a formatação!")
        return True
    except Exception as e:
        print(f"❌ Erro ao gerar análise automatizada: {e}")
        return False