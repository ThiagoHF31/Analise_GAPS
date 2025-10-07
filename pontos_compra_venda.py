# 🎯 PONTOS ESPECÍFICOS DE COMPRA E VENDA - WIN$N
# Script para mostrar exatamente QUANDO comprar e QUANDO vender com dados específicos

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("🎯 ANÁLISE DE PONTOS ESPECÍFICOS DE COMPRA E VENDA")
print("=" * 70)

# Carregar dados diários
print("📂 Carregando dados...")

try:
    # Tentar carregar dados já processados primeiro
    dados = pd.read_csv('dados_diarios_WIN.csv')
    dados['data'] = pd.to_datetime(dados['data'])
    print(f"✅ Dados diários carregados: {len(dados)} dias")
    
except FileNotFoundError:
    print("📂 Processando dados brutos WIN$N_M1.csv...")
    
    # Carregar dados brutos e processar
    dados_brutos = pd.read_csv('WIN$N_M1.csv', sep='\t')
    print(f"✅ Dados brutos carregados: {len(dados_brutos):,} registros")
    
    # Converter datas e horas
    dados_brutos['data'] = pd.to_datetime(dados_brutos['<DATE>'])
    
    # Agrupar por dia para obter dados diários
    dados = dados_brutos.groupby(dados_brutos['data'].dt.date).agg({
        '<OPEN>': 'first',
        '<HIGH>': 'max', 
        '<LOW>': 'min',
        '<CLOSE>': 'last',
        '<VOL>': 'sum'
    }).reset_index()
    
    dados.columns = ['data', 'abertura', 'maxima', 'minima', 'fechamento', 'volume']
    dados['data'] = pd.to_datetime(dados['data'])
    
    print(f"✅ Dados diários processados: {len(dados)} dias")
print(f"📅 Período: {dados['data'].min().strftime('%d/%m/%Y')} a {dados['data'].max().strftime('%d/%m/%Y')}")

# Função para calcular indicadores (mesma do arquivo principal)
def calcular_indicadores_tecnicos(df):
    """Calcula todos os indicadores técnicos necessários"""
    df = df.copy()
    
    # RSI (Relative Strength Index)
    delta = df['fechamento'].diff()
    ganho = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    perda = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = ganho / perda
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = df['fechamento'].ewm(span=12).mean()
    ema26 = df['fechamento'].ewm(span=26).mean()
    df['macd'] = ema12 - ema26
    df['macd_sinal'] = df['macd'].ewm(span=9).mean()
    df['macd_histograma'] = df['macd'] - df['macd_sinal']
    
    # Médias Móveis
    df['sma_20'] = df['fechamento'].rolling(window=20).mean()
    df['sma_50'] = df['fechamento'].rolling(window=50).mean()
    
    # Bollinger Bands
    bb_periodo = 20
    df['bb_media'] = df['fechamento'].rolling(window=bb_periodo).mean()
    bb_std = df['fechamento'].rolling(window=bb_periodo).std()
    df['bb_superior'] = df['bb_media'] + (bb_std * 2)
    df['bb_inferior'] = df['bb_media'] - (bb_std * 2)
    
    # Volume médio
    df['volume_ma'] = df['volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma']
    
    # Suporte e resistência (níveis significativos)
    df['maxima_local'] = df['fechamento'].rolling(window=10, center=True).max() == df['fechamento']
    df['minima_local'] = df['fechamento'].rolling(window=10, center=True).min() == df['fechamento']
    df['resistencia'] = df['maxima_local'] & (df['fechamento'].shift(1) < df['fechamento'])
    df['suporte'] = df['minima_local'] & (df['fechamento'].shift(1) > df['fechamento'])
    
    return df

# Calcular indicadores
dados = calcular_indicadores_tecnicos(dados)
dados['preco'] = dados['fechamento']  # Para compatibilidade

# === INTEGRAÇÃO COM CLASSES DE GAPS ===
print("\n🔍 INTEGRANDO COM ANÁLISE DE CLASSES DE GAPS...")

# Calcular GAPs diários
dados['gap'] = dados['abertura'] - dados['fechamento'].shift(1)
dados['gap_pct'] = dados['gap'] / dados['fechamento'].shift(1) * 100

