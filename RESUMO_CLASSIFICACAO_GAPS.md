# 📊 ANÁLISE DE CLASSIFICAÇÃO DE GAPS - RESUMO EXECUTIVO

## 🎯 Objetivo
Análise estatística para classificação otimizada de gaps em intervalos com base em distribuição estatística, gerando métricas detalhadas para desenvolvimento de modelos preditivos.

## 📈 Método de Classificação Utilizado
**Método Selecionado**: **Quartis** (melhor balanceamento estatístico)

Foram avaliados 5 métodos:
- Quantis uniformes
- **Quartis** ✅ (selecionado)
- Regra de Sturges
- K-means clustering
- Intervalos customizados de mercado

## 📊 TABELA RESUMO - MÉTRICAS POR CLASSE

| Intervalo | N° Obs | Gap Up | Gap Down | P(Fechar Up) | P(Fechar Down) | Ampl. Máx | T. Fechamento Up | T. Fechamento Down | Volatilidade |
|-----------|--------|---------|----------|--------------|----------------|-----------|------------------|-------------------|--------------|
| **100-265** | 139 (25.8%) | 78 (56.1%) | 54 (38.8%) | **92.3%** | 83.3% | 4,130 | **2.8 dias** | **3.0 dias** | **1.83%** |
| **265-455** | 131 (24.3%) | 73 (55.7%) | 58 (44.3%) | 87.7% | **94.8%** | 4,470 | 3.4 dias | 4.6 dias | 1.84% |
| **455-748** | 133 (24.7%) | 69 (51.9%) | 64 (48.1%) | 88.4% | 85.9% | 5,300 | 3.8 dias | 3.3 dias | 1.99% |
| **748-5360** | 135 (25.1%) | 72 (53.3%) | 63 (46.7%) | 87.5% | 87.3% | 5,950 | 6.0 dias | 7.1 dias | **2.14%** |

## 🔍 INSIGHTS ESTATÍSTICOS PRINCIPAIS

### ✅ **Probabilidades de Fechamento**
- **Gaps pequenos (100-265)**: Maior probabilidade para Gap Up (92.3%)
- **Gaps médios (265-455)**: Maior probabilidade para Gap Down (94.8%)
- **Padrão geral**: 83-95% de probabilidade de fechamento

### ⏱️ **Tempos de Fechamento**
- **Gaps pequenos**: Mais rápidos (2.8-3.0 dias)
- **Gaps grandes**: Mais lentos (6.0-7.1 dias)
- **Tempo para pico**: 1.4-3.6 dias (menor que tempo de fechamento)

### 📊 **Volatilidade e Amplitude**
- **Correlação positiva**: Gaps maiores = maior volatilidade
- **Range de volatilidade**: 1.83% - 2.14%
- **Amplitude máxima**: Até 5,950 pontos

## 🎯 RECOMENDAÇÕES PARA MODELO PREDITIVO

### 🔹 **Features Mais Relevantes**
1. **gap_absoluto** - Tamanho do gap (principal classificador)
2. **tipo_gap** - Direção (Up/Down) 
3. **volatilidade** - Indicador de risco
4. **amplitude** - Movimento máximo esperado
5. **gap_class_encoded** - Classe numérica para ML

### 🔹 **Estratégias por Classe**
- **100-265**: Estratégia de reversão rápida (alta probabilidade, baixo risco)
- **265-455**: Estratégia balanceada (boa probabilidade, risco moderado)
- **455-748**: Estratégia de timing (probabilidade boa, maior paciência)
- **748+**: Estratégia de longo prazo (alta volatilidade, maior tempo)

## 📁 DATASETS GERADOS

### 1. **gaps_classificados.csv** (538 registros)
- Dados originais + classificação por intervalo
- Uso: Análise exploratória e validação

### 2. **metricas_por_classe.csv** (4 classes)
- Métricas estatísticas por intervalo
- Uso: Parametrização de estratégias

### 3. **features_para_modelo.csv** (538 registros, 10 features)
- Dataset preparado para machine learning
- Features numéricas e categóricas codificadas
- **Uso principal**: Treinamento de modelos preditivos

## 🧠 CONCLUSÕES ESTATÍSTICAS

1. **Distribuição não-normal** dos gaps (p-value < 0.05)
2. **Classificação por quartis** oferece melhor balanceamento
3. **Alta previsibilidade**: 83-95% de taxa de fechamento
4. **Relação tempo-tamanho**: Gaps maiores demoram mais para fechar
5. **Oportunidade de arbitragem**: Padrões estatisticamente significativos

---
*Análise gerada em: Outubro 2025*  
*Base de dados: 538 gaps significativos (≥100 pontos)*  
*Período analisado: 2020-2023*