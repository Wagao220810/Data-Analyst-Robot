import pytest
import pandas as pd
import sys
import os
from unittest.mock import patch

# Garante que o Python encontre o arquivo data_analyst_robot.py na raiz
PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PASTA_RAIZ)

from data_analyst_robot import RoboAnalistaDados

@pytest.fixture
def robo():
    """Fixture: Instância nova e limpa do robô para injetar nos testes."""
    return RoboAnalistaDados()

@pytest.fixture
def df_fake():
    """Fixture: DataFrame dummy para testes."""
    return pd.DataFrame({'Coluna1': [1, 2, 3], 'Coluna2': ['A', 'B', 'C']})

def test_inicializacao_robo(robo):
    assert robo.df is None
    assert robo.output_dir is None

@patch('data_analyst_robot.RoboAnalistaDados._criar_diretorio_saida')
def test_processar_novo_df(mock_criar_dir, robo, df_fake):
    sucesso = robo._processar_novo_df(df_fake)
    
    assert sucesso is True
    assert robo.df.shape == (3, 2)
    mock_criar_dir.assert_called_once()

@patch('src.dados.carregar_arquivo')
@patch('data_analyst_robot.RoboAnalistaDados._processar_novo_df')
def test_carregar_dados(mock_processar, mock_carregar_arquivo, robo, df_fake):
    robo._garantir_dependencias()
    mock_carregar_arquivo.return_value = df_fake
    mock_processar.return_value = True
    
    resultado = robo.carregar_dados()
    
    mock_carregar_arquivo.assert_called_once()
    mock_processar.assert_called_once_with(df_fake, "✅ Dados carregados!")
    assert resultado is True

def test_decorator_dados_carregados_bloqueia_sem_dados(capsys, robo):
    robo.df = None
    robo.estatisticas_descritivas()
    
    captured = capsys.readouterr()
    assert "❌ ERRO: Nenhum dado foi carregado" in captured.out

if __name__ == "__main__":
    # Permite rodar o arquivo diretamente no VS Code (Ex: botão Play)
    pytest.main([__file__, "-v"])