# Classificar GAPs usando a metodologia que desenvolvemos
def classificar_gaps_por_quartis(gaps_pct):
    """Classifica gaps usando quartis (método superior ao K-means)"""
    q1 = gaps_pct.quantile(0.25)
    q3 = gaps_pct.quantile(0.75)
    
    classes = pd.Series(index=gaps_pct.index, dtype='object')
    classes[gaps_pct <= q1] = 'Gap Down Forte'
    classes[(gaps_pct > q1) & (gaps_pct < q3)] = 'Gap Neutro'
    classes[gaps_pct >= q3] = 'Gap Up Forte'
    
    return classes

# Aplicar classificação
dados['classe_gap'] = classificar_gaps_por_quartis(dados['gap_pct'].dropna())

# Estatísticas das classes
print("📊 DISTRIBUIÇÃO DAS CLASSES DE GAPS:")
distribuicao_classes = dados['classe_gap'].value_counts()
for classe, count in distribuicao_classes.items():
    pct = count / len(dados.dropna()) * 100
    print(f"   • {classe}: {count} dias ({pct:.1f}%)")

# Função de sinais MELHORADA com classes (mesma do arquivo principal)
def gerar_sinais_trading_com_classes(df):
    """Gera sinais de compra e venda baseados em múltiplos indicadores + classes de gaps"""
    sinais = pd.DataFrame(index=df.index)
    sinais['data'] = df['data']
    sinais['preco'] = df['fechamento']
    sinais['classe_gap'] = df['classe_gap']
    
    # Sinais RSI
    sinais['rsi_compra'] = (df['rsi'] < 30) & (df['rsi'].shift(1) >= 30)
    sinais['rsi_venda'] = (df['rsi'] > 70) & (df['rsi'].shift(1) <= 70)
    
    # Sinais MACD
    sinais['macd_compra'] = (df['macd'] > df['macd_sinal']) & (df['macd'].shift(1) <= df['macd_sinal'].shift(1))
    sinais['macd_venda'] = (df['macd'] < df['macd_sinal']) & (df['macd'].shift(1) >= df['macd_sinal'].shift(1))
    
    # Sinais Médias Móveis
    sinais['ma_compra'] = (df['fechamento'] > df['sma_20']) & (df['sma_20'] > df['sma_50'])
    sinais['ma_venda'] = (df['fechamento'] < df['sma_20']) & (df['sma_20'] < df['sma_50'])
    
    # Sinais Bollinger Bands
    sinais['bb_compra'] = df['fechamento'] < df['bb_inferior']
    sinais['bb_venda'] = df['fechamento'] > df['bb_superior']
    
    # NOVO: Sinais baseados em classes de GAPs
    sinais['gap_compra'] = df['classe_gap'] == 'Gap Down Forte'  # Gap Down = oportunidade de compra
    sinais['gap_venda'] = df['classe_gap'] == 'Gap Up Forte'     # Gap Up = oportunidade de venda
    
    # Volume alto (confirmação)
    sinais['volume_alto'] = df['volume_ratio'] > 1.2
    
    # Scores de compra e venda MELHORADOS (incluindo gaps)
    sinais['compra_score'] = (
        sinais['rsi_compra'].astype(int) + 
        sinais['macd_compra'].astype(int) + 
        sinais['ma_compra'].astype(int) + 
        sinais['bb_compra'].astype(int) +
        sinais['gap_compra'].astype(int)  # NOVO: peso para gaps
    )
    sinais['venda_score'] = (
        sinais['rsi_venda'].astype(int) + 
        sinais['macd_venda'].astype(int) + 
        sinais['ma_venda'].astype(int) + 
        sinais['bb_venda'].astype(int) +
        sinais['gap_venda'].astype(int)  # NOVO: peso para gaps
    )
    
    # Sinais finais MELHORADOS (score >= 2 OU combinações específicas incluindo gaps)
    sinais['COMPRA'] = (
        (sinais['compra_score'] >= 2) | 
        (sinais['rsi_compra'] & sinais['bb_compra']) |
        (sinais['macd_compra'] & sinais['ma_compra']) |
        (sinais['gap_compra'] & sinais['rsi_compra']) |  # NOVO: Gap Down + RSI
        (sinais['gap_compra'] & sinais['bb_compra'])     # NOVO: Gap Down + Bollinger
    )
    sinais['VENDA'] = (
        (sinais['venda_score'] >= 2) | 
        (sinais['rsi_venda'] & sinais['bb_venda']) |
        (sinais['macd_venda'] & sinais['ma_venda']) |
        (sinais['gap_venda'] & sinais['rsi_venda']) |    # NOVO: Gap Up + RSI
        (sinais['gap_venda'] & sinais['bb_venda'])       # NOVO: Gap Up + Bollinger
    )
    
    return sinais

