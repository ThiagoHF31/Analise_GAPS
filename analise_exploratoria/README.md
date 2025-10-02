# 📊 Análise Exploratória - WIN$N Dados Brutos

## 🎯 Objetivo
Esta pasta contém uma **análise exploratória completa** dos dados brutos do arquivo `WIN$N_M1.csv`, focando na compreensão detalhada das variáveis e padrões presentes nos dados financeiros do Mini Índice Bovespa.

## 📁 Conteúdo da Pasta

### 📓 **analise_dados_brutos_WIN.ipynb**
Notebook principal com análise exploratória completa contendo:

#### 🔍 **Seções da Análise:**
1. **📦 Importação e Setup** - Bibliotecas e configurações
2. **📂 Carregamento dos Dados** - Leitura do WIN$N_M1.csv
3. **📋 Descrição das Variáveis** - Explicação detalhada de cada campo
4. **🔍 Exploração da Estrutura** - Tipos de dados, missing values, duplicatas
5. **📊 Estatísticas Descritivas** - Medidas de centralidade e dispersão
6. **📈 Visualizações Temporais** - Gráficos de séries temporais OHLCV
7. **📊 Análise de Distribuições** - Histogramas, boxplots, Q-Q plots
8. **🔗 Correlações** - Matriz de correlação entre variáveis
9. **🔍 Detecção de Outliers** - Método IQR e análise de padrões
10. **📋 Resumo Executivo** - Insights e próximos passos

## 🚀 Como Usar

### 1. **Executar o Notebook**
```bash
jupyter notebook analise_dados_brutos_WIN.ipynb
```

### 2. **Ou usar VS Code**
- Abrir o arquivo `.ipynb` no VS Code
- Executar células sequencialmente
- Visualizar gráficos inline

## 📊 Variáveis Analisadas

### 🔢 **Dados Financeiros (OHLCV):**
| Variável | Descrição | Significado |
|----------|-----------|-------------|
| **DateTime** | Timestamp | Data/hora do registro minuto a minuto |
| **Open** | Abertura | Primeiro preço negociado no minuto |
| **High** | Máxima | Maior preço atingido no minuto |
| **Low** | Mínima | Menor preço atingido no minuto |
| **Close** | Fechamento | Último preço negociado no minuto |
| **Volume** | Volume | Quantidade de contratos negociados |

## 📈 Visualizações Geradas

### 🎨 **Gráficos Principais:**
- **📈 Séries Temporais**: Evolução dos preços OHLC
- **📦 Volume**: Distribuição e padrões de negociação
- **📏 Spread**: Análise High-Low
- **📊 Retornos**: Movimentações percentuais
- **📊 Distribuições**: Histogramas de cada variável
- **🔗 Correlações**: Heatmap de correlações
- **🔍 Outliers**: Detecção e visualização de valores atípicos

## 🎯 Insights Esperados

### 📋 **Análises Realizadas:**
- ✅ **Qualidade dos Dados**: Missing values, duplicatas, consistência
- ✅ **Padrões Temporais**: Comportamento intraday
- ✅ **Distribuições**: Normalidade, assimetria, curtose
- ✅ **Volatilidade**: Clusters e padrões de risco
- ✅ **Correlações**: Relacionamentos entre variáveis
- ✅ **Outliers**: Identificação de valores extremos

### 🚀 **Aplicações:**
- **Trading Intraday**: Compreensão de padrões M1
- **Desenvolvimento de Estratégias**: Base para algoritmos
- **Risk Management**: Análise de volatilidade
- **Backtesting**: Dados limpos para testes históricos

## 📁 Saídas Geradas

### 💾 **Arquivos de Saída:**
- `dados_processados/WIN_dados_explorados.csv` - Dataset processado
- `dados_processados/WIN_estatisticas_resumo.csv` - Estatísticas resumo

## 🔗 Integração com o Projeto

Esta análise exploratória **complementa** o sistema principal de análise de gaps:
- **Dados Brutos** → Análise Exploratória (esta pasta)
- **Dados Processados** → Sistema Principal (pasta raiz)
- **Insights** → Estratégias de Trading

---

## 📚 **Para Desenvolvedores**

### 🛠️ **Dependências:**
```python
pandas >= 1.3.0
numpy >= 1.20.0
matplotlib >= 3.3.0
seaborn >= 0.11.0
scipy >= 1.7.0
plotly >= 5.0.0
jupyter >= 1.0.0
```

### 🚀 **Executar análise:**
```python
# No notebook, executar todas as células sequencialmente
# Ou executar programaticamente:
import subprocess
subprocess.run(["jupyter", "nbconvert", "--execute", "analise_dados_brutos_WIN.ipynb"])
```

---
**🎯 Esta análise fornece a fundação estatística para todas as análises subsequentes do projeto WIN$N!** 📊🚀