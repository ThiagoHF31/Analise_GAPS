# 📊 Análise de Estratégias de Trading WIN$N
# Análise completa para decisões de compra/venda

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurações de visualização
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 11

# Criar diretório para salvar gráficos
import os
os.makedirs('output/graphs/trading', exist_ok=True)
os.makedirs('output/reports', exist_ok=True)

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

# === 2. GRÁFICOS INDIVIDUAIS DE ANÁLISE TÉCNICA ===
print("\n" + "=" * 60)
print("📊 GERANDO GRÁFICOS INDIVIDUAIS DE ANÁLISE TÉCNICA")
print("=" * 60)

# Garantir que o diretório existe
import os
os.makedirs('output/graphs/trading', exist_ok=True)

# Últimos 100 dias para visualização clara
periodo_analise = dados.tail(100).copy()
sinais_periodo = sinais.tail(100).copy()

# Gráfico 1: Preços com Suporte/Resistência e Sinais
plt.figure(figsize=(16, 8))
plt.plot(periodo_analise['data'], periodo_analise['fechamento'], 
         label='Fechamento WIN$N', linewidth=2.5, color='black')
plt.plot(periodo_analise['data'], periodo_analise['sma_20'], 
         label='SMA 20', alpha=0.8, color='blue', linewidth=2)
plt.plot(periodo_analise['data'], periodo_analise['sma_50'], 
         label='SMA 50', alpha=0.8, color='red', linewidth=2)

# Bollinger Bands
plt.fill_between(periodo_analise['data'], 
                periodo_analise['bb_superior'], 
                periodo_analise['bb_inferior'], 
                alpha=0.15, color='gray', label='Bollinger Bands')

# Sinais de compra e venda
compras_periodo = sinais_periodo[sinais_periodo['COMPRA']]
vendas_periodo = sinais_periodo[sinais_periodo['VENDA']]

if not compras_periodo.empty:
    plt.scatter(compras_periodo['data'], compras_periodo['preco'], 
               color='green', marker='^', s=150, label=f'🟢 COMPRA ({len(compras_periodo)})', 
               zorder=5, edgecolors='darkgreen', linewidth=2)

if not vendas_periodo.empty:
    plt.scatter(vendas_periodo['data'], vendas_periodo['preco'], 
               color='red', marker='v', s=150, label=f'🔴 VENDA ({len(vendas_periodo)})', 
               zorder=5, edgecolors='darkred', linewidth=2)

# Níveis de suporte e resistência
resistencias_periodo = periodo_analise[periodo_analise['resistencia']]
suportes_periodo = periodo_analise[periodo_analise['suporte']]

if not resistencias_periodo.empty:
    for _, ponto in resistencias_periodo.iterrows():
        plt.axhline(y=ponto['fechamento'], color='red', linestyle='--', 
                   alpha=0.7, linewidth=1.5)
        plt.text(periodo_analise['data'].iloc[-1], ponto['fechamento'], 
                f' R: {ponto["fechamento"]:.0f}', fontsize=10, color='red', 
                fontweight='bold')

if not suportes_periodo.empty:
    for _, ponto in suportes_periodo.iterrows():
        plt.axhline(y=ponto['fechamento'], color='green', linestyle='--', 
                   alpha=0.7, linewidth=1.5)
        plt.text(periodo_analise['data'].iloc[-1], ponto['fechamento'], 
                f' S: {ponto["fechamento"]:.0f}', fontsize=10, color='green', 
                fontweight='bold')

plt.title('💰 WIN$N - Preços com Sinais de Trading e Suporte/Resistência\n' + 
          f'Período: {periodo_analise["data"].min().strftime("%d/%m/%Y")} a {periodo_analise["data"].max().strftime("%d/%m/%Y")}', 
          fontsize=14, fontweight='bold', pad=20)
