import pytest
import pandas as pd
import sys
import os

# Garante que o Python encontre a pasta src
PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PASTA_RAIZ)

from src import dados

def test_detectar_anomalias():
    """Testa se a função identifica outliers corretamente via método IQR (Tukey)."""
    # Cria um DataFrame onde o valor 100 é claramente um outlier no meio de idades jovens
    df_teste = pd.DataFrame({
        'Idade': [25, 26, 24, 25, 27, 26, 25, 100],  # 100 é a anomalia
        'Salario': [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000] # Constante para garantir 0 outliers
    })
    
    resultado = dados.detectar_anomalias(df_teste)
    
    # 1. Verifica se encontrou anomalia na coluna 'Idade'
    assert 'Idade' in resultado
    assert resultado['Idade']['quantidade'] == 1
    # Verifica se o outlier exato (100) foi capturado na amostra
    assert 100 in resultado['Idade']['amostra_valores']
    
    # 2. Verifica se a coluna 'Salario' foi ignorada porque está tudo normal
    assert 'Salario' not in resultado

if __name__ == "__main__":
    # Permite rodar o arquivo diretamente no terminal ou VS Code
    pytest.main([__file__, "-v"])