# Gerar sinais com classes integradas
sinais = gerar_sinais_trading_com_classes(dados)

# EXTRAIR PONTOS ESPECÍFICOS DE COMPRA E VENDA
print("\n🔍 EXTRAINDO PONTOS ESPECÍFICOS...")

# Filtrar apenas dias com sinais
pontos_compra = sinais[sinais['COMPRA']].copy()
pontos_venda = sinais[sinais['VENDA']].copy()

print(f"✅ Encontrados {len(pontos_compra)} pontos de COMPRA")
print(f"✅ Encontrados {len(pontos_venda)} pontos de VENDA")

# MOSTRAR PONTOS DE COMPRA DETALHADOS
if len(pontos_compra) > 0:
    print("\n" + "=" * 70)
    print("📈 PONTOS ESPECÍFICOS DE COMPRA")
    print("=" * 70)
    
    for i, (idx, ponto) in enumerate(pontos_compra.iterrows(), 1):
        # Buscar dados do dia correspondente
        dados_dia = dados.loc[idx]
        sinais_dia = sinais.loc[idx]
        
        print(f"\n🟢 COMPRA #{i}:")
        print(f"   📅 Data: {ponto['data'].strftime('%d/%m/%Y (%A)')}")
        print(f"   💰 Preço: {ponto['preco']:,.0f} pontos")
        print(f"   📊 Score: {sinais_dia['compra_score']}/5")  # Agora são 5 indicadores
        
        # Mostrar quais indicadores deram sinal
        indicadores_ativos = []
        if sinais_dia['rsi_compra']:
            indicadores_ativos.append(f"RSI ({dados_dia['rsi']:.1f} < 30)")
        if sinais_dia['macd_compra']:
            indicadores_ativos.append("MACD (cruzamento alta)")
        if sinais_dia['ma_compra']:
            indicadores_ativos.append("Médias Móveis (tendência alta)")
        if sinais_dia['bb_compra']:
            indicadores_ativos.append("Bollinger (preço < banda inferior)")
        if sinais_dia['gap_compra']:
            indicadores_ativos.append(f"Gap Down Forte ({dados_dia['gap_pct']:.2f}%)")
        
        print(f"   🎯 Indicadores: {', '.join(indicadores_ativos)}")
        print(f"   📦 Volume: {dados_dia['volume']:,.0f} (ratio: {dados_dia['volume_ratio']:.1f}x)")
        print(f"   🔸 Classe Gap: {dados_dia['classe_gap']}")
        
        # Contexto do mercado
        if dados_dia['volume_ratio'] > 1.5:
            print(f"   🐋 Volume ALTO - possível big player")
        if dados_dia['resistencia']:
            print(f"   ⚠️  Próximo a resistência")
        if dados_dia['suporte']:
            print(f"   ✅ Próximo a suporte")

