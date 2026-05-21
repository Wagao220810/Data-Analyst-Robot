import pytest
import pandas as pd
import os
import sys
from unittest.mock import patch, MagicMock

# Garante que o Python encontre a pasta src
PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PASTA_RAIZ)

from src import visualizacao

@patch('src.visualizacao.plt')
@patch('src.visualizacao.sns')
def test_gerar_graficos_basicos(mock_sns, mock_plt, tmp_path):
    """Testa se a função de gráficos básicos tenta salvar as imagens sem abrir janelas reais."""
    df_fake = pd.DataFrame({
        'Idade': [25, 30, 35],
        'Salario': [5000, 6000, 7000],
        'Categoria': ['A', 'B', 'A']
    })
    pasta_saida = str(tmp_path)
    
    visualizacao.gerar_graficos_basicos(df_fake, pasta_saida)
    
    # Verifica se os métodos do matplotlib foram chamados (indica que rodou até o fim)
    assert mock_plt.savefig.called
    assert mock_plt.show.called

@patch('src.visualizacao.clipboard_set')
def test_gerar_scripts_powerbi(mock_clipboard, tmp_path):
    """Testa se o script do Power BI é gerado em arquivo e copiado para a área de transferência."""
    pasta_saida = str(tmp_path)
    
    resultado = visualizacao.gerar_scripts_powerbi(pasta_saida)
    
    assert resultado is True
    
    # Verifica se o arquivo foi criado fisicamente na pasta temporária
    caminho_arquivo = os.path.join(pasta_saida, 'script_pbi_interativo.py')
    assert os.path.exists(caminho_arquivo)
    
    # Verifica se a função de copiar para área de transferência foi ativada
    mock_clipboard.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])