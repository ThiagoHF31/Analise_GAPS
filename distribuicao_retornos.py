# 📊 GRÁFICOS DE DISTRIBUIÇÃO DE RETORNOS - WIN$N
# Script específico para análise estatística dos retornos

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("📊 ANÁLISE DE DISTRIBUIÇÃO DE RETORNOS WIN$N")
print("=" * 60)

# Carregar dados
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

# Calcular retornos diários
dados['retorno'] = dados['fechamento'].pct_change()
retornos = dados['retorno'].dropna()

print(f"📅 Período: {dados['data'].min().strftime('%d/%m/%Y')} a {dados['data'].max().strftime('%d/%m/%Y')}")
print(f"📈 Total de retornos: {len(retornos):,}")

# === ESTATÍSTICAS DESCRITIVAS ===
print(f"\n📊 ESTATÍSTICAS DOS RETORNOS DIÁRIOS:")
print(f"   • Retorno médio: {retornos.mean()*100:.4f}%")
print(f"   • Mediana: {retornos.median()*100:.4f}%")
print(f"   • Desvio padrão: {retornos.std()*100:.4f}%")
print(f"   • Skewness: {retornos.skew():.4f}")
print(f"   • Kurtosis: {retornos.kurtosis():.4f}")
print(f"   • Maior ganho: {retornos.max()*100:.2f}%")
print(f"   • Maior perda: {retornos.min()*100:.2f}%")

# Classificação dos retornos
dias_alta = (retornos > 0).sum()
dias_baixa = (retornos < 0).sum()
dias_neutro = (retornos == 0).sum()

print(f"\n📊 DISTRIBUIÇÃO DOS MOVIMENTOS:")
print(f"   📈 Dias de alta: {dias_alta} ({dias_alta/len(retornos)*100:.1f}%)")
print(f"   📉 Dias de baixa: {dias_baixa} ({dias_baixa/len(retornos)*100:.1f}%)")
print(f"   ➡️  Dias neutros: {dias_neutro} ({dias_neutro/len(retornos)*100:.1f}%)")

# === GRÁFICO DE DISTRIBUIÇÃO DOS RETORNOS ===
print(f"\n📊 Gerando gráficos de distribuição...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('📊 ANÁLISE COMPLETA DA DISTRIBUIÇÃO DE RETORNOS WIN$N\n' + 
             f'Período: {dados["data"].min().strftime("%d/%m/%Y")} a {dados["data"].max().strftime("%d/%m/%Y")} | {len(retornos)} observações',
             fontsize=16, fontweight='bold', y=0.98)

# 1. Histograma dos retornos com curva normal
ax1 = axes[0, 0]
n, bins, patches = ax1.hist(retornos * 100, bins=50, density=True, alpha=0.7, 
                           color='skyblue', edgecolor='black', label='Distribuição Real')

# Curva normal teórica sobreposta (implementação manual)
mu, sigma = retornos.mean() * 100, retornos.std() * 100
x = np.linspace(retornos.min() * 100, retornos.max() * 100, 100)

