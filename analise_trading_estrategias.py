# 📊 Análise de Estratégias de Trading WIN$N
# Análise completa para decisões de compra/venda

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurações de visualização
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 11

print("🎯 ANÁLISE DE ESTRATÉGIAS DE TRADING WIN$N")
print("=" * 60)

# Carregar dados processados (se existirem) ou dados brutos
try:
    # Tentar carregar dados processados primeiro
    dados = pd.read_csv('data/processed/dados_diarios.csv')
    print("✅ Dados diários carregados com sucesso!")
    dados['data'] = pd.to_datetime(dados['data'])
except:
    # Fallback: carregar dados brutos e processar
    print("📂 Carregando dados brutos...")
    dados_brutos = pd.read_csv('WIN$N_M1.csv', sep='\t')
    
    # Processar dados para análise diária
    dados_brutos['DateTime'] = pd.to_datetime(dados_brutos['<DATE>'] + ' ' + dados_brutos['<TIME>'])
    dados_brutos['Date'] = dados_brutos['DateTime'].dt.date
    
    # Agregar por dia
    dados = dados_brutos.groupby('Date').agg({
        '<OPEN>': 'first',
        '<HIGH>': 'max', 
        '<LOW>': 'min',
        '<CLOSE>': 'last',
        '<VOL>': 'sum'
    }).reset_index()
    
    dados.columns = ['data', 'abertura', 'maxima', 'minima', 'fechamento', 'volume']
    dados['data'] = pd.to_datetime(dados['data'])
    
    print(f"✅ Dados processados: {len(dados)} dias de negociação")

# Calcular indicadores técnicos
def calcular_indicadores(df):
    """Calcula indicadores técnicos essenciais"""
    
    # Retornos
    df['retorno'] = df['fechamento'].pct_change()
    df['retorno_log'] = np.log(df['fechamento'] / df['fechamento'].shift(1))
    
    # Médias móveis
    df['sma_20'] = df['fechamento'].rolling(window=20).mean()
    df['sma_50'] = df['fechamento'].rolling(window=50).mean()
    df['ema_12'] = df['fechamento'].ewm(span=12).mean()
    df['ema_26'] = df['fechamento'].ewm(span=26).mean()
    
    # RSI (Índice de Força Relativa)
    def calcular_rsi(precos, periodo=14):
        delta = precos.diff()
        ganho = delta.where(delta > 0, 0)
        perda = (-delta).where(delta < 0, 0)
        
        media_ganho = ganho.rolling(window=periodo).mean()
        media_perda = perda.rolling(window=periodo).mean()
        
        rs = media_ganho / media_perda
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    df['rsi'] = calcular_rsi(df['fechamento'])
    
    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_sinal'] = df['macd'].ewm(span=9).mean()
    df['macd_histograma'] = df['macd'] - df['macd_sinal']
    
    # Bollinger Bands
    df['bb_medio'] = df['fechamento'].rolling(window=20).mean()
    df['bb_std'] = df['fechamento'].rolling(window=20).std()
    df['bb_superior'] = df['bb_medio'] + (df['bb_std'] * 2)
    df['bb_inferior'] = df['bb_medio'] - (df['bb_std'] * 2)
    
    # Suporte e Resistência (máximas/mínimas locais)
    def identificar_suporte_resistencia(precos, janela=20):
        maximas_locais = precos.rolling(window=janela, center=True).max()
        minimas_locais = precos.rolling(window=janela, center=True).min()
        
        resistencias = (precos == maximas_locais) & (precos.shift(1) < precos) & (precos.shift(-1) < precos)
        suportes = (precos == minimas_locais) & (precos.shift(1) > precos) & (precos.shift(-1) > precos)
        
        return suportes, resistencias
    
    df['suporte'], df['resistencia'] = identificar_suporte_resistencia(df['fechamento'])
    
    # Volume Profile Simplificado
    df['volume_ma'] = df['volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma']
    
    return df

# Aplicar indicadores
dados = calcular_indicadores(dados)

