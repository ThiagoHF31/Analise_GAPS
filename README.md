# Análise de Dados Financeiros WIN$N M1

Este projeto realiza uma análise completa de dados financeiros do índice WIN$N (Mini Índice Bovespa) em timeframe de 1 minuto, incluindo agregação diária, detecção de outliers, análise de gaps e geração de gráficos.

## 📊 Funcionalidades

- **Agregação de Dados**: Converte dados de minuto para diário com estatísticas OHLCV
- **Análise de Outliers**: Detecta e trata valores anômalos usando método IQR
- **Análise de Gaps**: Identifica gaps de abertura e verifica seu fechamento
- **Visualizações**: Gera gráficos profissionais de análise temporal e gaps
- **Dataset Limpo**: Produz dados prontos para backtesting e estratégias

## 🚀 Como Usar

### Instalação e Execução Automática

1. **Baixe ou clone o projeto**
2. **Coloque seu arquivo de dados**: Certifique-se de que o arquivo `WIN$N_M1.csv` está na pasta `data/`
3. **Execute o programa principal**:
   ```bash
   python run.py
   ```

O programa irá:
- ✅ Instalar automaticamente todas as dependências necessárias
- ✅ Carregar e processar os dados
- ✅ Realizar todas as análises (outliers, gaps, estatísticas)
- ✅ Gerar gráficos profissionais
- ✅ Criar relatórios detalhados
- ✅ Salvar todos os resultados

### Execução Manual (Opcional)

Se preferir instalar dependências manualmente:
```bash
pip install -r requirements.txt
python run.py
```

### Usando os Resultados

Após a execução, você pode usar os dados processados:
```python
import pandas as pd

# Carregar dados limpos finais
dados = pd.read_csv('data/processed/dados_limpos_finais.csv', 
                   index_col=0, parse_dates=True)

# Carregar análise de gaps
gaps = pd.read_csv('data/processed/gaps_analisados.csv',
                  index_col=0, parse_dates=True)

# Suas análises customizadas aqui...
```

### Exemplos Avançados

Execute exemplos de análises customizadas:
```bash
python exemplos_uso.py
```

## 📁 Estrutura do Projeto

```
projeto/
├── run.py                    # Arquivo principal - execute este
├── src/
│   ├── data_processor.py     # Processamento e agregação de dados
│   ├── outlier_analyzer.py   # Análise de outliers
│   ├── gap_analyzer.py       # Análise de gaps
│   └── visualizer.py         # Geração de gráficos
├── data/
│   ├── WIN$N_M1.csv         # Dados originais (você deve fornecer)
│   └── processed/           # Dados processados (gerado automaticamente)
├── output/
│   ├── graphs/              # Gráficos gerados
│   └── reports/             # Relatórios gerados
└── README.md               # Este arquivo
```

## 📊 Resultados Gerados

### Arquivos de Dados
- `dados_diarios.csv` - Dados agregados por dia
- `gaps_analisados.csv` - Análise completa dos gaps
- `dados_limpos_finais.csv` - Dataset final para trading

### Gráficos
- `evolucao_precos.png` - Evolução temporal dos preços
- `analise_gaps.png` - Análise visual dos gaps
- `comparacao_datasets.png` - Antes vs depois da limpeza

### Relatórios
- `relatorio_completo.txt` - Relatório detalhado da análise

## 📈 Métricas Principais

Com base nos dados analisados (2020-2023):

- **603 dias** de negociação processados
- **539 gaps significativos** identificados (≥100 pontos)
- **88.7% de taxa de fechamento** dos gaps
- **4.2 dias** tempo médio para fechamento
- **1.93%** volatilidade média diária

## 🔧 Configurações

Você pode ajustar os parâmetros no arquivo `run.py`:

```python
# Configurações principais
GAP_MINIMO = 100           # Gap mínimo em pontos para análise
OUTLIER_THRESHOLD = 1.5    # Multiplicador IQR para outliers
DIAS_LIMITE_GAP = 30       # Dias para verificar fechamento de gap
```

## 💡 Interpretação dos Resultados

### Gaps
- **Gap Up**: Abertura acima do fechamento anterior
- **Gap Down**: Abertura abaixo do fechamento anterior
- **Gap Fechado**: Preço retornou ao nível anterior ao gap
- **Taxa de Fechamento**: % de gaps que foram fechados

### Outliers
- Detectados usando método IQR (Interquartile Range)
- Mantidos se representam < 5% dos dados
- Removidos se muito numerosos e distorcem análise

### Dataset Final
- Dados limpos sem gaps não fechados
- Pronto para backtesting de estratégias
- Estatísticas normalizadas e consistentes

## 🚨 Solução de Problemas

### Erro: "Arquivo WIN$N_M1.csv não encontrado"
- Certifique-se de que o arquivo está na pasta `data/`
- Verifique se o nome está correto (incluindo o símbolo $)

### Erro: "Módulo não encontrado"
- O programa instala dependências automaticamente
- Se persistir, execute: `pip install pandas matplotlib numpy scipy`

### Erro: "Memória insuficiente"
- Para arquivos muito grandes, aumente a memória virtual
- Ou processe em lotes menores modificando o código

## 📞 Suporte

Este projeto foi desenvolvido para análise de dados financeiros do mercado brasileiro. Para dúvidas ou melhorias, consulte o código fonte bem documentado.

## 📋 Dependências

- `pandas` - Manipulação de dados
- `numpy` - Computação numérica  
- `matplotlib` - Gráficos
- `scipy` - Estatísticas avançadas

Todas são instaladas automaticamente quando você executa `run.py`.

## 🎯 Próximos Passos Sugeridos

1. **Estratégias de Trading**: Use o dataset limpo para backtesting
2. **Análise Sazonal**: Estude padrões por mês/dia da semana
3. **Machine Learning**: Desenvolva modelos preditivos para gaps
4. **Risk Management**: Analise drawdowns e volatilidade
5. **Backtesting**: Implemente estratégias baseadas em gaps

---

**Developed for Brazilian Financial Market Analysis** 🇧🇷