"""
EXEMPLOS DE USO - WIN$N Financial Analyzer
Como usar os dados gerados e personalizar análises
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ============================================================================
# 1. CARREGANDO OS DADOS PROCESSADOS
# ============================================================================

def carregar_dados_limpos():
    """Carrega o dataset final limpo"""
    dados = pd.read_csv('data/processed/dados_limpos_finais.csv', 
                       index_col=0, parse_dates=True)
    print(f"✅ {len(dados)} dias de dados carregados")
    return dados

def carregar_analise_gaps():
    """Carrega a análise completa dos gaps"""
    gaps = pd.read_csv('data/processed/gaps_analisados.csv',
                      index_col=0, parse_dates=True)
    print(f"✅ {len(gaps)} gaps analisados carregados")
    return gaps

# ============================================================================
# 2. ANÁLISES BÁSICAS COM OS DADOS
# ============================================================================

def analise_retornos_basica(dados):
    """Análise básica de retornos"""
    print("📊 ANÁLISE DE RETORNOS:")
    print(f"   • Retorno médio: {dados['retorno_diario'].mean()*100:.3f}%")
    print(f"   • Volatilidade: {dados['retorno_diario'].std()*100:.2f}%")
    print(f"   • Sharpe Ratio: {dados['retorno_diario'].mean()/dados['retorno_diario'].std()*np.sqrt(252):.3f}")
    print(f"   • Melhor dia: {dados['retorno_diario'].max()*100:.2f}%")
    print(f"   • Pior dia: {dados['retorno_diario'].min()*100:.2f}%")

def analise_volatilidade(dados):
    """Análise de volatilidade realizada"""
    print("\n📊 ANÁLISE DE VOLATILIDADE:")
    vol_media = dados['volatilidade'].mean()
    vol_alta = dados['volatilidade'].quantile(0.9)
    
    print(f"   • Volatilidade média: {vol_media:.2f}%")
    print(f"   • 90º percentil: {vol_alta:.2f}%")
    
    # Dias de alta volatilidade
    dias_alta_vol = dados[dados['volatilidade'] > vol_alta]
    print(f"   • Dias alta volatilidade: {len(dias_alta_vol)} ({len(dias_alta_vol)/len(dados)*100:.1f}%)")

# ============================================================================
# 3. ANÁLISES ESPECÍFICAS DE GAPS
# ============================================================================

def analise_gaps_por_tamanho(gaps):
    """Analisa gaps por faixas de tamanho"""
    print("\n📈 GAPS POR FAIXA DE TAMANHO:")
    
    faixas = [
        (100, 200, "100-200 pts"),
        (200, 500, "200-500 pts"), 
        (500, 1000, "500-1000 pts"),
        (1000, float('inf'), ">1000 pts")
    ]
    
    for min_gap, max_gap, label in faixas:
        subset = gaps[
            (gaps['gap_absoluto'] >= min_gap) & 
            (gaps['gap_absoluto'] < max_gap)
        ]
        
        if len(subset) > 0:
            taxa_fechamento = subset['gap_fechado'].mean() * 100
            tempo_medio = subset[subset['gap_fechado']]['dias_para_fechamento'].mean()
            
            print(f"   • {label}: {len(subset)} gaps, {taxa_fechamento:.1f}% fechados, {tempo_medio:.1f} dias médios")

def gaps_por_mes(gaps):
    """Analisa sazonalidade dos gaps por mês"""
    print("\n📅 GAPS POR MÊS:")
    
    gaps['mes'] = gaps.index.month
    gaps_por_mes = gaps.groupby('mes').agg({
        'gap_absoluto': ['count', 'mean'],
        'gap_fechado': 'mean'
    })
    
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    for mes_num in range(1, 13):
        if mes_num in gaps_por_mes.index:
            dados_mes = gaps_por_mes.loc[mes_num]
            count = dados_mes[('gap_absoluto', 'count')]
            media = dados_mes[('gap_absoluto', 'mean')]
            taxa = dados_mes[('gap_fechado', 'mean')] * 100
            
            print(f"   • {meses[mes_num-1]}: {count} gaps, média {media:.0f} pts, {taxa:.1f}% fechados")

# ============================================================================
# 4. ESTRATÉGIAS DE TRADING BASEADAS EM GAPS
# ============================================================================

def simular_estrategia_reversao_gaps(dados, gaps):
    """Simula estratégia simples de reversão em gaps"""
    print("\n💰 SIMULAÇÃO: ESTRATÉGIA DE REVERSÃO EM GAPS")
    
    # Parâmetros da estratégia
    gap_minimo = 200  # Operar apenas gaps > 200 pontos
    stop_loss = 0.02  # Stop loss de 2%
    take_profit = 0.01  # Take profit de 1%
    
    trades = []
    
    # Filtrar gaps para trading
    gaps_trading = gaps[
        (gaps['gap_absoluto'] >= gap_minimo) & 
        (gaps['gap_fechado'] == True)
    ]
    
    print(f"   • Gaps elegíveis: {len(gaps_trading)}")
    
    for idx, gap in gaps_trading.head(50).iterrows():  # Primeiros 50 para exemplo
        # Entrada no trade (reversão do gap)
        preco_entrada = gap['abertura']
        
        if gap['gap_abertura'] > 0:  # Gap Up - vender
            direcao = 'SELL'
            take_profit_price = preco_entrada * (1 - take_profit)
            stop_loss_price = preco_entrada * (1 + stop_loss)
        else:  # Gap Down - comprar
            direcao = 'BUY'  
            take_profit_price = preco_entrada * (1 + take_profit)
            stop_loss_price = preco_entrada * (1 - stop_loss)
        
        # Verificar dados futuros
        dados_futuros = dados[dados.index > idx][:5]  # Próximos 5 dias
        
        if len(dados_futuros) == 0:
            continue
            
        # Simular resultado
        for _, dia in dados_futuros.iterrows():
            if direcao == 'SELL':
                if dia['minima'] <= take_profit_price:
                    resultado = 'WIN'
                    break
                elif dia['maxima'] >= stop_loss_price:
                    resultado = 'LOSS'
                    break
            else:  # BUY
                if dia['maxima'] >= take_profit_price:
                    resultado = 'WIN'
                    break
                elif dia['minima'] <= stop_loss_price:
                    resultado = 'LOSS'
                    break
        else:
            resultado = 'NEUTRO'
        
        trades.append({
            'data': idx,
            'gap_size': gap['gap_absoluto'],
            'direcao': direcao,
            'resultado': resultado
        })
    
    # Análise dos trades
    df_trades = pd.DataFrame(trades)
    
    if len(df_trades) > 0:
        wins = (df_trades['resultado'] == 'WIN').sum()
        losses = (df_trades['resultado'] == 'LOSS').sum()
        neutros = (df_trades['resultado'] == 'NEUTRO').sum()
        
        taxa_acerto = wins / len(df_trades) * 100
        
        print(f"   • Total de trades: {len(df_trades)}")
        print(f"   • Wins: {wins} ({wins/len(df_trades)*100:.1f}%)")
        print(f"   • Losses: {losses} ({losses/len(df_trades)*100:.1f}%)")
        print(f"   • Neutros: {neutros} ({neutros/len(df_trades)*100:.1f}%)")
        print(f"   • Taxa de acerto: {taxa_acerto:.1f}%")

# ============================================================================
# 5. GRÁFICOS CUSTOMIZADOS
# ============================================================================

def grafico_gaps_timeline(gaps):
    """Gráfico timeline dos gaps"""
    plt.figure(figsize=(15, 8))
    
    # Separar por tipo
    gap_up = gaps[gaps['tipo_gap'] == 'Gap Up']
    gap_down = gaps[gaps['tipo_gap'] == 'Gap Down']
    
    # Plot
    plt.scatter(gap_up.index, gap_up['gap_absoluto'], 
               c='red', alpha=0.6, s=30, label='Gap Up')
    plt.scatter(gap_down.index, gap_down['gap_absoluto'], 
               c='blue', alpha=0.6, s=30, label='Gap Down')
    
    plt.title('Timeline de Gaps WIN$N', fontsize=14, fontweight='bold')
    plt.xlabel('Data')
    plt.ylabel('Tamanho do Gap (pontos)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('output/graphs/timeline_gaps.png', dpi=300)
    plt.show()
    
    print("✅ Gráfico salvo: output/graphs/timeline_gaps.png")

def grafico_distribuicao_retornos(dados):
    """Gráfico de distribuição de retornos"""
    plt.figure(figsize=(12, 6))
    
    retornos = dados['retorno_diario'] * 100
    
    plt.hist(retornos, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
    plt.axvline(retornos.mean(), color='red', linestyle='--', 
               label=f'Média: {retornos.mean():.3f}%')
    plt.axvline(retornos.mean() - retornos.std(), color='orange', linestyle='--', alpha=0.7)
    plt.axvline(retornos.mean() + retornos.std(), color='orange', linestyle='--', alpha=0.7)
    
    plt.title('Distribuição de Retornos Diários', fontsize=14, fontweight='bold')
    plt.xlabel('Retorno (%)')
    plt.ylabel('Frequência')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output/graphs/distribuicao_retornos.png', dpi=300)
    plt.show()
    
    print("✅ Gráfico salvo: output/graphs/distribuicao_retornos.png")

# ============================================================================
# 6. EXEMPLO DE USO COMPLETO
# ============================================================================

def main():
    """Exemplo de uso completo do sistema"""
    print("🚀 EXEMPLOS DE USO - WIN$N ANALYZER")
    print("=" * 50)
    
    # Carregar dados
    dados = carregar_dados_limpos()
    gaps = carregar_analise_gaps()
    
    # Análises básicas
    analise_retornos_basica(dados)
    analise_volatilidade(dados)
    
    # Análises de gaps
    analise_gaps_por_tamanho(gaps)
    gaps_por_mes(gaps)
    
    # Estratégia de trading
    simular_estrategia_reversao_gaps(dados, gaps)
    
    # Gráficos customizados
    grafico_gaps_timeline(gaps)
    grafico_distribuicao_retornos(dados)
    
    print("\n🎯 Exemplos concluídos! Verifique os gráficos gerados.")

if __name__ == "__main__":
    main()