print(f"📊 Indicadores calculados para {len(dados)} registros")
print(f"📅 Período: {dados['data'].min().date()} a {dados['data'].max().date()}")

# === 1. QUANDO COMPRAR E QUANDO VENDER ===
print("\n" + "=" * 60)
print("💰 ESTRATÉGIAS DE COMPRA E VENDA")
print("=" * 60)

def gerar_sinais_trading(df):
    """Gera sinais de compra e venda baseados em múltiplos indicadores"""
    
    sinais = pd.DataFrame(index=df.index)
    sinais['preco'] = df['fechamento']
    sinais['data'] = df['data']
    
    # Sinais individuais
    # 1. RSI
    sinais['rsi_compra'] = (df['rsi'] < 30) & (df['rsi'].shift(1) >= 30)  # RSI saindo de sobrevenda
    sinais['rsi_venda'] = (df['rsi'] > 70) & (df['rsi'].shift(1) <= 70)   # RSI entrando em sobrecompra
    
    # 2. MACD
    sinais['macd_compra'] = (df['macd'] > df['macd_sinal']) & (df['macd'].shift(1) <= df['macd_sinal'].shift(1))
    sinais['macd_venda'] = (df['macd'] < df['macd_sinal']) & (df['macd'].shift(1) >= df['macd_sinal'].shift(1))
    
    # 3. Médias Móveis
    sinais['ma_compra'] = (df['fechamento'] > df['sma_20']) & (df['sma_20'] > df['sma_50'])
    sinais['ma_venda'] = (df['fechamento'] < df['sma_20']) & (df['sma_20'] < df['sma_50'])
    
    # 4. Bollinger Bands
    sinais['bb_compra'] = df['fechamento'] < df['bb_inferior']  # Preço abaixo da banda inferior
    sinais['bb_venda'] = df['fechamento'] > df['bb_superior']   # Preço acima da banda superior
    
    # 5. Volume
    sinais['volume_confirmacao'] = df['volume_ratio'] > 1.5  # Volume 50% acima da média
    
    # Sinais combinados (pelo menos 2 indicadores concordando)
    sinais['compra_score'] = (
        sinais['rsi_compra'].astype(int) + 
        sinais['macd_compra'].astype(int) + 
        sinais['ma_compra'].astype(int) + 
        sinais['bb_compra'].astype(int)
    )
    
    sinais['venda_score'] = (
        sinais['rsi_venda'].astype(int) + 
        sinais['macd_venda'].astype(int) + 
        sinais['ma_venda'].astype(int) + 
        sinais['bb_venda'].astype(int)
    )
    
    # Sinais finais (score >= 2 OU combinações específicas)
    sinais['COMPRA'] = (
        (sinais['compra_score'] >= 2) | 
        (sinais['rsi_compra'] & sinais['bb_compra']) |
        (sinais['macd_compra'] & sinais['ma_compra'])
    )
    sinais['VENDA'] = (
        (sinais['venda_score'] >= 2) | 
        (sinais['rsi_venda'] & sinais['bb_venda']) |
        (sinais['macd_venda'] & sinais['ma_venda'])
    )
    
    return sinais

sinais = gerar_sinais_trading(dados)

# Estatísticas dos sinais
compras = sinais[sinais['COMPRA']].shape[0]
vendas = sinais[sinais['VENDA']].shape[0]

print(f"📈 Sinais de COMPRA identificados: {compras}")
print(f"📉 Sinais de VENDA identificados: {vendas}")
print(f"📊 Frequência média: {(compras + vendas) / len(dados) * 100:.1f}% dos dias úteis")

# === 2. GRÁFICO DE SUPORTE E RESISTÊNCIA ===
print("\n" + "=" * 60)
print("📊 GRÁFICO DE SUPORTE E RESISTÊNCIA")
print("=" * 60)

