# Análise de Dados Financeiros WIN$N M1 📊

Este projeto realiza uma **análise completa e avançada** de dados financeiros do índice WIN$N (Mini Índice Bovespa) em timeframe de 1 minuto, incluindo agregação diária, detecção de outliers, análise de gaps, **classificação estatística de gaps** e geração de visualizações profissionais.

## � Funcionalidades Principais

- **Agregação de Dados**: Converte dados de minuto para diário com estatísticas OHLCV
- **Análise de Outliers**: Detecta e trata valores anômalos usando método IQR
- **Análise de Gaps**: Identifica gaps de abertura e verifica seu fechamento
- **🆕 Classificação Estatística de Gaps**: Classifica gaps em 4 intervalos otimizados usando análise de quartis
- **🆕 Análise Preditiva**: Calcula probabilidades de fechamento, tempos médios e métricas por classe
- **Visualizações Avançadas**: Gera 7 gráficos profissionais de análise temporal, gaps e classificação
- **Datasets para ML**: Produz dados limpos e features preparadas para machine learning
- **Relatórios Detalhados**: Gera análises estatísticas completas com insights para trading

## 🚀 Como Usar

### Instalação e Execução Automática

1. **Baixe ou clone o projeto**
2. **Coloque seu arquivo de dados**: Certifique-se de que o arquivo `WIN$N_M1.csv` está na pasta `data/`
3. **Execute o programa principal**:
   ```bash
   python run.py
   ```

O programa irá executar **6 etapas completas**:
- ✅ Instalar automaticamente todas as dependências necessárias
- ✅ Carregar e processar os dados (agregação diária)
- ✅ Realizar análise de outliers com método IQR
- ✅ Executar análise completa de gaps (identificação e fechamento)
- ✅ **🆕 Classificar gaps estatisticamente em 4 intervalos otimizados**
- ✅ **🆕 Calcular métricas preditivas (probabilidades, tempos, volatilidade)**
- ✅ Gerar 7 gráficos profissionais de análise
- ✅ Criar relatórios detalhados com insights para trading
- ✅ Salvar todos os resultados e datasets

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

# 🆕 Carregar gaps classificados
gaps_classificados = pd.read_csv('data/processed/gaps_classificados.csv',
                                index_col=0, parse_dates=True)

# 🆕 Carregar métricas por classe
metricas = pd.read_csv('data/processed/metricas_por_classe.csv')

# 🆕 Carregar features para machine learning
features = pd.read_csv('data/processed/features_para_modelo.csv',
                      index_col=0, parse_dates=True)