# Função normal manual
def normal_pdf(x, mu, sigma):
    return (1/(sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

normal_curve = normal_pdf(x, mu, sigma)
ax1.plot(x, normal_curve, 'r-', linewidth=3, label=f'Normal Teórica (μ={mu:.3f}%, σ={sigma:.3f}%)')

# Linhas de referência
ax1.axvline(mu, color='red', linestyle='--', linewidth=2, alpha=0.8, label=f'Média: {mu:.3f}%')
ax1.axvline(retornos.median() * 100, color='green', linestyle='--', linewidth=2, alpha=0.8, 
           label=f'Mediana: {retornos.median()*100:.3f}%')

# Zonas de percentis
p5 = np.percentile(retornos * 100, 5)
p95 = np.percentile(retornos * 100, 95)
ax1.axvspan(p5, p95, alpha=0.2, color='yellow', label=f'90% dos dados ({p5:.1f}% a {p95:.1f}%)')

ax1.set_title('📊 Histograma - Distribuição dos Retornos Diários')
ax1.set_xlabel('Retorno (%)')
ax1.set_ylabel('Densidade de Probabilidade')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

# 2. Q-Q Plot para normalidade (implementação manual)
ax2 = axes[0, 1]
sorted_returns = np.sort(retornos * 100)
n = len(sorted_returns)

# Quantis teóricos normais (implementação manual)
percentiles = np.linspace(1, 99, n)
# Aproximação da função inversa normal usando transformação Box-Muller simplificada
def norm_ppf_approx(p):
    # Aproximação para quantis normais
    return np.sqrt(2) * np.array([np.sign(x - 0.5) * np.sqrt(-2 * np.log(min(abs(x - 0.5), 0.499))) 
                                 for x in p/100])

theoretical_quantiles = norm_ppf_approx(percentiles)
empirical_quantiles = sorted_returns

ax2.scatter(theoretical_quantiles, empirical_quantiles, alpha=0.6, color='blue', s=20)

# Linha de referência (ideal)
min_val = min(min(theoretical_quantiles), min(empirical_quantiles))
max_val = max(max(theoretical_quantiles), max(empirical_quantiles))
ax2.plot([min_val, max_val], [min_val, max_val], 'r-', linewidth=2, label='Linha Ideal (Normal)')

# Ajuste linear dos dados
coef = np.polyfit(theoretical_quantiles, empirical_quantiles, 1)
line_fit = np.poly1d(coef)
ax2.plot(theoretical_quantiles, line_fit(theoretical_quantiles), 'g--', linewidth=2, 
         label=f'Ajuste Linear (R²={np.corrcoef(theoretical_quantiles, empirical_quantiles)[0,1]**2:.3f})')

ax2.set_title('📈 Q-Q Plot - Teste de Normalidade')
ax2.set_xlabel('Quantis Teóricos (Normal)')
ax2.set_ylabel('Quantis Empíricos (Dados)')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. Box Plot dos retornos
ax3 = axes[1, 0]
box_plot = ax3.boxplot(retornos * 100, vert=True, patch_artist=True, 
                       boxprops=dict(facecolor='lightblue', alpha=0.7),
                       medianprops=dict(color='red', linewidth=2),
                       flierprops=dict(marker='o', markerfacecolor='red', markersize=4, alpha=0.6))

# Estatísticas do box plot
q1 = np.percentile(retornos * 100, 25)
q3 = np.percentile(retornos * 100, 75)
iqr = q3 - q1
median = np.median(retornos * 100)

# Adicionar labels informativos
ax3.text(1.2, q1, f'Q1: {q1:.2f}%', fontsize=10, va='center')
ax3.text(1.2, median, f'Mediana: {median:.3f}%', fontsize=10, va='center', fontweight='bold')
ax3.text(1.2, q3, f'Q3: {q3:.2f}%', fontsize=10, va='center')
ax3.text(1.2, q3 + iqr/2, f'IQR: {iqr:.2f}%', fontsize=10, va='center')

# Outliers count
outliers = retornos * 100
outliers_count = len(outliers[(outliers < q1 - 1.5*iqr) | (outliers > q3 + 1.5*iqr)])
ax3.text(1.2, retornos.max()*100, f'Outliers: {outliers_count}', fontsize=10, va='center', color='red')

ax3.set_title('📦 Box Plot - Identificação de Outliers e Quartis')
ax3.set_ylabel('Retorno (%)')
ax3.set_xticklabels(['Retornos WIN$N'])
ax3.grid(True, alpha=0.3)

# 4. Retornos ao longo do tempo com padrões
ax4 = axes[1, 1]
dados_retornos = dados[dados['retorno'].notna()].copy()

# Plotar série temporal
ax4.plot(dados_retornos['data'], dados_retornos['retorno'] * 100, 
         alpha=0.7, color='purple', linewidth=1, label='Retornos Diários')

# Adicionar linha zero
ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)

# Destacar retornos extremos
retornos_extremos_pos = dados_retornos[dados_retornos['retorno'] > 0.04]  # >4%
retornos_extremos_neg = dados_retornos[dados_retornos['retorno'] < -0.04]  # <-4%

if not retornos_extremos_pos.empty:
    ax4.scatter(retornos_extremos_pos['data'], retornos_extremos_pos['retorno'] * 100, 
               color='green', s=30, alpha=0.8, label=f'Ganhos >4% ({len(retornos_extremos_pos)})', zorder=5)

if not retornos_extremos_neg.empty:
    ax4.scatter(retornos_extremos_neg['data'], retornos_extremos_neg['retorno'] * 100, 
               color='red', s=30, alpha=0.8, label=f'Perdas >4% ({len(retornos_extremos_neg)})', zorder=5)

# Bandas de volatilidade (±1 desvio padrão)
volatilidade = retornos.std() * 100
ax4.axhspan(-volatilidade, volatilidade, alpha=0.1, color='gray', label=f'±1σ ({volatilidade:.2f}%)')

# Rolling volatility (30 dias)
rolling_vol = dados_retornos['retorno'].rolling(30).std() * 100
ax4.plot(dados_retornos['data'], rolling_vol, color='orange', alpha=0.7, linewidth=2, 
         label='Volatilidade 30d')
ax4.plot(dados_retornos['data'], -rolling_vol, color='orange', alpha=0.7, linewidth=2)

ax4.set_title('📈 Evolução Temporal dos Retornos e Volatilidade')
ax4.set_xlabel('Data')
ax4.set_ylabel('Retorno (%)')
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3)