# Plotar gráfico principal de análise técnica
fig, axes = plt.subplots(4, 1, figsize=(16, 20))
fig.suptitle('📊 ANÁLISE TÉCNICA COMPLETA WIN$N - Estratégias de Trading', fontsize=16, fontweight='bold')

# Últimos 100 dias para visualização clara
periodo_analise = dados.tail(100).copy()
sinais_periodo = sinais.tail(100).copy()

# Gráfico 1: Preços com Suporte/Resistência e Sinais
ax1 = axes[0]
ax1.plot(periodo_analise['data'], periodo_analise['fechamento'], label='Fechamento', linewidth=2, color='black')
ax1.plot(periodo_analise['data'], periodo_analise['sma_20'], label='SMA 20', alpha=0.7, color='blue')
ax1.plot(periodo_analise['data'], periodo_analise['sma_50'], label='SMA 50', alpha=0.7, color='red')

# Bollinger Bands
ax1.fill_between(periodo_analise['data'], periodo_analise['bb_superior'], periodo_analise['bb_inferior'], 
                alpha=0.2, color='gray', label='Bollinger Bands')

# Sinais de compra e venda
compras_periodo = sinais_periodo[sinais_periodo['COMPRA']]
vendas_periodo = sinais_periodo[sinais_periodo['VENDA']]

if not compras_periodo.empty:
    ax1.scatter(compras_periodo['data'], compras_periodo['preco'], 
               color='green', marker='^', s=100, label=f'COMPRA ({len(compras_periodo)})', zorder=5)

if not vendas_periodo.empty:
    ax1.scatter(vendas_periodo['data'], vendas_periodo['preco'], 
               color='red', marker='v', s=100, label=f'VENDA ({len(vendas_periodo)})', zorder=5)

# Identificar níveis de suporte e resistência principais
resistencias_periodo = periodo_analise[periodo_analise['resistencia']]
suportes_periodo = periodo_analise[periodo_analise['suporte']]

if not resistencias_periodo.empty:
    for _, ponto in resistencias_periodo.iterrows():
        ax1.axhline(y=ponto['fechamento'], color='red', linestyle='--', alpha=0.6, linewidth=1)
        ax1.text(periodo_analise['data'].iloc[-1], ponto['fechamento'], 
                f'R: {ponto["fechamento"]:.0f}', fontsize=9, color='red')

if not suportes_periodo.empty:
    for _, ponto in suportes_periodo.iterrows():
        ax1.axhline(y=ponto['fechamento'], color='green', linestyle='--', alpha=0.6, linewidth=1)
        ax1.text(periodo_analise['data'].iloc[-1], ponto['fechamento'], 
                f'S: {ponto["fechamento"]:.0f}', fontsize=9, color='green')

ax1.set_title('💰 Preços com Sinais de Trading e Suporte/Resistência')
ax1.set_ylabel('Preço (pontos)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Gráfico 2: RSI (Índice de Força Relativa)
ax2 = axes[1]
ax2.plot(periodo_analise['data'], periodo_analise['rsi'], label='RSI', linewidth=2, color='purple')
ax2.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Sobrecompra (70)')
ax2.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Sobrevenda (30)')
ax2.fill_between(periodo_analise['data'], 30, 70, alpha=0.1, color='gray')

ax2.set_title('📊 RSI - Índice de Força Relativa')
ax2.set_ylabel('RSI')
ax2.set_ylim(0, 100)
ax2.legend()
ax2.grid(True, alpha=0.3)

# Gráfico 3: MACD
ax3 = axes[2]
ax3.plot(periodo_analise['data'], periodo_analise['macd'], label='MACD', linewidth=2, color='blue')
ax3.plot(periodo_analise['data'], periodo_analise['macd_sinal'], label='Sinal', linewidth=2, color='red')
ax3.bar(periodo_analise['data'], periodo_analise['macd_histograma'], label='Histograma', alpha=0.6, color='gray')
ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)