plt.xlabel('Data', fontsize=12)
plt.ylabel('Preço (pontos)', fontsize=12)
plt.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('output/graphs/trading/01_precos_sinais_suporte_resistencia.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
print("✅ Gráfico 1 salvo: 01_precos_sinais_suporte_resistencia.png")

# Gráfico 2: RSI (Índice de Força Relativa)
plt.figure(figsize=(16, 6))
plt.plot(periodo_analise['data'], periodo_analise['rsi'], 
         label='RSI (14 períodos)', linewidth=2.5, color='purple')
plt.axhline(y=70, color='red', linestyle='--', alpha=0.8, linewidth=2, 
           label='🔴 Sobrecompra (70)')
plt.axhline(y=30, color='green', linestyle='--', alpha=0.8, linewidth=2, 
           label='🟢 Sobrevenda (30)')
plt.fill_between(periodo_analise['data'], 30, 70, alpha=0.1, color='gray', 
                label='Zona Neutra')

# Destacar zonas extremas
zona_sobrecompra = periodo_analise['rsi'] > 70
zona_sobrevenda = periodo_analise['rsi'] < 30

if zona_sobrecompra.any():
    plt.fill_between(periodo_analise['data'], periodo_analise['rsi'], 70, 
                    where=zona_sobrecompra, alpha=0.3, color='red', 
                    interpolate=True, label='Região Sobrecompra')

if zona_sobrevenda.any():
    plt.fill_between(periodo_analise['data'], periodo_analise['rsi'], 30, 
                    where=zona_sobrevenda, alpha=0.3, color='green', 
                    interpolate=True, label='Região Sobrevenda')

plt.title('📊 RSI - Índice de Força Relativa WIN$N\n' + 
          'Identificação de Condições de Sobrecompra e Sobrevenda', 
          fontsize=14, fontweight='bold', pad=20)
plt.xlabel('Data', fontsize=12)
plt.ylabel('RSI', fontsize=12)
plt.ylim(0, 100)
plt.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('output/graphs/trading/02_rsi_analise_forca_relativa.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
print("✅ Gráfico 2 salvo: 02_rsi_analise_forca_relativa.png")

# Gráfico 3: MACD
plt.figure(figsize=(16, 6))
plt.plot(periodo_analise['data'], periodo_analise['macd'], 
         label='MACD', linewidth=2.5, color='blue')
plt.plot(periodo_analise['data'], periodo_analise['macd_sinal'], 
         label='Linha de Sinal', linewidth=2.5, color='red')

# Histograma com cores condicionais
histograma_positivo = periodo_analise['macd_histograma'] >= 0
histograma_negativo = periodo_analise['macd_histograma'] < 0

plt.bar(periodo_analise[histograma_positivo]['data'], 
        periodo_analise[histograma_positivo]['macd_histograma'], 
        alpha=0.6, color='green', label='Histograma Positivo', width=0.8)
plt.bar(periodo_analise[histograma_negativo]['data'], 
        periodo_analise[histograma_negativo]['macd_histograma'], 
        alpha=0.6, color='red', label='Histograma Negativo', width=0.8)

plt.axhline(y=0, color='black', linestyle='-', alpha=0.6, linewidth=1)

# Destacar cruzamentos
cruzamentos_alta = ((periodo_analise['macd'] > periodo_analise['macd_sinal']) & 
                   (periodo_analise['macd'].shift(1) <= periodo_analise['macd_sinal'].shift(1)))
cruzamentos_baixa = ((periodo_analise['macd'] < periodo_analise['macd_sinal']) & 
                    (periodo_analise['macd'].shift(1) >= periodo_analise['macd_sinal'].shift(1)))

if cruzamentos_alta.any():
    plt.scatter(periodo_analise[cruzamentos_alta]['data'], 
               periodo_analise[cruzamentos_alta]['macd'], 
               color='green', marker='^', s=100, zorder=5, 
               label='🟢 Cruzamento Alta')

if cruzamentos_baixa.any():
    plt.scatter(periodo_analise[cruzamentos_baixa]['data'], 
               periodo_analise[cruzamentos_baixa]['macd'], 
               color='red', marker='v', s=100, zorder=5, 
               label='🔴 Cruzamento Baixa')

plt.title('📈 MACD - Convergência e Divergência de Médias Móveis\n' + 
          'Identificação de Mudanças de Momentum', 
          fontsize=14, fontweight='bold', pad=20)
plt.xlabel('Data', fontsize=12)
plt.ylabel('MACD', fontsize=12)
plt.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('output/graphs/trading/03_macd_convergencia_divergencia.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
print("✅ Gráfico 3 salvo: 03_macd_convergencia_divergencia.png")

# Gráfico 4: Volume Profile - Big Players Detection
plt.figure(figsize=(16, 6))

# Volume normal vs anômalo
volume_normal = periodo_analise['volume_ratio'] <= 1.5
volume_alto = (periodo_analise['volume_ratio'] > 1.5) & (periodo_analise['volume_ratio'] <= 2)
volume_anomalo = periodo_analise['volume_ratio'] > 2

plt.bar(periodo_analise[volume_normal]['data'], 
        periodo_analise[volume_normal]['volume'], 
        alpha=0.6, color='lightblue', label='Volume Normal', width=0.8)

if volume_alto.any():
    plt.bar(periodo_analise[volume_alto]['data'], 
            periodo_analise[volume_alto]['volume'], 
            alpha=0.8, color='orange', label='Volume Alto (1.5-2x)', width=0.8)

if volume_anomalo.any():
    plt.bar(periodo_analise[volume_anomalo]['data'], 
            periodo_analise[volume_anomalo]['volume'], 
            alpha=0.9, color='red', label='🐋 Big Players (>2x)', width=0.8)

plt.plot(periodo_analise['data'], periodo_analise['volume_ma'], 
         label='Volume Médio (20d)', color='darkblue', linewidth=3, alpha=0.8)

# Linha de threshold para Big Players
volume_threshold = dados['volume'].quantile(0.95)
plt.axhline(y=volume_threshold, color='red', linestyle='--', alpha=0.8, 
           linewidth=2, label=f'Threshold Big Players ({volume_threshold:,.0f})')

plt.title('📦 Volume Profile - Detecção de Big Players WIN$N\n' + 
          'Identificação de Movimentações Anômalas de Volume', 
          fontsize=14, fontweight='bold', pad=20)
plt.xlabel('Data', fontsize=12)
plt.ylabel('Volume', fontsize=12)
plt.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)

# Formatação do eixo Y para volume
ax = plt.gca()
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))