# MOSTRAR PONTOS DE VENDA DETALHADOS
if len(pontos_venda) > 0:
    print("\n" + "=" * 70)
    print("📉 PONTOS ESPECÍFICOS DE VENDA")
    print("=" * 70)
    
    for i, (idx, ponto) in enumerate(pontos_venda.iterrows(), 1):
        # Buscar dados do dia correspondente
        dados_dia = dados.loc[idx]
        sinais_dia = sinais.loc[idx]
        
        print(f"\n🔴 VENDA #{i}:")
        print(f"   📅 Data: {ponto['data'].strftime('%d/%m/%Y (%A)')}")
        print(f"   💰 Preço: {ponto['preco']:,.0f} pontos")
        print(f"   📊 Score: {sinais_dia['venda_score']}/5")  # Agora são 5 indicadores
        
        # Mostrar quais indicadores deram sinal
        indicadores_ativos = []
        if sinais_dia['rsi_venda']:
            indicadores_ativos.append(f"RSI ({dados_dia['rsi']:.1f} > 70)")
        if sinais_dia['macd_venda']:
            indicadores_ativos.append("MACD (cruzamento baixa)")
        if sinais_dia['ma_venda']:
            indicadores_ativos.append("Médias Móveis (tendência baixa)")
        if sinais_dia['bb_venda']:
            indicadores_ativos.append("Bollinger (preço > banda superior)")
        if sinais_dia['gap_venda']:
            indicadores_ativos.append(f"Gap Up Forte ({dados_dia['gap_pct']:.2f}%)")
        
        print(f"   🎯 Indicadores: {', '.join(indicadores_ativos)}")
        print(f"   📦 Volume: {dados_dia['volume']:,.0f} (ratio: {dados_dia['volume_ratio']:.1f}x)")
        print(f"   🔸 Classe Gap: {dados_dia['classe_gap']}")
        
        # Contexto do mercado
        if dados_dia['volume_ratio'] > 1.5:
            print(f"   🐋 Volume ALTO - possível big player")
        if dados_dia['resistencia']:
            print(f"   ✅ Próximo a resistência")
        if dados_dia['suporte']:
            print(f"   ⚠️  Próximo a suporte")

# CRIAR TABELA RESUMO
print("\n" + "=" * 70)
print("📋 TABELA RESUMO DE TODOS OS SINAIS")
print("=" * 70)

# Combinar compra e venda
todos_sinais = []

for idx, ponto in pontos_compra.iterrows():
    dados_dia = dados.loc[idx]
    sinais_dia = sinais.loc[idx]
    todos_sinais.append({
        'Data': ponto['data'].strftime('%d/%m/%Y'),
        'Tipo': 'COMPRA',
        'Preço': f"{ponto['preco']:,.0f}",
        'Score': f"{sinais_dia['compra_score']}/5",  # Agora são 5 indicadores
        'Volume_Ratio': f"{dados_dia['volume_ratio']:.1f}x",
        'RSI': f"{dados_dia['rsi']:.1f}",
        'Classe_Gap': dados_dia['classe_gap'],
        'Gap_Pct': f"{dados_dia['gap_pct']:.2f}%"
    })

for idx, ponto in pontos_venda.iterrows():
    dados_dia = dados.loc[idx]
    sinais_dia = sinais.loc[idx]
    todos_sinais.append({
        'Data': ponto['data'].strftime('%d/%m/%Y'),
        'Tipo': 'VENDA',
        'Preço': f"{ponto['preco']:,.0f}",
        'Score': f"{sinais_dia['venda_score']}/5",  # Agora são 5 indicadores
        'Volume_Ratio': f"{dados_dia['volume_ratio']:.1f}x",
        'RSI': f"{dados_dia['rsi']:.1f}",
        'Classe_Gap': dados_dia['classe_gap'],
        'Gap_Pct': f"{dados_dia['gap_pct']:.2f}%"
    })

# Ordenar por data
df_resumo = pd.DataFrame(todos_sinais)
if len(df_resumo) > 0:
    df_resumo['Data_Sort'] = pd.to_datetime(df_resumo['Data'], format='%d/%m/%Y')
    df_resumo = df_resumo.sort_values('Data_Sort').drop('Data_Sort', axis=1)
    
    print(df_resumo.to_string(index=False))
    
    # Salvar tabela
    df_resumo.to_csv('pontos_compra_venda_detalhados.csv', index=False)
    print(f"\n💾 Tabela salva em: pontos_compra_venda_detalhados.csv")

# CRIAR GRÁFICO ESPECÍFICO DOS PONTOS - TODOS OS 602 DIAS
print("\n📊 Gerando gráfico com pontos específicos usando TODOS os dados...")

plt.figure(figsize=(20, 12))

# USAR TODOS OS DADOS (não apenas últimos 6 meses)
periodo_completo = dados.copy()
sinais_completo = sinais.copy()

print(f"📅 Período completo: {len(periodo_completo)} dias de {periodo_completo['data'].min().strftime('%d/%m/%Y')} a {periodo_completo['data'].max().strftime('%d/%m/%Y')}")