ax3.set_title('📈 MACD - Convergência e Divergência de Médias Móveis')
ax3.set_ylabel('MACD')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Gráfico 4: Volume com Profile
ax4 = axes[3]
bars = ax4.bar(periodo_analise['data'], periodo_analise['volume'], alpha=0.6, color='lightblue')
ax4.plot(periodo_analise['data'], periodo_analise['volume_ma'], label='Volume Médio (20d)', color='red', linewidth=2)

# Destacar volumes anômalos
volume_alto = periodo_analise['volume_ratio'] > 2
if volume_alto.any():
    ax4.bar(periodo_analise[volume_alto]['data'], periodo_analise[volume_alto]['volume'], 
            alpha=0.8, color='orange', label='Volume Anômalo')

ax4.set_title('📦 Volume Profile - Big Players Detection')
ax4.set_ylabel('Volume')
ax4.set_xlabel('Data')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# === 3. BIG PLAYERS ANALYSIS ===
print("\n" + "=" * 60)
print("🐋 ANÁLISE DE BIG PLAYERS")
print("=" * 60)

def analisar_big_players(df):
    """Analisa movimentações de grandes investidores"""
    
    # Identificar dias com volume anômalo (possível atuação de big players)
    volume_threshold = df['volume'].quantile(0.95)  # Top 5% de volume
    big_player_days = df[df['volume'] >= volume_threshold].copy()
    
    # Analisar impacto no preço
    big_player_days['impacto_preco'] = abs(big_player_days['fechamento'] - big_player_days['abertura'])
    big_player_days['direcao'] = np.where(big_player_days['fechamento'] > big_player_days['abertura'], 'ALTA', 'BAIXA')
    
    print(f"📊 Dias com suspeita de Big Players: {len(big_player_days)}")
    print(f"📈 Volume médio normal: {df['volume'].median():,.0f}")
    print(f"🐋 Volume médio Big Players: {big_player_days['volume'].mean():,.0f}")
    print(f"📊 Multiplicador: {big_player_days['volume'].mean() / df['volume'].median():.1f}x")
    
    # Análise direcional
    alta_count = (big_player_days['direcao'] == 'ALTA').sum()
    baixa_count = (big_player_days['direcao'] == 'BAIXA').sum()
    
    print(f"\n🎯 Direcionamento dos Big Players:")
    print(f"   📈 Dias de alta: {alta_count} ({alta_count/len(big_player_days)*100:.1f}%)")
    print(f"   📉 Dias de baixa: {baixa_count} ({baixa_count/len(big_player_days)*100:.1f}%)")
    
    # Impacto médio no preço
    impacto_medio = big_player_days['impacto_preco'].mean()
    print(f"   💥 Impacto médio no preço: {impacto_medio:.0f} pontos")
    
    return big_player_days

big_players = analisar_big_players(dados)

# === 4. DISTRIBUIÇÃO DOS RETORNOS ===
print("\n" + "=" * 60)
print("📊 DISTRIBUIÇÃO DOS RETORNOS")
print("=" * 60)

# Análise estatística dos retornos
retornos = dados['retorno'].dropna()

print(f"📈 Estatísticas dos Retornos Diários:")
print(f"   • Retorno médio: {retornos.mean()*100:.3f}%")
print(f"   • Mediana: {retornos.median()*100:.3f}%")
print(f"   • Desvio padrão: {retornos.std()*100:.2f}%")
print(f"   • Skewness: {retornos.skew():.3f}")
print(f"   • Kurtosis: {retornos.kurtosis():.3f}")
print(f"   • Maior ganho: {retornos.max()*100:.2f}%")
print(f"   • Maior perda: {retornos.min()*100:.2f}%")

# Classificação dos retornos
dias_alta = (retornos > 0).sum()
dias_baixa = (retornos < 0).sum()
dias_neutro = (retornos == 0).sum()

print(f"\n📊 Distribuição dos Movimentos:")
print(f"   📈 Dias de alta: {dias_alta} ({dias_alta/len(retornos)*100:.1f}%)")
print(f"   📉 Dias de baixa: {dias_baixa} ({dias_baixa/len(retornos)*100:.1f}%)")
print(f"   ➡️  Dias neutros: {dias_neutro} ({dias_neutro/len(retornos)*100:.1f}%)")