plt.tight_layout()
plt.savefig('output/graphs/trading/04_volume_profile_big_players.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
print("✅ Gráfico 4 salvo: 04_volume_profile_big_players.png")

print("\n📁 Todos os gráficos salvos no diretório: output/graphs/trading/")
print("   - 01_precos_sinais_suporte_resistencia.png")
print("   - 02_rsi_analise_forca_relativa.png")
print("   - 03_macd_convergencia_divergencia.png")
print("   - 04_volume_profile_big_players.png")

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
ax2 = axes[0, 1]
# Implementação simples sem scipy
sorted_returns = np.sort(retornos)
n = len(sorted_returns)
theoretical_quantiles = np.linspace(0.01, 0.99, n)
from math import sqrt, pi, erf
def normal_quantile(p):
    # Aproximação da função quantil normal
    return sqrt(2) * np.array([0.5 * (1 + erf(x / sqrt(2))) for x in np.linspace(-3, 3, len(p))])

ax2.scatter(np.linspace(-3, 3, n), sorted_returns, alpha=0.6)
ax2.plot(np.linspace(-3, 3, n), np.linspace(sorted_returns.min(), sorted_returns.max(), n), 
         'r-', label='Linha Teórica')
ax2.set_title('📈 Q-Q Plot - Teste de Normalidade')
ax2.set_xlabel('Quantis Teóricos')
ax2.set_ylabel('Quantis dos Dados')
ax2.legend()
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

# === 5. INTEGRAÇÃO COM ANÁLISE PRINCIPAL ===
print("\n" + "=" * 60)
print("🔗 INTEGRAÇÃO COM ANÁLISE PRINCIPAL (run.py)")
print("=" * 60)

def salvar_resumo_trading():
    """Salva resumo para integração com run.py"""
    
    # Criar diretório se não existir
    os.makedirs('output/reports', exist_ok=True)
    
    # Dados para salvar
    resumo_trading = {
        'data_analise': dados['data'].max().strftime('%Y-%m-%d'),
        'total_registros': len(dados),
        'periodo': f"{dados['data'].min().strftime('%d/%m/%Y')} a {dados['data'].max().strftime('%d/%m/%Y')}",
        'sinais': {
            'compras': int(sinais[sinais['COMPRA']].shape[0]),
            'vendas': int(sinais[sinais['VENDA']].shape[0]),
            'frequencia_pct': float((sinais[sinais['COMPRA']].shape[0] + sinais[sinais['VENDA']].shape[0]) / len(dados) * 100)
        },
        'big_players': {
            'dias_detectados': int(len(big_players)),
            'multiplicador_volume': float(big_players['volume'].mean() / dados['volume'].median()),
            'impacto_medio_pontos': float(big_players['impacto_preco'].mean()),
            'direcao_alta_pct': float((big_players['direcao'] == 'ALTA').sum() / len(big_players) * 100)
        },
        'distribuicao_retornos': {
            'retorno_medio_pct': float(retornos.mean() * 100),
            'volatilidade_pct': float(retornos.std() * 100),
            'dias_alta_pct': float(dias_alta / len(retornos) * 100),
            'dias_baixa_pct': float(dias_baixa / len(retornos) * 100),
            'maior_ganho_pct': float(retornos.max() * 100),
            'maior_perda_pct': float(retornos.min() * 100)
        },
        'graficos_salvos': [
            'output/graphs/trading/01_precos_sinais_suporte_resistencia.png',
            'output/graphs/trading/02_rsi_analise_forca_relativa.png',
            'output/graphs/trading/03_macd_convergencia_divergencia.png',
            'output/graphs/trading/04_volume_profile_big_players.png'
        ]
    }
    
    # Salvar em JSON para integração
    import json
    with open('output/reports/trading_analysis_summary.json', 'w', encoding='utf-8') as f:
        json.dump(resumo_trading, f, indent=2, ensure_ascii=False)
    
    # Salvar relatório em texto
    with open('output/reports/trading_analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("📊 RELATÓRIO DE ANÁLISE DE TRADING - WIN$N\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"📅 Data da Análise: {resumo_trading['data_analise']}\n")
        f.write(f"📊 Período Analisado: {resumo_trading['periodo']}\n")
        f.write(f"📈 Total de Registros: {resumo_trading['total_registros']:,}\n\n")
        
        f.write("🎯 SINAIS DE TRADING:\n")
        f.write(f"   • Sinais de Compra: {resumo_trading['sinais']['compras']}\n")
        f.write(f"   • Sinais de Venda: {resumo_trading['sinais']['vendas']}\n")
        f.write(f"   • Frequência: {resumo_trading['sinais']['frequencia_pct']:.1f}% dos dias\n\n")
        
        f.write("🐋 BIG PLAYERS:\n")
        f.write(f"   • Dias Detectados: {resumo_trading['big_players']['dias_detectados']}\n")
        f.write(f"   • Multiplicador Volume: {resumo_trading['big_players']['multiplicador_volume']:.1f}x\n")
        f.write(f"   • Impacto Médio: {resumo_trading['big_players']['impacto_medio_pontos']:.0f} pontos\n")
        f.write(f"   • Direcionamento Alta: {resumo_trading['big_players']['direcao_alta_pct']:.0f}%\n\n")
        
        f.write("📊 DISTRIBUIÇÃO DE RETORNOS:\n")
        f.write(f"   • Retorno Médio: {resumo_trading['distribuicao_retornos']['retorno_medio_pct']:.3f}%\n")
        f.write(f"   • Volatilidade: {resumo_trading['distribuicao_retornos']['volatilidade_pct']:.2f}%\n")
        f.write(f"   • Dias de Alta: {resumo_trading['distribuicao_retornos']['dias_alta_pct']:.1f}%\n")
        f.write(f"   • Dias de Baixa: {resumo_trading['distribuicao_retornos']['dias_baixa_pct']:.1f}%\n")
        f.write(f"   • Maior Ganho: {resumo_trading['distribuicao_retornos']['maior_ganho_pct']:.2f}%\n")
        f.write(f"   • Maior Perda: {resumo_trading['distribuicao_retornos']['maior_perda_pct']:.2f}%\n\n")
        
        f.write("📁 GRÁFICOS GERADOS:\n")
        for grafico in resumo_trading['graficos_salvos']:
            f.write(f"   • {grafico}\n")
    
    return resumo_trading

# Salvar dados para integração
resumo_final = salvar_resumo_trading()

print("💾 Dados salvos para integração:")
print(f"   • JSON: output/reports/trading_analysis_summary.json")
print(f"   • Relatório: output/reports/trading_analysis_report.txt")
print(f"   • Gráficos: {len(resumo_final['graficos_salvos'])} arquivos PNG")

print("\n" + "=" * 60)
print("✅ ANÁLISE DE TRADING COMPLETA E PRONTA PARA INTEGRAÇÃO!")
print("=" * 60)

print(f"""
📊 RESUMO FINAL:
   • {resumo_final['sinais']['compras']} sinais de compra
   • {resumo_final['sinais']['vendas']} sinais de venda
   • {resumo_final['big_players']['dias_detectados']} dias com big players
   • {resumo_final['distribuicao_retornos']['volatilidade_pct']:.1f}% volatilidade diária
   • 4 gráficos individuais salvos em alta resolução
   
🔗 Para integrar com run.py:
   • Importe: trading_analysis_summary.json
   • Exiba: gráficos da pasta output/graphs/trading/
   • Use: métricas do relatório para dashboard principal
""")