# Rotacionar labels do eixo x
for ax in [ax4]:
    for label in ax.get_xticklabels():
        label.set_rotation(45)

plt.tight_layout()

# Salvar gráfico
plt.savefig('output/graphs/trading/05_distribuicao_retornos_completa.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

print("✅ Gráfico salvo: output/graphs/trading/05_distribuicao_retornos_completa.png")

# === ANÁLISE ADICIONAL DE RISCO ===
print(f"\n📊 ANÁLISE DE RISCO:")

# Value at Risk (VaR) histórico
var_95 = np.percentile(retornos * 100, 5)
var_99 = np.percentile(retornos * 100, 1)

print(f"   📉 VaR 95%: {var_95:.2f}% (perda máxima em 95% dos casos)")
print(f"   📉 VaR 99%: {var_99:.2f}% (perda máxima em 99% dos casos)")

# Conditional VaR (Expected Shortfall)
cvar_95 = retornos[retornos <= np.percentile(retornos, 5)].mean() * 100
cvar_99 = retornos[retornos <= np.percentile(retornos, 1)].mean() * 100

print(f"   📉 CVaR 95%: {cvar_95:.2f}% (perda média quando VaR é excedido)")
print(f"   📉 CVaR 99%: {cvar_99:.2f}% (perda média em cenários extremos)")

# Sharpe Ratio (assumindo taxa livre de risco = 0)
sharpe_ratio = retornos.mean() / retornos.std() * np.sqrt(252)  # Anualizado

print(f"   📊 Sharpe Ratio: {sharpe_ratio:.3f} (retorno ajustado ao risco)")

# Maximum Drawdown
precos_acumulados = (1 + dados_retornos['retorno']).cumprod()
peak = precos_acumulados.cummax()
drawdown = (precos_acumulados - peak) / peak
max_drawdown = drawdown.min() * 100

print(f"   📉 Drawdown Máximo: {max_drawdown:.2f}% (maior queda desde o pico)")

# Dias consecutivos de alta/baixa
dados_retornos['sinal'] = np.where(dados_retornos['retorno'] > 0, 1, 
                                  np.where(dados_retornos['retorno'] < 0, -1, 0))

# Função para calcular sequências
def max_consecutive(series, value):
    """Calcula a máxima sequência consecutiva de um valor"""
    max_seq = 0
    current_seq = 0
    
    for val in series:
        if val == value:
            current_seq += 1
            max_seq = max(max_seq, current_seq)
        else:
            current_seq = 0
    
    return max_seq

max_alta_consecutiva = max_consecutive(dados_retornos['sinal'], 1)
max_baixa_consecutiva = max_consecutive(dados_retornos['sinal'], -1)

print(f"   📈 Máxima sequência de alta: {max_alta_consecutiva} dias")
print(f"   📉 Máxima sequência de baixa: {max_baixa_consecutiva} dias")

# Resumo final
print(f"\n🎯 RESUMO DA DISTRIBUIÇÃO:")
if abs(retornos.skew()) < 0.5:
    assimetria = "aproximadamente simétrica"
elif retornos.skew() > 0:
    assimetria = "assimétrica positiva (cauda à direita)"
else:
    assimetria = "assimétrica negativa (cauda à esquerda)"

if retornos.kurtosis() > 3:
    curtose = "leptocúrtica (caudas pesadas)"
elif retornos.kurtosis() < 3:
    curtose = "platicúrtica (caudas leves)"
else:
    curtose = "mesocúrtica (normal)"

print(f"   📊 Distribuição: {assimetria}")
print(f"   📊 Curtose: {curtose}")
print(f"   📊 Volatilidade anualizada: {retornos.std() * np.sqrt(252) * 100:.1f}%")
print(f"   📊 Retorno anualizado: {retornos.mean() * 252 * 100:.1f}%")

print(f"\n✅ ANÁLISE COMPLETA DE DISTRIBUIÇÃO FINALIZADA!")
print(f"📁 Gráfico salvo em: output/graphs/trading/05_distribuicao_retornos_completa.png")