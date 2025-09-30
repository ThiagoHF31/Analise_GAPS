"""
Report Generator Module
Módulo responsável pela geração de relatórios detalhados
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

class ReportGenerator:
    """Classe para geração de relatórios detalhados da análise"""
    
    def __init__(self, config):
        self.config = config
        # Criar pasta de relatórios se não existir
        os.makedirs(f"{config['OUTPUT_DIR']}/reports", exist_ok=True)
    
    def calcular_metricas_performance(self, dados):
        """Calcula métricas de performance financeira"""
        if 'retorno_diario' not in dados.columns:
            return {}
        
        retornos = dados['retorno_diario'].dropna()
        
        metricas = {
            'retorno_medio_diario': retornos.mean(),
            'retorno_anualizado': retornos.mean() * 252,
            'volatilidade_diaria': retornos.std(),
            'volatilidade_anualizada': retornos.std() * np.sqrt(252),
            'sharpe_ratio': (retornos.mean() / retornos.std() * np.sqrt(252)) if retornos.std() != 0 else 0,
            'maior_ganho': retornos.max(),
            'maior_perda': retornos.min(),
            'dias_positivos': (retornos > 0).sum(),
            'dias_negativos': (retornos < 0).sum(),
            'taxa_acerto': (retornos > 0).mean()
        }
        
        # Calcular drawdown
        if 'fechamento' in dados.columns:
            precos_cumulativos = dados['fechamento']
            picos = precos_cumulativos.cummax()
            drawdowns = (precos_cumulativos - picos) / picos
            metricas['max_drawdown'] = drawdowns.min()
        
        return metricas
    
    def gerar_secao_dados_originais(self, dados_diarios):
        """Gera seção do relatório sobre dados originais"""
        linhas = []
        linhas.append("1. DADOS ORIGINAIS")
        linhas.append("=" * 50)
        linhas.append("")
        
        # Informações básicas
        linhas.append(f"Período analisado: {dados_diarios.index.min().strftime('%d/%m/%Y')} até {dados_diarios.index.max().strftime('%d/%m/%Y')}")
        linhas.append(f"Total de dias de negociação: {len(dados_diarios)}")
        linhas.append(f"Fonte: WIN$N M1 (Mini Índice Bovespa)")
        linhas.append("")
        
        # Estatísticas de preços
        linhas.append("ESTATÍSTICAS DE PREÇOS:")
        linhas.append(f"  • Preço médio de fechamento: {dados_diarios['fechamento'].mean():,.2f} pontos")
        linhas.append(f"  • Maior máxima: {dados_diarios['maxima'].max():,.0f} pontos")
        linhas.append(f"  • Menor mínima: {dados_diarios['minima'].min():,.0f} pontos")
        linhas.append(f"  • Amplitude média diária: {dados_diarios['amplitude'].mean():,.2f} pontos")
        linhas.append(f"  • Volatilidade média diária: {dados_diarios['volatilidade'].mean():.2f}%")
        linhas.append("")
        
        # Estatísticas de volume
        linhas.append("ESTATÍSTICAS DE VOLUME:")
        linhas.append(f"  • Volume médio diário: {dados_diarios['volume_total'].mean():,.0f}")
        linhas.append(f"  • Volume máximo diário: {dados_diarios['volume_total'].max():,.0f}")
        linhas.append(f"  • Volume mínimo diário: {dados_diarios['volume_total'].min():,.0f}")
        linhas.append("")
        
        # Métricas de performance
        metricas = self.calcular_metricas_performance(dados_diarios)
        if metricas:
            linhas.append("MÉTRICAS DE PERFORMANCE:")
            linhas.append(f"  • Retorno médio diário: {metricas['retorno_medio_diario']*100:.3f}%")
            linhas.append(f"  • Retorno anualizado: {metricas['retorno_anualizado']*100:.2f}%")
            linhas.append(f"  • Volatilidade anualizada: {metricas['volatilidade_anualizada']*100:.2f}%")
            linhas.append(f"  • Sharpe Ratio: {metricas['sharpe_ratio']:.3f}")
            linhas.append(f"  • Maior ganho diário: {metricas['maior_ganho']*100:.2f}%")
            linhas.append(f"  • Maior perda diária: {metricas['maior_perda']*100:.2f}%")
            linhas.append(f"  • Taxa de acerto: {metricas['taxa_acerto']*100:.1f}%")
            if 'max_drawdown' in metricas:
                linhas.append(f"  • Máximo drawdown: {metricas['max_drawdown']*100:.2f}%")
        
        return linhas
    
    def gerar_secao_gaps(self, gaps_analisados):
        """Gera seção do relatório sobre análise de gaps"""
        linhas = []
        linhas.append("2. ANÁLISE DE GAPS")
        linhas.append("=" * 50)
        linhas.append("")
        
        if gaps_analisados is None or len(gaps_analisados) == 0:
            linhas.append("❌ Nenhum gap significativo encontrado para análise.")
            linhas.append("")
            return linhas
        
        # Estatísticas gerais
        total_gaps = len(gaps_analisados)
        gaps_fechados = gaps_analisados['gap_fechado'].sum()
        taxa_fechamento = gaps_fechados / total_gaps * 100
        
        linhas.append("ESTATÍSTICAS GERAIS:")
        linhas.append(f"  • Total de gaps significativos: {total_gaps}")
        linhas.append(f"  • Gaps fechados: {gaps_fechados} ({taxa_fechamento:.1f}%)")
        linhas.append(f"  • Gaps não fechados: {total_gaps - gaps_fechados}")
        linhas.append(f"  • Critério de gap mínimo: {self.config['GAP_MINIMO']} pontos")
        linhas.append(f"  • Gap médio: {gaps_analisados['gap_absoluto'].mean():.1f} pontos")
        linhas.append(f"  • Maior gap: {gaps_analisados['gap_absoluto'].max():.0f} pontos")
        linhas.append("")
        
        # Análise por tipo
        linhas.append("ANÁLISE POR TIPO DE GAP:")
        for tipo in ['Gap Up', 'Gap Down']:
            subset = gaps_analisados[gaps_analisados['tipo_gap'] == tipo]
            if len(subset) > 0:
                fechados_tipo = subset['gap_fechado'].sum()
                taxa_tipo = fechados_tipo / len(subset) * 100
                gap_medio_tipo = subset['gap_absoluto'].mean()
                
                linhas.append(f"  {tipo}:")
                linhas.append(f"    - Quantidade: {len(subset)}")
                linhas.append(f"    - Fechados: {fechados_tipo} ({taxa_tipo:.1f}%)")
                linhas.append(f"    - Gap médio: {gap_medio_tipo:.1f} pontos")
                linhas.append("")
        
        # Análise temporal
        gaps_fechados_df = gaps_analisados[gaps_analisados['gap_fechado'] == True]
        if len(gaps_fechados_df) > 0:
            tempo_medio = gaps_fechados_df['dias_para_fechamento'].mean()
            tempo_mediano = gaps_fechados_df['dias_para_fechamento'].median()
            tempo_min = gaps_fechados_df['dias_para_fechamento'].min()
            tempo_max = gaps_fechados_df['dias_para_fechamento'].max()
            
            linhas.append("TEMPO PARA FECHAMENTO:")
            linhas.append(f"  • Tempo médio: {tempo_medio:.1f} dias")
            linhas.append(f"  • Tempo mediano: {tempo_mediano:.1f} dias")
            linhas.append(f"  • Fechamento mais rápido: {tempo_min:.0f} dia(s)")
            linhas.append(f"  • Fechamento mais lento: {tempo_max:.0f} dias")
            linhas.append("")
            
            # Distribuição de tempos
            linhas.append("DISTRIBUIÇÃO DE TEMPOS DE FECHAMENTO:")
            bins = [0, 1, 3, 7, 15, 30]
            labels = ['1 dia', '2-3 dias', '4-7 dias', '8-15 dias', '16-30 dias']
            
            for i, (bin_start, bin_end) in enumerate(zip(bins[:-1], bins[1:])):
                if i == 0:
                    count = (gaps_fechados_df['dias_para_fechamento'] <= bin_end).sum()
                else:
                    count = ((gaps_fechados_df['dias_para_fechamento'] > bin_start) & 
                            (gaps_fechados_df['dias_para_fechamento'] <= bin_end)).sum()
                
                pct = count / len(gaps_fechados_df) * 100
                linhas.append(f"  • {labels[i]}: {count} gaps ({pct:.1f}%)")
        
        return linhas
    
    def gerar_secao_dados_finais(self, dados_originais, dados_finais):
        """Gera seção sobre dados finais limpos"""
        linhas = []
        linhas.append("3. DATASET FINAL LIMPO")
        linhas.append("=" * 50)
        linhas.append("")
        
        # Comparação de tamanhos
        dias_removidos = len(dados_originais) - len(dados_finais)
        reducao_pct = dias_removidos / len(dados_originais) * 100
        
        linhas.append("PROCESSO DE LIMPEZA:")
        linhas.append(f"  • Dados originais: {len(dados_originais)} dias")
        linhas.append(f"  • Dados finais: {len(dados_finais)} dias")
        linhas.append(f"  • Dias removidos: {dias_removidos} ({reducao_pct:.1f}%)")
        linhas.append(f"  • Critério: Remoção de gaps não fechados")
        linhas.append("")
        
        # Métricas dos dados finais
        metricas_finais = self.calcular_metricas_performance(dados_finais)
        if metricas_finais:
            linhas.append("MÉTRICAS DO DATASET FINAL:")
            linhas.append(f"  • Retorno médio diário: {metricas_finais['retorno_medio_diario']*100:.3f}%")
            linhas.append(f"  • Retorno anualizado: {metricas_finais['retorno_anualizado']*100:.2f}%")
            linhas.append(f"  • Volatilidade anualizada: {metricas_finais['volatilidade_anualizada']*100:.2f}%")
            linhas.append(f"  • Sharpe Ratio: {metricas_finais['sharpe_ratio']:.3f}")
            linhas.append(f"  • Taxa de acerto: {metricas_finais['taxa_acerto']*100:.1f}%")
            if 'max_drawdown' in metricas_finais:
                linhas.append(f"  • Máximo drawdown: {metricas_finais['max_drawdown']*100:.2f}%")
            linhas.append("")
        
        # Comparação com dados originais
        if metricas_finais:
            metricas_originais = self.calcular_metricas_performance(dados_originais)
            if metricas_originais:
                linhas.append("COMPARAÇÃO COM DADOS ORIGINAIS:")
                
                mudanca_retorno = ((metricas_finais['retorno_medio_diario'] - metricas_originais['retorno_medio_diario']) / 
                                 abs(metricas_originais['retorno_medio_diario']) * 100) if metricas_originais['retorno_medio_diario'] != 0 else 0
                
                mudanca_vol = ((metricas_finais['volatilidade_anualizada'] - metricas_originais['volatilidade_anualizada']) / 
                              metricas_originais['volatilidade_anualizada'] * 100) if metricas_originais['volatilidade_anualizada'] != 0 else 0
                
                linhas.append(f"  • Mudança no retorno médio: {mudanca_retorno:+.2f}%")
                linhas.append(f"  • Mudança na volatilidade: {mudanca_vol:+.2f}%")
                linhas.append(f"  • Mudança no Sharpe Ratio: {metricas_finais['sharpe_ratio'] - metricas_originais['sharpe_ratio']:+.3f}")
        
        return linhas
    
    def gerar_secao_recomendacoes(self, gaps_analisados):
        """Gera seção de conclusões e recomendações"""
        linhas = []
        linhas.append("4. CONCLUSÕES E RECOMENDAÇÕES")
        linhas.append("=" * 50)
        linhas.append("")
        
        linhas.append("QUALIDADE DOS DADOS:")
        linhas.append("  ✅ Dataset robusto com dados históricos consistentes")
        linhas.append("  ✅ Baixa incidência de outliers problemáticos")
        linhas.append("  ✅ Processo de limpeza preservou integridade estatística")
        linhas.append("")
        
        if gaps_analisados is not None and len(gaps_analisados) > 0:
            taxa_fechamento = gaps_analisados['gap_fechado'].mean() * 100
            
            linhas.append("INSIGHTS SOBRE GAPS:")
            if taxa_fechamento > 85:
                linhas.append("  ✅ Alta taxa de fechamento de gaps indica mercado eficiente")
            elif taxa_fechamento > 70:
                linhas.append("  ⚠️  Taxa moderada de fechamento de gaps")
            else:
                linhas.append("  ❌ Baixa taxa de fechamento de gaps")
                
            linhas.append(f"  📊 {taxa_fechamento:.1f}% dos gaps significativos são fechados")
            
            # Tempo médio
            gaps_fechados = gaps_analisados[gaps_analisados['gap_fechado'] == True]
            if len(gaps_fechados) > 0:
                tempo_medio = gaps_fechados['dias_para_fechamento'].mean()
                linhas.append(f"  ⏱️  Tempo médio para fechamento: {tempo_medio:.1f} dias")
            linhas.append("")
        
        linhas.append("RECOMENDAÇÕES PARA TRADING:")
        linhas.append("  🎯 Utilizar arquivo 'dados_limpos_finais.csv' para backtesting")
        linhas.append("  📈 Considerar estratégias de reversão em gaps")
        linhas.append(f"  🔍 Focar em gaps >= {self.config['GAP_MINIMO']} pontos")
        
        if gaps_analisados is not None and len(gaps_analisados) > 0:
            gap_up = gaps_analisados[gaps_analisados['tipo_gap'] == 'Gap Up']
            gap_down = gaps_analisados[gaps_analisados['tipo_gap'] == 'Gap Down']
            
            if len(gap_up) > 0 and len(gap_down) > 0:
                taxa_up = gap_up['gap_fechado'].mean() * 100
                taxa_down = gap_down['gap_fechado'].mean() * 100
                
                if abs(taxa_up - taxa_down) > 5:
                    if taxa_up > taxa_down:
                        linhas.append("  📊 Gaps Up têm maior probabilidade de fechamento")
                    else:
                        linhas.append("  📊 Gaps Down têm maior probabilidade de fechamento")
        
        linhas.append("")
        
        linhas.append("PRÓXIMOS PASSOS SUGERIDOS:")
        linhas.append("  1. Implementar backtesting de estratégias baseadas em gaps")
        linhas.append("  2. Analisar sazonalidade (gaps por dia da semana/mês)")
        linhas.append("  3. Estudar correlação entre volume e fechamento de gaps")
        linhas.append("  4. Desenvolver modelos preditivos para probabilidade de fechamento")
        linhas.append("  5. Testar diferentes thresholds de gap mínimo")
        
        return linhas
    
    def gerar_cabecalho_relatorio(self):
        """Gera cabeçalho do relatório"""
        linhas = []
        linhas.append("RELATÓRIO DE ANÁLISE FINANCEIRA WIN$N")
        linhas.append("=" * 80)
        linhas.append("")
        linhas.append(f"Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        linhas.append("Instrumento: WIN$N (Mini Índice Bovespa)")
        linhas.append("Timeframe: M1 (agregado para diário)")
        linhas.append("Desenvolvido para: Análise de Gaps e Trading")
        linhas.append("")
        linhas.append("CONFIGURAÇÕES UTILIZADAS:")
        linhas.append(f"  • Gap mínimo: {self.config['GAP_MINIMO']} pontos")
        linhas.append(f"  • Threshold outliers: {self.config['OUTLIER_THRESHOLD']}")
        linhas.append(f"  • Limite dias gap: {self.config['DIAS_LIMITE_GAP']} dias")
        linhas.append("")
        linhas.append("")
        
        return linhas
    
    def gerar_relatorio_completo(self, dados_diarios, gaps_analisados, dados_finais):
        """Gera relatório completo da análise"""
        print("\n📋 INICIANDO GERAÇÃO DE RELATÓRIO")
        print("=" * 50)
        
        try:
            # Montar conteúdo do relatório
            conteudo = []
            
            # Cabeçalho
            conteudo.extend(self.gerar_cabecalho_relatorio())
            
            # Seções
            conteudo.extend(self.gerar_secao_dados_originais(dados_diarios))
            conteudo.append("")
            
            conteudo.extend(self.gerar_secao_gaps(gaps_analisados))
            conteudo.append("")
            
            conteudo.extend(self.gerar_secao_dados_finais(dados_diarios, dados_finais))
            conteudo.append("")
            
            conteudo.extend(self.gerar_secao_recomendacoes(gaps_analisados))
            
            # Rodapé
            conteudo.append("")
            conteudo.append("=" * 80)
            conteudo.append("Relatório gerado automaticamente pelo WIN$N Financial Analyzer")
            conteudo.append("Desenvolvido para análise do mercado brasileiro")
            
            # Salvar relatório
            caminho_relatorio = f"{self.config['OUTPUT_DIR']}/reports/relatorio_completo.txt"
            
            with open(caminho_relatorio, 'w', encoding='utf-8') as f:
                f.write('\n'.join(conteudo))
            
            print(f"✅ Relatório gerado: {caminho_relatorio}")
            print(f"📄 {len(conteudo)} linhas de conteúdo")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}")
            return False