# Plotar preços
plt.plot(periodo_completo['data'], periodo_completo['fechamento'], 
         label='Preço WIN$N', linewidth=1.5, color='black', alpha=0.8)

# Plotar médias móveis
plt.plot(periodo_completo['data'], periodo_completo['sma_20'], 
         label='SMA 20', alpha=0.6, color='blue', linewidth=1)
plt.plot(periodo_completo['data'], periodo_completo['sma_50'], 
         label='SMA 50', alpha=0.6, color='red', linewidth=1)

# Bollinger Bands
plt.fill_between(periodo_completo['data'], 
                periodo_completo['bb_superior'], 
                periodo_completo['bb_inferior'], 
                alpha=0.05, color='gray', label='Bollinger Bands')

# Pontos de COMPRA por classe
compras_completo = sinais_completo[sinais_completo['COMPRA']].copy()
if not compras_completo.empty:
    # Separar por classes
    compras_gap_down = compras_completo[compras_completo['classe_gap'] == 'Gap Down Forte']
    compras_neutro = compras_completo[compras_completo['classe_gap'] == 'Gap Neutro']
    compras_gap_up = compras_completo[compras_completo['classe_gap'] == 'Gap Up Forte']
    
    # Plotar com cores diferentes por classe
    if not compras_gap_down.empty:
        plt.scatter(compras_gap_down['data'], compras_gap_down['preco'], 
                   color='darkgreen', marker='^', s=150, 
                   label=f'🟢 COMPRA Gap Down ({len(compras_gap_down)})', 
                   zorder=5, edgecolors='black', linewidth=1, alpha=0.8)
    
    if not compras_neutro.empty:
        plt.scatter(compras_neutro['data'], compras_neutro['preco'], 
                   color='green', marker='^', s=100, 
                   label=f'🟢 COMPRA Neutro ({len(compras_neutro)})', 
                   zorder=4, edgecolors='black', linewidth=1, alpha=0.7)
    
    if not compras_gap_up.empty:
        plt.scatter(compras_gap_up['data'], compras_gap_up['preco'], 
                   color='lightgreen', marker='^', s=100, 
                   label=f'🟢 COMPRA Gap Up ({len(compras_gap_up)})', 
                   zorder=3, edgecolors='black', linewidth=1, alpha=0.6)

# Pontos de VENDA por classe
vendas_completo = sinais_completo[sinais_completo['VENDA']].copy()
if not vendas_completo.empty:
    # Separar por classes
    vendas_gap_down = vendas_completo[vendas_completo['classe_gap'] == 'Gap Down Forte']
    vendas_neutro = vendas_completo[vendas_completo['classe_gap'] == 'Gap Neutro']
    vendas_gap_up = vendas_completo[vendas_completo['classe_gap'] == 'Gap Up Forte']
    
    # Plotar com cores diferentes por classe
    if not vendas_gap_down.empty:
        plt.scatter(vendas_gap_down['data'], vendas_gap_down['preco'], 
                   color='lightcoral', marker='v', s=100, 
                   label=f'🔴 VENDA Gap Down ({len(vendas_gap_down)})', 
                   zorder=3, edgecolors='black', linewidth=1, alpha=0.6)
    
    if not vendas_neutro.empty:
        plt.scatter(vendas_neutro['data'], vendas_neutro['preco'], 
                   color='red', marker='v', s=100, 
                   label=f'🔴 VENDA Neutro ({len(vendas_neutro)})', 
                   zorder=4, edgecolors='black', linewidth=1, alpha=0.7)
    
    if not vendas_gap_up.empty:
        plt.scatter(vendas_gap_up['data'], vendas_gap_up['preco'], 
                   color='darkred', marker='v', s=150, 
                   label=f'🔴 VENDA Gap Up ({len(vendas_gap_up)})', 
                   zorder=5, edgecolors='black', linewidth=1, alpha=0.8)

