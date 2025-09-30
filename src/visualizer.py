"""
Visualizer Module
Módulo responsável pela geração de gráficos e visualizações
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# Configurar matplotlib
plt.style.use('default')
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10

class Visualizer:
    """Classe para geração de visualizações e gráficos"""
    
    def __init__(self, config):
        self.config = config
        # Criar pasta de gráficos se não existir
        os.makedirs(f"{config['OUTPUT_DIR']}/graphs", exist_ok=True)
    
    def plotar_evolucao_precos(self, dados_diarios):
        """Gera gráfico de evolução temporal dos preços"""
        print("📊 Gerando gráfico de evolução de preços...")
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(20, 12))
            fig.suptitle('WIN$N - Análise Temporal (Dados Diários)', fontsize=16, fontweight='bold')
            
            # 1. Evolução dos preços de fechamento
            ax1 = axes[0, 0]
            ax1.plot(dados_diarios.index, dados_diarios['fechamento'], 
                     color='blue', linewidth=1, alpha=0.8)
            ax1.fill_between(dados_diarios.index, 
                           dados_diarios['minima'], dados_diarios['maxima'], 
                           alpha=0.2, color='gray', label='Range Min-Max')
            ax1.set_title('Evolução dos Preços de Fechamento')
            ax1.set_ylabel('Preço (pontos)')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # 2. Volume diário
            ax2 = axes[0, 1]
            ax2.bar(dados_diarios.index, dados_diarios['volume_total'], 
                   width=1, alpha=0.6, color='orange')
            ax2.set_title('Volume Diário Total')
            ax2.set_ylabel('Volume')
            ax2.grid(True, alpha=0.3)
            
            # 3. Retornos diários
            ax3 = axes[1, 0]
            retornos = dados_diarios['retorno_diario'] * 100
            cores = ['green' if x > 0 else 'red' for x in retornos]
            ax3.bar(dados_diarios.index, retornos, width=1, color=cores, alpha=0.7)
            ax3.axhline(y=0, color='black', linestyle='-', alpha=0.8)
            ax3.set_title('Retornos Diários (%)')
            ax3.set_ylabel('Retorno (%)')
            ax3.grid(True, alpha=0.3)
            
            # 4. Volatilidade diária
            ax4 = axes[1, 1]
            ax4.plot(dados_diarios.index, dados_diarios['volatilidade'], 
                     color='purple', linewidth=1, alpha=0.8)
            ax4.set_title('Volatilidade Diária (%)')
            ax4.set_ylabel('Volatilidade (%)')
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Salvar gráfico
            caminho_grafico = f"{self.config['OUTPUT_DIR']}/graphs/evolucao_precos.png"
            plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Gráfico salvo: {caminho_grafico}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de evolução: {e}")
            return False
    
    def plotar_analise_gaps(self, gaps_analisados):
        """Gera gráficos de análise de gaps"""
        if gaps_analisados is None or len(gaps_analisados) == 0:
            print("⚠️  Nenhum gap para plotar")
            return False
        
        print("📊 Gerando gráficos de análise de gaps...")
        
        try:
            fig, axes = plt.subplots(2, 3, figsize=(20, 12))
            fig.suptitle('WIN$N - Análise Detalhada de Gaps', fontsize=16, fontweight='bold')
            
            # 1. Distribuição do tamanho dos gaps
            ax1 = axes[0, 0]
            gaps_analisados['gap_absoluto'].hist(bins=30, ax=ax1, alpha=0.7, 
                                               color='skyblue', edgecolor='black')
            ax1.set_title('Distribuição do Tamanho dos Gaps')
            ax1.set_xlabel('Gap (pontos)')
            ax1.set_ylabel('Frequência')
            ax1.grid(True, alpha=0.3)
            
            # 2. Gaps fechados vs não fechados
            ax2 = axes[0, 1]
            gap_counts = gaps_analisados['gap_fechado'].value_counts()
            labels = ['Não Fechados', 'Fechados']
            colors = ['lightcoral', 'lightgreen']
            # Reorganizar para [False, True] se necessário
            values = [gap_counts.get(False, 0), gap_counts.get(True, 0)]
            ax2.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax2.set_title('Proporção de Gaps Fechados')
            
            # 3. Distribuição por tipo de gap
            ax3 = axes[0, 2]
            tipo_counts = gaps_analisados['tipo_gap'].value_counts()
            bars = ax3.bar(tipo_counts.index, tipo_counts.values, 
                          color=['red', 'blue'], alpha=0.7)
            ax3.set_title('Distribuição por Tipo de Gap')
            ax3.set_ylabel('Quantidade')
            ax3.grid(True, alpha=0.3)
            
            # Adicionar valores nas barras
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom')
            
            # 4. Tempo para fechamento
            ax4 = axes[1, 0]
            gaps_fechados = gaps_analisados[gaps_analisados['gap_fechado'] == True]
            if len(gaps_fechados) > 0:
                gaps_fechados['dias_para_fechamento'].hist(bins=20, ax=ax4, alpha=0.7, 
                                                          color='green', edgecolor='black')
                ax4.set_title('Distribuição: Dias para Fechar Gap')
                ax4.set_xlabel('Dias')
                ax4.set_ylabel('Frequência')
                ax4.grid(True, alpha=0.3)
                
                # Linha da média
                media_dias = gaps_fechados['dias_para_fechamento'].mean()
                ax4.axvline(media_dias, color='red', linestyle='--', 
                           label=f'Média: {media_dias:.1f} dias')
                ax4.legend()
            
            # 5. Status por tipo de gap
            ax5 = axes[1, 1]
            if 'tipo_gap' in gaps_analisados.columns and 'gap_fechado' in gaps_analisados.columns:
                gap_tipo_status = gaps_analisados.groupby(['tipo_gap', 'gap_fechado']).size().unstack(fill_value=0)
                gap_tipo_status.plot(kind='bar', ax=ax5, color=['lightcoral', 'lightgreen'], 
                                   alpha=0.8, stacked=False)
                ax5.set_title('Status dos Gaps por Tipo')
                ax5.set_ylabel('Quantidade')
                ax5.legend(['Não Fechados', 'Fechados'])
                ax5.tick_params(axis='x', rotation=45)
                ax5.grid(True, alpha=0.3)
            
            # 6. Evolução temporal dos gaps
            ax6 = axes[1, 2]
            try:
                gaps_por_mes = gaps_analisados.groupby(gaps_analisados.index.to_period('M')).size()
                gaps_por_mes.plot(ax=ax6, color='purple', marker='o', linewidth=2)
                ax6.set_title('Gaps por Mês')
                ax6.set_ylabel('Número de Gaps')
                ax6.grid(True, alpha=0.3)
                ax6.tick_params(axis='x', rotation=45)
            except Exception:
                ax6.text(0.5, 0.5, 'Dados insuficientes\npara análise temporal', 
                        ha='center', va='center', transform=ax6.transAxes)
                ax6.set_title('Evolução Temporal dos Gaps')
            
            plt.tight_layout()
            
            # Salvar gráfico
            caminho_grafico = f"{self.config['OUTPUT_DIR']}/graphs/analise_gaps.png"
            plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Gráfico salvo: {caminho_grafico}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de gaps: {e}")
            return False
    
    def plotar_comparacao_datasets(self, dados_originais, dados_finais):
        """Compara datasets antes e depois da limpeza"""
        print("📊 Gerando gráfico de comparação...")
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            fig.suptitle('Comparação: Dados Originais vs Dados Limpos Finais', 
                        fontsize=14, fontweight='bold')
            
            # 1. Comparação de retornos
            ax1 = axes[0, 0]
            ax1.hist(dados_originais['retorno_diario']*100, bins=50, alpha=0.6, 
                     label='Original', color='blue', density=True)
            ax1.hist(dados_finais['retorno_diario']*100, bins=50, alpha=0.6, 
                     label='Dados Limpos', color='red', density=True)
            ax1.set_title('Distribuição dos Retornos Diários')
            ax1.set_xlabel('Retorno (%)')
            ax1.set_ylabel('Densidade')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 2. Comparação de volatilidade
            ax2 = axes[0, 1]
            ax2.hist(dados_originais['volatilidade'], bins=50, alpha=0.6, 
                     label='Original', color='blue', density=True)
            ax2.hist(dados_finais['volatilidade'], bins=50, alpha=0.6, 
                     label='Dados Limpos', color='red', density=True)
            ax2.set_title('Distribuição da Volatilidade')
            ax2.set_xlabel('Volatilidade (%)')
            ax2.set_ylabel('Densidade')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # 3. Evolução comparativa dos preços
            ax3 = axes[1, 0]
            ax3.plot(dados_originais.index, dados_originais['fechamento'], 
                     label='Original', alpha=0.7, linewidth=1)
            ax3.plot(dados_finais.index, dados_finais['fechamento'], 
                     label='Dados Limpos', alpha=0.8, linewidth=1)
            ax3.set_title('Evolução dos Preços de Fechamento')
            ax3.set_ylabel('Preço (pontos)')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # 4. Estatísticas comparativas
            ax4 = axes[1, 1]
            stats_original = [
                dados_originais['retorno_diario'].mean()*100,
                dados_originais['retorno_diario'].std()*100,
                dados_originais['volatilidade'].mean(),
                len(dados_originais)
            ]
            
            stats_limpo = [
                dados_finais['retorno_diario'].mean()*100,
                dados_finais['retorno_diario'].std()*100,
                dados_finais['volatilidade'].mean(),
                len(dados_finais)
            ]
            
            x = np.arange(4)
            width = 0.35
            
            labels = ['Ret. Médio (%)', 'Vol. Retornos (%)', 'Volatilidade (%)', 'Nº Dias']
            
            bars1 = ax4.bar(x - width/2, stats_original, width, 
                           label='Original', alpha=0.7, color='blue')
            bars2 = ax4.bar(x + width/2, stats_limpo, width, 
                           label='Dados Limpos', alpha=0.7, color='red')
            
            ax4.set_title('Comparação de Estatísticas')
            ax4.set_xticks(x)
            ax4.set_xticklabels(labels, rotation=45)
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            
            # Adicionar valores nas barras
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax4.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}', ha='center', va='bottom', fontsize=8)
            
            plt.tight_layout()
            
            # Salvar gráfico
            caminho_grafico = f"{self.config['OUTPUT_DIR']}/graphs/comparacao_datasets.png"
            plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Gráfico salvo: {caminho_grafico}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico de comparação: {e}")
            return False
    
    def gerar_todos_graficos(self, dados_diarios, gaps_analisados, dados_finais):
        """Gera todos os gráficos da análise"""
        print("\n📊 INICIANDO GERAÇÃO DE GRÁFICOS")
        print("=" * 50)
        
        graficos_gerados = 0
        
        # 1. Evolução de preços
        if self.plotar_evolucao_precos(dados_diarios):
            graficos_gerados += 1
        
        # 2. Análise de gaps (se houver)
        if gaps_analisados is not None:
            if self.plotar_analise_gaps(gaps_analisados):
                graficos_gerados += 1
        
        # 3. Comparação de datasets
        if self.plotar_comparacao_datasets(dados_diarios, dados_finais):
            graficos_gerados += 1
        
        print(f"\n✅ Geração de gráficos concluída!")
        print(f"📊 {graficos_gerados} gráficos gerados com sucesso")
        print(f"📁 Pasta: {self.config['OUTPUT_DIR']}/graphs/")
        
        return graficos_gerados > 0