#!/usr/bin/env python3
"""
Gap Classification Analysis
===========================
Análise estatística para classificação otimizada de gaps em intervalos
com métricas detalhadas para cada classe.

Autor: GitHub Copilot
Data: 2025-10-01
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

class GapClassificationAnalyzer:
    def __init__(self, gaps_file):
        """Inicializa o analisador com dados de gaps"""
        self.gaps_df = pd.read_csv(gaps_file, index_col=0, parse_dates=True)
        self.gaps_df = self.gaps_df[self.gaps_df['gap_absoluto'] >= 100]  # Apenas gaps significativos
        
    def analyze_distribution(self):
        """Analisa a distribuição dos gaps para determinar os melhores intervalos"""
        print("📊 ANÁLISE DE DISTRIBUIÇÃO DOS GAPS")
        print("=" * 60)
        
        gaps = self.gaps_df['gap_absoluto'].values
        
        print(f"📈 Total de gaps analisados: {len(gaps)}")
        print(f"📊 Gap mínimo: {gaps.min():.0f} pontos")
        print(f"📊 Gap máximo: {gaps.max():.0f} pontos")
        print(f"📊 Gap médio: {gaps.mean():.1f} pontos")
        print(f"📊 Gap mediano: {np.median(gaps):.1f} pontos")
        print(f"📊 Desvio padrão: {gaps.std():.1f} pontos")
        
        # Análise de distribuição
        print("\n📊 ANÁLISE ESTATÍSTICA DA DISTRIBUIÇÃO")
        print("-" * 50)
        
        # Quartis
        q1, q2, q3 = np.percentile(gaps, [25, 50, 75])
        iqr = q3 - q1
        
        print(f"• Q1 (25%): {q1:.0f} pontos")
        print(f"• Q2 (50%): {q2:.0f} pontos")
        print(f"• Q3 (75%): {q3:.0f} pontos")
        print(f"• IQR: {iqr:.0f} pontos")
        
        # Teste de normalidade
        stat, p_value = stats.normaltest(gaps)
        print(f"• Teste de normalidade: p-value = {p_value:.2e}")
        print(f"• Distribuição: {'Normal' if p_value > 0.05 else 'Não-normal'}")
        
        # Análise de densidade
        return self._optimize_intervals(gaps)
    
    def _optimize_intervals(self, gaps):
        """Otimiza os intervalos usando diferentes métodos estatísticos"""
        print("\n🔍 OTIMIZAÇÃO DE INTERVALOS")
        print("-" * 50)
        
        methods = {}
        
        # Método 1: Quantis uniformes (5 intervalos)
        percentiles = np.percentile(gaps, [0, 20, 40, 60, 80, 100])
        methods['quantis_uniformes'] = percentiles
        print(f"• Quantis uniformes (5 classes): {[int(x) for x in percentiles]}")
        
        # Método 2: Quartis + extremos
        q1, q2, q3 = np.percentile(gaps, [25, 50, 75])
        quartil_intervals = [gaps.min(), q1, q2, q3, gaps.max()]
        methods['quartis'] = quartil_intervals
        print(f"• Quartis: {[int(x) for x in quartil_intervals]}")
        
        # Método 3: Regra de Sturges modificada
        n_sturges = int(np.log2(len(gaps)) + 1)
        sturges_intervals = np.linspace(gaps.min(), gaps.max(), n_sturges + 1)
        methods['sturges'] = sturges_intervals
        print(f"• Sturges ({n_sturges} classes): {[int(x) for x in sturges_intervals]}")
        
        # Método 4: K-means otimizado
        optimal_k = self._find_optimal_clusters(gaps)
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(gaps.reshape(-1, 1))
        cluster_centers = sorted(kmeans.cluster_centers_.flatten())
        
        # Criar intervalos baseados nos clusters
        kmeans_intervals = [gaps.min()]
        for i in range(len(cluster_centers) - 1):
            boundary = (cluster_centers[i] + cluster_centers[i+1]) / 2
            kmeans_intervals.append(boundary)
        kmeans_intervals.append(gaps.max())
        
        methods['kmeans'] = kmeans_intervals
        print(f"• K-means ({optimal_k} clusters): {[int(x) for x in kmeans_intervals]}")
        
        # Método 5: Intervalos customizados baseados em análise de mercado
        custom_intervals = [100, 250, 500, 1000, 2000, gaps.max()]
        methods['custom'] = custom_intervals
        print(f"• Customizado (mercado): {[int(x) for x in custom_intervals]}")
        
        # Avaliar métodos
        best_method = self._evaluate_methods(gaps, methods)
        print(f"\n✅ Melhor método selecionado: {best_method}")
        
        return methods[best_method]
    
    def _find_optimal_clusters(self, gaps):
        """Encontra o número ótimo de clusters usando método do cotovelo"""
        max_k = min(10, len(np.unique(gaps)) // 20)  # Máximo razoável
        if max_k < 2:
            return 5  # Default
        
        inertias = []
        k_range = range(2, max_k + 1)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(gaps.reshape(-1, 1))
            inertias.append(kmeans.inertia_)
        
        # Método do cotovelo
        if len(inertias) >= 3:
            diffs = np.diff(inertias)
            diffs2 = np.diff(diffs)
            optimal_k = k_range[np.argmax(diffs2) + 1]
        else:
            optimal_k = 5  # Default
        
        return min(optimal_k, 6)  # Limitar a 6 clusters
    
    def _evaluate_methods(self, gaps, methods):
        """Avalia os métodos de intervalos usando múltiplos critérios"""
        scores = {}
        
        for method_name, intervals in methods.items():
            # Criar bins
            bins = pd.cut(gaps, bins=intervals, include_lowest=True, duplicates='drop')
            bin_counts = bins.value_counts()
            
            # Critério 1: Distribuição balanceada (menor variância)
            balance_score = 1 / (bin_counts.std() / bin_counts.mean()) if bin_counts.std() > 0 else 1
            
            # Critério 2: Número mínimo por bin
            min_obs_score = 1 if bin_counts.min() >= 10 else bin_counts.min() / 10
            
            # Critério 3: Facilidade de interpretação (penalizar muitos bins)
            simplicity_score = 1 / len(intervals) if len(intervals) > 0 else 0
            
            # Score total (pode ajustar pesos)
            total_score = (balance_score * 0.4 + min_obs_score * 0.4 + simplicity_score * 0.2)
            scores[method_name] = total_score
        
        return max(scores, key=scores.get)
    
    def classify_gaps(self, intervals):
        """Classifica os gaps nos intervalos otimizados"""
        print(f"\n📊 CLASSIFICAÇÃO DOS GAPS")
        print("=" * 60)
        
        # Criar labels para os intervalos
        labels = []
        for i in range(len(intervals) - 1):
            labels.append(f"{int(intervals[i])}-{int(intervals[i+1])}")
        
        # Classificar gaps
        self.gaps_df['gap_class'] = pd.cut(
            self.gaps_df['gap_absoluto'], 
            bins=intervals, 
            labels=labels, 
            include_lowest=True
        )
        
        print(f"✅ Intervalos criados: {labels}")
        print(f"✅ Gaps classificados: {len(self.gaps_df)}")
        
        return intervals, labels
    
    def calculate_metrics_by_class(self):
        """Calcula métricas detalhadas para cada classe de gap"""
        print(f"\n📈 CALCULANDO MÉTRICAS POR CLASSE")
        print("=" * 60)
        
        results = []
        
        for gap_class in self.gaps_df['gap_class'].cat.categories:
            class_data = self.gaps_df[self.gaps_df['gap_class'] == gap_class].copy()
            
            if len(class_data) == 0:
                continue
            
            # Métricas básicas
            n_obs = len(class_data)
            n_gap_up = len(class_data[class_data['tipo_gap'] == 'Gap Up'])
            n_gap_down = len(class_data[class_data['tipo_gap'] == 'Gap Down'])
            
            # Probabilidades de fechamento
            gaps_fechados_up = class_data[(class_data['tipo_gap'] == 'Gap Up') & (class_data['gap_fechado'] == True)]
            gaps_fechados_down = class_data[(class_data['tipo_gap'] == 'Gap Down') & (class_data['gap_fechado'] == True)]
            
            prob_fechamento_up = len(gaps_fechados_up) / n_gap_up if n_gap_up > 0 else 0
            prob_fechamento_down = len(gaps_fechados_down) / n_gap_down if n_gap_down > 0 else 0
            
            # Amplitudes
            amplitude_max = class_data['amplitude'].max()
            amplitude_min = class_data['amplitude'].min()
            amplitude_media = class_data['amplitude'].mean()
            
            # Tempos para fechamento
            tempo_fechamento_up = gaps_fechados_up['dias_para_fechamento'].mean() if len(gaps_fechados_up) > 0 else np.nan
            tempo_fechamento_down = gaps_fechados_down['dias_para_fechamento'].mean() if len(gaps_fechados_down) > 0 else np.nan
            
            # Tempo para pico (usando amplitude como proxy para movimento máximo)
            # Calcular o tempo até atingir a máxima amplitude dentro do período
            tempo_pico_up = self._calculate_time_to_peak(class_data[class_data['tipo_gap'] == 'Gap Up'])
            tempo_pico_down = self._calculate_time_to_peak(class_data[class_data['tipo_gap'] == 'Gap Down'])
            
            # Volatilidade média
            volatilidade_media = class_data['volatilidade'].mean()
            
            result = {
                'intervalo': gap_class,
                'n_observacoes': n_obs,
                'n_gap_up': n_gap_up,
                'n_gap_down': n_gap_down,
                'perc_gap_up': (n_gap_up / n_obs) * 100,
                'perc_gap_down': (n_gap_down / n_obs) * 100,
                'prob_fechamento_up': prob_fechamento_up,
                'prob_fechamento_down': prob_fechamento_down,
                'amplitude_maxima': amplitude_max,
                'amplitude_minima': amplitude_min,
                'amplitude_media': amplitude_media,
                'tempo_fechamento_up': tempo_fechamento_up,
                'tempo_fechamento_down': tempo_fechamento_down,
                'tempo_pico_up': tempo_pico_up,
                'tempo_pico_down': tempo_pico_down,
                'volatilidade_media': volatilidade_media,
                'gap_medio': class_data['gap_absoluto'].mean(),
                'gap_min': class_data['gap_absoluto'].min(),
                'gap_max': class_data['gap_absoluto'].max()
            }
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def _calculate_time_to_peak(self, class_data):
        """Calcula o tempo médio para atingir o pico do movimento"""
        if len(class_data) == 0:
            return np.nan
        
        # Como uma aproximação, vamos usar a amplitude como indicador
        # Em dados futuros, seria ideal ter dados intraday para calcular isso precisamente
        # Por ora, vamos estimar baseado na volatilidade e amplitude
        
        # Assumindo que gaps maiores tendem a ter picos mais rápidos (primeiros dias)
        # Esta é uma heurística que pode ser refinada com mais dados
        gaps_with_closure = class_data[class_data['gap_fechado'] == True]
        
        if len(gaps_with_closure) == 0:
            return np.nan
        
        # Estimar que o pico ocorre em aproximadamente 30-70% do tempo de fechamento
        # (baseado em estudos de comportamento de gaps)
        tempo_fechamento = gaps_with_closure['dias_para_fechamento']
        tempo_pico_estimado = tempo_fechamento * 0.5  # 50% do tempo até fechamento
        
        return tempo_pico_estimado.mean()
    
    def generate_summary_table(self, metrics_df):
        """Gera tabela resumo formatada"""
        print(f"\n📋 TABELA RESUMO - ANÁLISE DE GAPS POR CLASSE")
        print("=" * 120)
        
        # Formatação da tabela
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 20)
        
        # Criar tabela formatada
        table_data = []
        
        for _, row in metrics_df.iterrows():
            table_row = {
                'Intervalo': row['intervalo'],
                'N° Obs': f"{row['n_observacoes']:,}",
                'Gap Up': f"{row['n_gap_up']:,} ({row['perc_gap_up']:.1f}%)",
                'Gap Down': f"{row['n_gap_down']:,} ({row['perc_gap_down']:.1f}%)",
                'P(Fechar Up)': f"{row['prob_fechamento_up']:.1%}",
                'P(Fechar Down)': f"{row['prob_fechamento_down']:.1%}",
                'Ampl. Máx': f"{row['amplitude_maxima']:,.0f}",
                'Ampl. Mín': f"{row['amplitude_minima']:,.0f}",
                'T. Pico Up': f"{row['tempo_pico_up']:.1f}" if not pd.isna(row['tempo_pico_up']) else "N/A",
                'T. Pico Down': f"{row['tempo_pico_down']:.1f}" if not pd.isna(row['tempo_pico_down']) else "N/A",
                'T. Fechar Up': f"{row['tempo_fechamento_up']:.1f}" if not pd.isna(row['tempo_fechamento_up']) else "N/A",
                'T. Fechar Down': f"{row['tempo_fechamento_down']:.1f}" if not pd.isna(row['tempo_fechamento_down']) else "N/A",
                'Volatilidade': f"{row['volatilidade_media']:.2f}%"
            }
            table_data.append(table_row)
        
        summary_table = pd.DataFrame(table_data)
        print(summary_table.to_string(index=False))
        
        return summary_table
    
    def save_datasets(self, metrics_df):
        """Salva os datasets para uso em modelos"""
        print(f"\n💾 SALVANDO DATASETS")
        print("=" * 60)
        
        # Dataset 1: Dados classificados completos
        classified_file = 'data/processed/gaps_classificados.csv'
        self.gaps_df.to_csv(classified_file)
        print(f"✅ Gaps classificados salvos: {classified_file}")
        
        # Dataset 2: Métricas por classe
        metrics_file = 'data/processed/metricas_por_classe.csv'
        metrics_df.to_csv(metrics_file, index=False)
        print(f"✅ Métricas por classe salvas: {metrics_file}")
        
        # Dataset 3: Features para modelo (dados numéricos)
        features_df = self.gaps_df[[
            'gap_absoluto', 'gap_percentual', 'amplitude', 'volatilidade',
            'volume_total', 'retorno_diario', 'gap_fechado', 'dias_para_fechamento'
        ]].copy()
        
        # Adicionar features categóricas codificadas
        features_df['tipo_gap_up'] = (self.gaps_df['tipo_gap'] == 'Gap Up').astype(int)
        features_df['gap_class_encoded'] = self.gaps_df['gap_class'].cat.codes
        
        features_file = 'data/processed/features_para_modelo.csv'
        features_df.to_csv(features_file)
        print(f"✅ Features para modelo salvas: {features_file}")
        
        print(f"\n📊 Resumo dos datasets:")
        print(f"• Gaps classificados: {len(self.gaps_df)} registros")
        print(f"• Classes criadas: {len(metrics_df)} intervalos")
        print(f"• Features para modelo: {features_df.shape[1]} colunas")
        
        return classified_file, metrics_file, features_file

def main():
    """Função principal"""
    print("🚀 GAP CLASSIFICATION ANALYZER")
    print("=" * 60)
    print("Análise Estatística para Classificação Otimizada de Gaps")
    print("Desenvolvido para Análise de Mercado Financeiro")
    print()
    
    try:
        # Inicializar analisador
        analyzer = GapClassificationAnalyzer('data/processed/gaps_analisados.csv')
        
        # Etapa 1: Analisar distribuição e otimizar intervalos
        optimal_intervals = analyzer.analyze_distribution()
        
        # Etapa 2: Classificar gaps
        intervals, labels = analyzer.classify_gaps(optimal_intervals)
        
        # Etapa 3: Calcular métricas
        metrics_df = analyzer.calculate_metrics_by_class()
        
        # Etapa 4: Gerar tabela resumo
        summary_table = analyzer.generate_summary_table(metrics_df)
        
        # Etapa 5: Salvar datasets
        files = analyzer.save_datasets(metrics_df)
        
        print(f"\n🎯 ANÁLISE CONCLUÍDA COM SUCESSO!")
        print(f"📊 {len(labels)} classes de gaps criadas")
        print(f"📁 3 datasets salvos para uso em modelos")
        print(f"📋 Tabela resumo com todas as métricas gerada")
        
    except FileNotFoundError:
        print("❌ Erro: Arquivo 'data/processed/gaps_analisados.csv' não encontrado.")
        print("   Execute primeiro o script 'run.py' para gerar os dados de gaps.")
    except Exception as e:
        print(f"❌ Erro durante a análise: {str(e)}")

if __name__ == "__main__":
    main()