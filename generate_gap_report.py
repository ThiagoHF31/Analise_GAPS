#!/usr/bin/env python3
"""
Gap Analysis Report Generator
=============================
Gera um relatório detalhado da análise de classificação de gaps
"""

import pandas as pd
import numpy as np

def generate_detailed_report():
    """Gera relatório detalhado da análise de gaps"""
    
    # Carregar dados
    metricas_df = pd.read_csv('data/processed/metricas_por_classe.csv')
    
    print("📊 RELATÓRIO DETALHADO - ANÁLISE DE GAPS POR CLASSE")
    print("=" * 80)
    print()
    
    # Resumo geral
    total_gaps = metricas_df['n_observacoes'].sum()
    total_gap_up = metricas_df['n_gap_up'].sum()
    total_gap_down = metricas_df['n_gap_down'].sum()
    
    print(f"📈 RESUMO GERAL:")
    print(f"   • Total de gaps analisados: {total_gaps:,}")
    print(f"   • Gaps de alta: {total_gap_up:,} ({total_gap_up/total_gaps*100:.1f}%)")
    print(f"   • Gaps de baixa: {total_gap_down:,} ({total_gap_down/total_gaps*100:.1f}%)")
    print()
    
    # Tabela detalhada por classe
    print("📋 TABELA DETALHADA POR CLASSE DE GAP:")
    print("=" * 80)
    
    for idx, row in metricas_df.iterrows():
        print(f"\n🔹 CLASSE: {row['intervalo']} pontos")
        print("-" * 50)
        print(f"   📊 Observações: {row['n_observacoes']:,} ({row['n_observacoes']/total_gaps*100:.1f}% do total)")
        print(f"   📈 Gap Up: {row['n_gap_up']:,} ({row['perc_gap_up']:.1f}%)")
        print(f"   📉 Gap Down: {row['n_gap_down']:,} ({row['perc_gap_down']:.1f}%)")
        print()
        
        print(f"   🎯 PROBABILIDADES DE FECHAMENTO:")
        print(f"      • Gap Up: {row['prob_fechamento_up']:.1%}")
        print(f"      • Gap Down: {row['prob_fechamento_down']:.1%}")
        print()
        
        print(f"   📏 AMPLITUDES:")
        print(f"      • Máxima: {row['amplitude_maxima']:,.0f} pontos")
        print(f"      • Mínima: {row['amplitude_minima']:,.0f} pontos")
        print(f"      • Média: {row['amplitude_media']:,.0f} pontos")
        print()
        
        print(f"   ⏱️  TEMPOS (em dias):")
        if not pd.isna(row['tempo_pico_up']):
            print(f"      • Tempo para pico (Gap Up): {row['tempo_pico_up']:.1f}")
        if not pd.isna(row['tempo_pico_down']):
            print(f"      • Tempo para pico (Gap Down): {row['tempo_pico_down']:.1f}")
        if not pd.isna(row['tempo_fechamento_up']):
            print(f"      • Tempo fechamento (Gap Up): {row['tempo_fechamento_up']:.1f}")
        if not pd.isna(row['tempo_fechamento_down']):
            print(f"      • Tempo fechamento (Gap Down): {row['tempo_fechamento_down']:.1f}")
        print()
        
        print(f"   📊 OUTRAS MÉTRICAS:")
        print(f"      • Volatilidade média: {row['volatilidade_media']:.2f}%")
        print(f"      • Gap médio: {row['gap_medio']:.0f} pontos")
        print(f"      • Range de gaps: {row['gap_min']:.0f} - {row['gap_max']:.0f} pontos")
    
    # Insights e conclusões
    print("\n🧠 INSIGHTS E CONCLUSÕES:")
    print("=" * 80)
    
    # Classe com maior probabilidade de fechamento
    max_prob_up = metricas_df.loc[metricas_df['prob_fechamento_up'].idxmax()]
    max_prob_down = metricas_df.loc[metricas_df['prob_fechamento_down'].idxmax()]
    
    print(f"✅ Maior probabilidade fechamento Gap Up: {max_prob_up['intervalo']} ({max_prob_up['prob_fechamento_up']:.1%})")
    print(f"✅ Maior probabilidade fechamento Gap Down: {max_prob_down['intervalo']} ({max_prob_down['prob_fechamento_down']:.1%})")
    
    # Tempos mais rápidos
    tempo_up_validos = metricas_df[~pd.isna(metricas_df['tempo_fechamento_up'])]
    tempo_down_validos = metricas_df[~pd.isna(metricas_df['tempo_fechamento_down'])]
    
    if len(tempo_up_validos) > 0:
        min_tempo_up = tempo_up_validos.loc[tempo_up_validos['tempo_fechamento_up'].idxmin()]
        print(f"⚡ Fechamento mais rápido Gap Up: {min_tempo_up['intervalo']} ({min_tempo_up['tempo_fechamento_up']:.1f} dias)")
    
    if len(tempo_down_validos) > 0:
        min_tempo_down = tempo_down_validos.loc[tempo_down_validos['tempo_fechamento_down'].idxmin()]
        print(f"⚡ Fechamento mais rápido Gap Down: {min_tempo_down['intervalo']} ({min_tempo_down['tempo_fechamento_down']:.1f} dias)")
    
    # Volatilidade
    max_vol = metricas_df.loc[metricas_df['volatilidade_media'].idxmax()]
    min_vol = metricas_df.loc[metricas_df['volatilidade_media'].idxmin()]
    
    print(f"📈 Maior volatilidade: {max_vol['intervalo']} ({max_vol['volatilidade_media']:.2f}%)")
    print(f"📉 Menor volatilidade: {min_vol['intervalo']} ({min_vol['volatilidade_media']:.2f}%)")
    
    print("\n💡 RECOMENDAÇÕES PARA TRADING:")
    print("=" * 80)
    print("• Gaps pequenos (100-265) têm alta probabilidade de fechamento rápido")
    print("• Gaps médios (265-455) oferecem bom equilíbrio risco/retorno") 
    print("• Gaps grandes (748+) têm maior volatilidade mas tempos de fechamento mais longos")
    print("• Considere stops baseados na amplitude máxima histórica de cada classe")
    print("• Monitore tempos de pico para otimizar pontos de entrada/saída")

def create_excel_report():
    """Cria um relatório em Excel com formatação"""
    try:
        metricas_df = pd.read_csv('data/processed/metricas_por_classe.csv')
        
        # Criar arquivo Excel com múltiplas abas
        with pd.ExcelWriter('output/reports/analise_gaps_detalhada.xlsx', engine='openpyxl') as writer:
            # Aba principal com métricas
            metricas_df.to_excel(writer, sheet_name='Métricas por Classe', index=False)
            
            # Aba com dados classificados (sample)
            gaps_class = pd.read_csv('data/processed/gaps_classificados.csv')
            gaps_sample = gaps_class.head(100)  # Apenas uma amostra para não ficar muito grande
            gaps_sample.to_excel(writer, sheet_name='Amostra Dados', index=False)
            
            # Aba com features para modelo
            features = pd.read_csv('data/processed/features_para_modelo.csv')
            features.head(100).to_excel(writer, sheet_name='Features Modelo', index=False)
        
        print(f"\n📊 Relatório Excel criado: output/reports/analise_gaps_detalhada.xlsx")
        
    except ImportError:
        print("⚠️  Para gerar arquivo Excel, instale: pip install openpyxl")

if __name__ == "__main__":
    generate_detailed_report()
    create_excel_report()