# Exemplo: Análise de probabilidades por classe
print(metricas[['intervalo', 'prob_fechamento_up', 'prob_fechamento_down']])
```

### Exemplos Avançados

Execute exemplos de análises customizadas:
```bash
python exemplos_uso.py
```

## 📁 Estrutura do Projeto

```
projeto/
├── run.py                              # 🚀 Arquivo principal - execute este
├── src/
│   ├── data_processor.py               # Processamento e agregação de dados
│   ├── outlier_analyzer.py             # Análise de outliers
│   ├── gap_analyzer.py                 # Análise de gaps
│   ├── gap_classification_analyzer.py  # 🆕 Classificação estatística de gaps
│   ├── visualizer.py                   # Geração de gráficos
│   └── report_generator.py             # Geração de relatórios
├── data/
│   ├── WIN$N_M1.csv                   # Dados originais (você deve fornecer)
│   └── processed/                     # 📊 Dados processados (gerado automaticamente)
│       ├── dados_diarios.csv          # Dados agregados por dia
│       ├── gaps_analisados.csv        # Análise completa dos gaps
│       ├── gaps_classificados.csv     # 🆕 Gaps com classificação estatística
│       ├── metricas_por_classe.csv    # 🆕 Métricas detalhadas por classe
│       ├── features_para_modelo.csv   # 🆕 Features preparadas para ML
│       └── dados_limpos_finais.csv    # Dataset final para trading
├── output/
│   ├── graphs/                        # 📈 Gráficos gerados (7 arquivos)
│   └── reports/                       # 📄 Relatórios gerados
├── gap_classification_analysis.py     # Script standalone para classificação
├── generate_gap_report.py             # Gerador de relatórios detalhados
└── README.md                          # Este arquivo
```

## 📊 Resultados Gerados

### Arquivos de Dados (8 datasets)
- `dados_diarios.csv` - Dados agregados por dia
- `gaps_analisados.csv` - Análise completa dos gaps
- `dados_limpos_finais.csv` - Dataset final para trading
- **🆕 `gaps_classificados.csv`** - Gaps com classificação estatística em 4 classes
- **🆕 `metricas_por_classe.csv`** - Métricas detalhadas por classe de gap
- **🆕 `features_para_modelo.csv`** - Features preparadas para machine learning

### Gráficos (7 visualizações profissionais)
- `evolucao_precos.png` - Evolução temporal dos preços
- `analise_gaps.png` - Análise visual dos gaps
- `comparacao_datasets.png` - Antes vs depois da limpeza
- **🆕 `classificacao_distribuicao.png`** - Distribuição das classes de gaps
- **🆕 `classificacao_probabilidades.png`** - Probabilidades de fechamento por classe
- **🆕 `classificacao_tempos.png`** - Análise temporal por classe (pico e fechamento)
- **🆕 `classificacao_volatilidade.png`** - Volatilidade e amplitude por classe

### Relatórios
- `relatorio_completo.txt` - Relatório detalhado da análise
- `analise_outliers.txt` - Análise específica de outliers

## 📈 Métricas Principais

Com base nos dados analisados (2020-2023):

### 📊 Análise Geral
- **602 dias** de negociação processados
- **538 gaps significativos** identificados (≥100 pontos)
- **88.7% de taxa de fechamento** dos gaps
- **4.2 dias** tempo médio para fechamento
- **1.94%** volatilidade média diária

### 🎯 Classificação Estatística de Gaps (Novo!)

| Classe | N° Gaps | Gap Up | Gap Down | P(Fechar Up) | P(Fechar Down) | Tempo Médio | Volatilidade |
|--------|---------|---------|----------|--------------|----------------|-------------|--------------|
| **100-265** | 139 (25.8%) | 78 (56.1%) | 54 (38.8%) | **92.3%** | 83.3% | **2.8-3.0d** | **1.83%** |
| **265-455** | 131 (24.3%) | 73 (55.7%) | 58 (44.3%) | 87.7% | **94.8%** | 3.4-4.6d | 1.84% |
| **455-748** | 133 (24.7%) | 69 (51.9%) | 64 (48.1%) | 88.4% | 85.9% | 3.8-3.3d | 1.99% |
| **748-5360** | 135 (25.1%) | 72 (53.3%) | 63 (46.7%) | 87.5% | 87.3% | 6.0-7.1d | **2.14%** |

### 🧠 Insights Principais
- ✅ **Gaps pequenos (100-265)**: 92.3% probabilidade de fechamento em ~3 dias
- ✅ **Gaps médios (265-455)**: 94.8% probabilidade para Gap Down
- ⚡ **Fechamento mais rápido**: Gaps pequenos (~3 dias)
- 📈 **Maior volatilidade**: Gaps grandes (2.14%)

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

### 🆕 Classificação de Gaps
- **Classe 100-265**: Gaps pequenos - alta probabilidade, fechamento rápido, baixo risco
- **Classe 265-455**: Gaps médios - boa probabilidade, equilíbrio risco/retorno
- **Classe 455-748**: Gaps grandes - boa probabilidade, requer paciência
- **Classe 748+**: Gaps muito grandes - alta volatilidade, fechamento lento

### Outliers
- Detectados usando método IQR (Interquartile Range)
- Mantidos se representam < 5% dos dados
- Removidos se muito numerosos e distorcem análise

### Dataset Final
- Dados limpos sem gaps não fechados
- Pronto para backtesting de estratégias
- **🆕 Features preparadas para machine learning**
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

1. **🤖 Machine Learning**: Desenvolva modelos preditivos usando `features_para_modelo.csv`
2. **📊 Estratégias de Trading**: Use as probabilidades por classe para otimizar estratégias
3. **⏰ Análise Temporal**: Explore padrões por horário, dia da semana e sazonalidade
4. **🔍 Backtesting**: Implemente estratégias baseadas na classificação de gaps
5. **📈 Risk Management**: Use volatilidade por classe para dimensionar posições
6. **🎯 Otimização**: Ajuste stops e targets baseados na amplitude histórica por classe

### 🆕 Scripts Úteis Incluídos
- `gap_classification_analysis.py` - Análise standalone de classificação
- `generate_gap_report.py` - Gerador de relatórios detalhados Excel/PDF

---

**Developed for Brazilian Financial Market Analysis** 🇧🇷  
**🆕 Versão 2.0 - Com Análise Preditiva e Classificação Estatística**