plt.title('🎯 PONTOS ESPECÍFICOS DE COMPRA E VENDA COM CLASSES DE GAPS - WIN$N\n' + 
          f'Período COMPLETO: {periodo_completo["data"].min().strftime("%d/%m/%Y")} a {periodo_completo["data"].max().strftime("%d/%m/%Y")} ({len(periodo_completo)} dias)', 
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Data', fontsize=12)
plt.ylabel('Preço (pontos)', fontsize=12)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

# Salvar gráfico
plt.savefig('pontos_compra_venda_completo_com_classes.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

print("✅ Gráfico salvo: pontos_compra_venda_completo_com_classes.png")

# ANÁLISE DETALHADA POR CLASSE DE GAP
print("\n" + "=" * 70)
print("📊 ANÁLISE DETALHADA POR CLASSE DE GAP")
print("=" * 70)

# Estatísticas por classe
for classe in ['Gap Down Forte', 'Gap Neutro', 'Gap Up Forte']:
    dados_classe = dados[dados['classe_gap'] == classe]
    sinais_classe = sinais[sinais['classe_gap'] == classe]
    
    compras_classe = sinais_classe[sinais_classe['COMPRA']]
    vendas_classe = sinais_classe[sinais_classe['VENDA']]
    
    print(f"\n🔸 {classe.upper()}:")
    print(f"   • Total de dias: {len(dados_classe)}")
    print(f"   • Sinais de compra: {len(compras_classe)} ({len(compras_classe)/len(dados_classe)*100:.1f}%)")
    print(f"   • Sinais de venda: {len(vendas_classe)} ({len(vendas_classe)/len(dados_classe)*100:.1f}%)")
    
    if len(dados_classe) > 0:
        retorno_medio = dados_classe['gap_pct'].mean()
        volatilidade = dados_classe['gap_pct'].std()
        print(f"   • Gap médio: {retorno_medio:.2f}%")
        print(f"   • Volatilidade: {volatilidade:.2f}%")
        
        # Melhores momentos
        if classe == 'Gap Down Forte':
            print(f"   ✅ MELHOR PARA: COMPRA após gap down (oportunidade)")
            print(f"   💡 Estratégia: Comprar quando RSI < 30 + Gap Down")
        elif classe == 'Gap Up Forte':
            print(f"   ✅ MELHOR PARA: VENDA após gap up (realizando lucros)")
            print(f"   💡 Estratégia: Vender quando RSI > 70 + Gap Up")
        else:
            print(f"   ✅ MELHOR PARA: Seguir tendência com indicadores técnicos")
            print(f"   💡 Estratégia: Aguardar confirmação de 2+ indicadores")

# RESUMO FINAL
print("\n" + "=" * 70)
print("🎯 RESUMO FINAL - PONTOS DE ENTRADA E SAÍDA")
print("=" * 70)

print(f"""
📊 ESTATÍSTICAS MELHORADAS:
   • Total de sinais de COMPRA: {len(pontos_compra)}
   • Total de sinais de VENDA: {len(pontos_venda)}
   • Frequência total: {(len(pontos_compra) + len(pontos_venda)) / len(dados) * 100:.1f}% dos dias
   
📅 PERÍODO ANALISADO (COMPLETO):
   • De: {dados['data'].min().strftime('%d/%m/%Y')}
   • Até: {dados['data'].max().strftime('%d/%m/%Y')}
   • Total de dias: {len(dados)} dias de negociação

🎯 ESTRATÉGIAS POR CLASSE:
   • Gap Down Forte → COMPRAR (oportunidade de entrada)
   • Gap Up Forte → VENDER (realizando lucros)
   • Gap Neutro → Seguir indicadores técnicos

💡 COMO USAR (VERSÃO MELHORADA):
   1. Identifique a classe do gap diário
   2. Para Gap Down: Procure sinais de COMPRA (RSI<30 + BB)
   3. Para Gap Up: Procure sinais de VENDA (RSI>70 + BB)
   4. Para Neutro: Aguarde 2+ indicadores concordarem
   5. Confirme sempre com volume alto (>1.2x da média)
   6. Execute no preço do fechamento
   7. Use stop loss baseado em suporte/resistência

📁 ARQUIVOS GERADOS:
   • pontos_compra_venda_detalhados.csv → Tabela completa com classes
   • pontos_compra_venda_completo_com_classes.png → Gráfico período total
""")

print("✅ ANÁLISE COMPLETA MELHORADA! Todos os pontos identificados com classes de GAPs integradas.")
print("🎯 Agora você tem estratégias específicas para cada tipo de gap do mercado!")