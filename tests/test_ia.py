import pytest
import pandas as pd
import sys
import os
from unittest.mock import patch, MagicMock

# Garante que o Python encontre a pasta src na raiz do projeto
PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PASTA_RAIZ)

from src import ia

@pytest.fixture
def mock_gemini():
    """Fixture que centraliza a criação dos Mocks do Gemini para evitar repetição."""
    with patch('src.ia._configurar_gemini') as mock_conf, \
         patch('src.ia._obter_modelo') as mock_obt:
        mock_genai = MagicMock()
        mock_model = MagicMock()
        mock_conf.return_value = mock_genai
        mock_obt.return_value = (mock_model, "gemini-1.5-flash")
        yield mock_genai, mock_model, mock_conf, mock_obt

@patch.dict('os.environ', {'GEMINI_API_KEY': 'chave_falsa_valida_123'})
@patch('google.generativeai.configure')
def test_configurar_gemini_sucesso(mock_configure):
    """Testa se a configuração do Gemini ocorre corretamente quando há uma chave de API."""
    genai_module = ia._configurar_gemini()
    
    assert genai_module is not None
    # Verifica se a função de configuração da biblioteca original foi chamada com a nossa chave mockada
    mock_configure.assert_called_once_with(api_key='chave_falsa_valida_123')

def test_obter_insights(mock_gemini, tmp_path):
    mock_genai, mock_model, mock_conf, mock_obt = mock_gemini
    mock_response = MagicMock()
    mock_response.text = "Insight 1: Aumento de 20% nas vendas.\nInsight 2: Redução de custos."
    mock_model.generate_content.return_value = mock_response
    
    df_fake = pd.DataFrame({'Vendas': [100, 200], 'Custos': [50, 60]})
    pasta_saida = str(tmp_path) 
    
    ia.obter_insights(df_fake, pasta_saida)
    
    mock_conf.assert_called_once()
    mock_obt.assert_called_once_with(mock_genai, "flash")
    mock_model.generate_content.assert_called_once()
    
    caminho_arquivo = os.path.join(pasta_saida, 'insights_gemini.txt')
    assert os.path.exists(caminho_arquivo)
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
        assert "Insight 1" in conteudo

def test_estruturar_coluna_caotica(mock_gemini):
    mock_genai, mock_model, mock_conf, mock_obt = mock_gemini
    mock_response = MagicMock()
    
    mock_response.text = '{"Nome": "João Silva", "Valor": 2500}'
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    df_fake = pd.DataFrame({
        'ID': [1],
        'Descricao': ['O cliente João Silva comprou uma TV de 2500 reais.']
    })
    
    df_resultado = ia.estruturar_coluna_caotica(df_fake, 'Descricao')
    
    mock_conf.assert_called_once()
    mock_model.generate_content.assert_called_once()
    
    assert 'Descricao_ia_Nome' in df_resultado.columns
    assert 'Descricao_ia_Valor' in df_resultado.columns
    
    assert df_resultado['Descricao_ia_Nome'].iloc[0] == 'João Silva'
    assert df_resultado['Descricao_ia_Valor'].iloc[0] == 2500

if __name__ == "__main__":
    # Permite rodar o arquivo diretamente no VS Code (Ex: botão Play)
    pytest.main([__file__, "-v"])