# Gráfico de distribuição dos retornos
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('📊 ANÁLISE DA DISTRIBUIÇÃO DE RETORNOS WIN$N', fontsize=16, fontweight='bold')

# Histograma dos retornos
ax1 = axes[0, 0]
ax1.hist(retornos * 100, bins=50, alpha=0.7, color='skyblue', edgecolor='black', density=True)
ax1.axvline(retornos.mean() * 100, color='red', linestyle='--', linewidth=2, label=f'Média: {retornos.mean()*100:.3f}%')
ax1.axvline(retornos.median() * 100, color='green', linestyle='--', linewidth=2, label=f'Mediana: {retornos.median()*100:.3f}%')
ax1.set_title('📊 Distribuição dos Retornos Diários')
ax1.set_xlabel('Retorno (%)')
ax1.set_ylabel('Densidade')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Q-Q plot para testar normalidade
from scipy import stats
ax2 = axes[0, 1]
stats.probplot(retornos, dist="norm", plot=ax2)
ax2.set_title('📈 Q-Q Plot - Teste de Normalidade')
ax2.grid(True, alpha=0.3)

# Box plot dos retornos
ax3 = axes[1, 0]
ax3.boxplot(retornos * 100, vert=True)
ax3.set_title('📦 Box Plot - Retornos Diários')
ax3.set_ylabel('Retorno (%)')
ax3.grid(True, alpha=0.3)

# Retornos ao longo do tempo
ax4 = axes[1, 1]
dados_retornos = dados[dados['retorno'].notna()].copy()
ax4.plot(dados_retornos['data'], dados_retornos['retorno'] * 100, alpha=0.7, color='purple')
ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
ax4.set_title('📈 Retornos ao Longo do Tempo')
ax4.set_xlabel('Data')
ax4.set_ylabel('Retorno (%)')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# === RESUMO EXECUTIVO ===
print("\n" + "=" * 60)
print("🎯 RESUMO EXECUTIVO - ESTRATÉGIAS DE TRADING")
print("=" * 60)

print(f"""
💰 QUANDO COMPRAR:
   ✅ RSI < 30 (sobrevenda) + volume alto
   ✅ MACD cruzando linha de sinal para cima
   ✅ Preço tocando banda inferior de Bollinger
   ✅ Preço próximo a suportes identificados
   ✅ Pelo menos 2 indicadores concordando + volume confirmando

📉 QUANDO VENDER:
   ✅ RSI > 70 (sobrecompra) + volume alto
   ✅ MACD cruzando linha de sinal para baixo
   ✅ Preço tocando banda superior de Bollinger
   ✅ Preço próximo a resistências identificadas
   ✅ Pelo menos 2 indicadores concordando + volume confirmando

🐋 BIG PLAYERS:
   • Volume {big_players['volume'].mean() / dados['volume'].median():.1f}x acima da média indica atuação
   • {(big_players['direcao'] == 'ALTA').sum() / len(big_players) * 100:.0f}% das vezes direcionam para alta
   • Impacto médio: {big_players['impacto_preco'].mean():.0f} pontos

📊 CARACTERÍSTICAS DO MERCADO:
   • Retorno médio diário: {retornos.mean()*100:.3f}%
   • Volatilidade: {retornos.std()*100:.2f}%
   • {dias_alta/len(retornos)*100:.0f}% dos dias são de alta
   • Distribuição {'normal' if abs(retornos.skew()) < 0.5 else 'assimétrica'}

🎯 RECOMENDAÇÃO GERAL:
   • Use combinação de indicadores (nunca apenas um)
   • Sempre confirme com volume
   • Respeite suportes e resistências
   • Monitore atuação de big players
   • Gerencie risco baseado na volatilidade de {retornos.std()*100:.1f}%
""")

print("✅ Análise completa de estratégias de trading finalizada!")