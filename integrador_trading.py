# 🔗 Integrador de Análise de Trading com run.py
# Este arquivo integra os resultados da análise de trading com o sistema principal

import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def carregar_dados_trading():
    """Carrega os dados da análise de trading"""
    try:
        with open('output/reports/trading_analysis_summary.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo de análise de trading não encontrado!")
        print("Execute primeiro: python analise_trading_estrategias.py")
        return None

def exibir_dashboard_trading():
    """Exibe dashboard integrado com análise de trading"""
    
    dados_trading = carregar_dados_trading()
    if not dados_trading:
        return
    
    print("\n" + "=" * 80)
    print("📊 DASHBOARD INTEGRADO - ANÁLISE DE TRADING WIN$N")
    print("=" * 80)
    
    # Informações gerais
    print(f"\n📅 PERÍODO ANALISADO: {dados_trading['periodo']}")
    print(f"📊 Total de Registros: {dados_trading['total_registros']:,}")
    print(f"📈 Data da Última Análise: {dados_trading['data_analise']}")
    
    # Seção de Sinais de Trading
    sinais = dados_trading['sinais']
    print(f"\n🎯 SINAIS DE TRADING:")
    print(f"   📈 Compras Identificadas: {sinais['compras']}")
    print(f"   📉 Vendas Identificadas: {sinais['vendas']}")
    print(f"   🎲 Frequência de Sinais: {sinais['frequencia_pct']:.1f}% dos dias")
    print(f"   ⚡ Total de Oportunidades: {sinais['compras'] + sinais['vendas']}")
    
    # Seção Big Players
    big_players = dados_trading['big_players']
    print(f"\n🐋 BIG PLAYERS DETECTION:")
    print(f"   📊 Dias com Atividade Anômala: {big_players['dias_detectados']}")
    print(f"   📈 Multiplicador de Volume: {big_players['multiplicador_volume']:.1f}x")
    print(f"   💥 Impacto Médio no Preço: {big_players['impacto_medio_pontos']:.0f} pontos")
    print(f"   📈 Direcionamento para Alta: {big_players['direcao_alta_pct']:.0f}%")
    
    # Seção Distribuição de Retornos
    retornos = dados_trading['distribuicao_retornos']
    print(f"\n📊 DISTRIBUIÇÃO DE RETORNOS:")
    print(f"   💰 Retorno Médio Diário: {retornos['retorno_medio_pct']:.3f}%")
    print(f"   📈 Volatilidade: {retornos['volatilidade_pct']:.2f}%")
    print(f"   🟢 Dias de Alta: {retornos['dias_alta_pct']:.1f}%")
    print(f"   🔴 Dias de Baixa: {retornos['dias_baixa_pct']:.1f}%")
    print(f"   🚀 Maior Ganho: {retornos['maior_ganho_pct']:.2f}%")
    print(f"   ⬇️  Maior Perda: {retornos['maior_perda_pct']:.2f}%")
    
    # Performance Score
    score_trading = calcular_score_trading(dados_trading)
    print(f"\n⭐ SCORE DE PERFORMANCE TRADING: {score_trading:.1f}/10")
    
    # Recomendações
    print(f"\n🎯 RECOMENDAÇÕES BASEADAS NA ANÁLISE:")
    gerar_recomendacoes(dados_trading)
    
    # Status dos gráficos
    print(f"\n📁 GRÁFICOS DISPONÍVEIS: {len(dados_trading['graficos_salvos'])} arquivos")
    for i, grafico in enumerate(dados_trading['graficos_salvos'], 1):
        nome_grafico = Path(grafico).name
        print(f"   {i}. {nome_grafico}")

def calcular_score_trading(dados):
    """Calcula score de performance da estratégia de trading"""
    
    score = 0
    
    # Frequência de sinais (0-2 pontos)
    freq = dados['sinais']['frequencia_pct']
    if freq >= 3:
        score += 2
    elif freq >= 1:
        score += 1
    
    # Retorno médio (0-2 pontos)
    retorno = dados['distribuicao_retornos']['retorno_medio_pct']
    if retorno > 0:
        score += 2
    elif retorno > -0.1:
        score += 1
    
    # Volatilidade (0-2 pontos - menor é melhor)
    volatilidade = dados['distribuicao_retornos']['volatilidade_pct']
    if volatilidade < 1.5:
        score += 2
    elif volatilidade < 2.5:
        score += 1
    
    # Balance de dias alta/baixa (0-2 pontos)
    dias_alta = dados['distribuicao_retornos']['dias_alta_pct']
    if 48 <= dias_alta <= 52:
        score += 2
    elif 45 <= dias_alta <= 55:
        score += 1
    
    # Big players direcionamento (0-2 pontos)
    big_players_alta = dados['big_players']['direcao_alta_pct']
    if 45 <= big_players_alta <= 55:
        score += 2
    elif 40 <= big_players_alta <= 60:
        score += 1
    
    return score

def gerar_recomendacoes(dados):
    """Gera recomendações baseadas nos dados de trading"""
    
    sinais = dados['sinais']
    retornos = dados['distribuicao_retornos']
    big_players = dados['big_players']
    
    recomendacoes = []
    
    # Análise de frequência
    if sinais['frequencia_pct'] < 2:
        recomendacoes.append("⚠️  Baixa frequência de sinais - considere ajustar sensibilidade dos indicadores")
    elif sinais['frequencia_pct'] > 10:
        recomendacoes.append("⚠️  Alta frequência de sinais - risco de overtrading")
    else:
        recomendacoes.append("✅ Frequência de sinais adequada para swing trading")
    
    # Análise de volatilidade
    if retornos['volatilidade_pct'] > 2:
        recomendacoes.append("⚠️  Alta volatilidade - use stops mais conservadores")
    elif retornos['volatilidade_pct'] < 1:
        recomendacoes.append("✅ Baixa volatilidade - ambiente favorável para trading")
    else:
        recomendacoes.append("✅ Volatilidade moderada - ideal para estratégias técnicas")
    
    # Análise big players
    if big_players['multiplicador_volume'] > 2:
        recomendacoes.append("🐋 Forte presença de big players - monitore volume antes de operar")
    else:
        recomendacoes.append("✅ Atividade de big players moderada")
    
    # Análise de retornos
    if retornos['retorno_medio_pct'] > 0.05:
        recomendacoes.append("🚀 Mercado com tendência de alta - favoreça posições compradas")
    elif retornos['retorno_medio_pct'] < -0.05:
        recomendacoes.append("📉 Mercado com tendência de baixa - favoreça posições vendidas")
    else:
        recomendacoes.append("⚖️  Mercado neutro - use estratégias bidirecionais")
    
    # Exibir recomendações
    for rec in recomendacoes:
        print(f"   {rec}")

def criar_dashboard_visual():
    """Cria dashboard visual integrando todos os gráficos"""
    
    dados_trading = carregar_dados_trading()
    if not dados_trading:
        return
    
    # Verificar se gráficos existem
    graficos_existentes = []
    for grafico in dados_trading['graficos_salvos']:
        if os.path.exists(grafico):
            graficos_existentes.append(grafico)
    
    if not graficos_existentes:
        print("❌ Nenhum gráfico encontrado!")
        return
    
    print(f"\n📊 Criando dashboard visual com {len(graficos_existentes)} gráficos...")
    
    # Criar figura com grid
    fig = plt.figure(figsize=(20, 24))
    gs = GridSpec(4, 2, figure=fig, hspace=0.3, wspace=0.2)
    
    # Título principal
    fig.suptitle('📊 DASHBOARD COMPLETO - ANÁLISE DE TRADING WIN$N\n' + 
                f'Período: {dados_trading["periodo"]} | {dados_trading["total_registros"]} registros',
                fontsize=20, fontweight='bold', y=0.98)
    
    # Adicionar métricas principais como texto
    ax_metrics = fig.add_subplot(gs[0, :])
    ax_metrics.axis('off')
    
    # Texto com métricas
    metrics_text = f"""
🎯 SINAIS: {dados_trading['sinais']['compras']} Compras | {dados_trading['sinais']['vendas']} Vendas | {dados_trading['sinais']['frequencia_pct']:.1f}% Frequência

🐋 BIG PLAYERS: {dados_trading['big_players']['dias_detectados']} dias detectados | {dados_trading['big_players']['multiplicador_volume']:.1f}x volume | {dados_trading['big_players']['impacto_medio_pontos']:.0f} pts impacto

📊 RETORNOS: {dados_trading['distribuicao_retornos']['retorno_medio_pct']:.3f}% médio | {dados_trading['distribuicao_retornos']['volatilidade_pct']:.2f}% volatilidade | {dados_trading['distribuicao_retornos']['dias_alta_pct']:.0f}% dias alta

⭐ SCORE TRADING: {calcular_score_trading(dados_trading):.1f}/10
    """
    
    ax_metrics.text(0.5, 0.5, metrics_text, fontsize=14, ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
    
    # Carregar e exibir cada gráfico individual
    for i, grafico in enumerate(graficos_existentes[:4]):  # Máximo 4 gráficos
        try:
            img = plt.imread(grafico)
            ax = fig.add_subplot(gs[i+1, 0] if i < 2 else gs[i-1, 1])
            ax.imshow(img)
            ax.axis('off')
            
            # Título baseado no nome do arquivo
            nome = Path(grafico).stem.replace('_', ' ').title()
            ax.set_title(nome, fontsize=12, fontweight='bold', pad=10)
            
        except Exception as e:
            print(f"❌ Erro ao carregar {grafico}: {e}")
    
    # Salvar dashboard
    os.makedirs('output/dashboards', exist_ok=True)
    dashboard_path = 'output/dashboards/dashboard_trading_completo.png'
    plt.savefig(dashboard_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    print(f"✅ Dashboard visual salvo: {dashboard_path}")
    
    return dashboard_path

def main():
    """Função principal do integrador"""
    
    print("🔗 INTEGRADOR DE ANÁLISE DE TRADING")
    print("=" * 50)
    
    # Verificar se análise foi executada
    if not os.path.exists('output/reports/trading_analysis_summary.json'):
        print("❌ Análise de trading não encontrada!")
        print("Execute primeiro: python analise_trading_estrategias.py")
        return
    
    # Exibir dashboard textual
    exibir_dashboard_trading()
    
    # Criar dashboard visual
    dashboard_path = criar_dashboard_visual()
    
    print(f"\n✅ Integração completa!")
    print(f"📁 Arquivos disponíveis:")
    print(f"   • Dashboard: {dashboard_path}")
    print(f"   • JSON: output/reports/trading_analysis_summary.json")
    print(f"   • Relatório: output/reports/trading_analysis_report.txt")
    print(f"   • Gráficos individuais: output/graphs/trading/")

if __name__ == "__main__":
    main()