#!/usr/bin/env python3
"""
Gap Classification Analyzer
===========================
Módulo para análise de classificação de gaps integrado ao sistema principal
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Implementação simples de K-means para evitar dependência do sklearn
class SimpleKMeans:
    def __init__(self, n_clusters=4, max_iters=100, random_state=42):
        self.n_clusters = n_clusters
        self.max_iters = max_iters
        self.random_state = random_state
        np.random.seed(random_state)
        
    def fit_predict(self, X):
        X = X.flatten()
        
        # Inicializar centroides
        min_val, max_val = X.min(), X.max()
        centroids = np.linspace(min_val, max_val, self.n_clusters)
        
        for _ in range(self.max_iters):
            # Atribuir pontos aos clusters
            distances = np.abs(X[:, np.newaxis] - centroids)
            labels = np.argmin(distances, axis=1)
            
            # Atualizar centroides
            new_centroids = np.array([X[labels == i].mean() if len(X[labels == i]) > 0 else centroids[i] 
                                    for i in range(self.n_clusters)])
            
            if np.allclose(centroids, new_centroids):
                break
                
            centroids = new_centroids
        
        self.cluster_centers_ = centroids.reshape(-1, 1)
        return labels

class GapClassificationAnalyzer:
    def __init__(self, config):
        """Inicializa o analisador com configurações"""
        self.config = config
        self.gaps_df = None
        self.metrics_df = None
        
    def executar_analise_completa(self):
        """Executa a análise completa de classificação de gaps"""
        print("\n📊 INICIANDO ANÁLISE DE CLASSIFICAÇÃO DE GAPS")
        print("=" * 60)
        
        # Carregar dados de gaps
        if not self._carregar_dados_gaps():
            return None, None
            
        # Analisar distribuição
        optimal_intervals = self._analisar_distribuicao()
        
        # Classificar gaps
        intervals, labels = self._classificar_gaps(optimal_intervals)
        
        # Calcular métricas
        self.metrics_df = self._calcular_metricas_por_classe()
        
        # Gerar visualizações
        self._gerar_graficos_classificacao()
        
        # Salvar datasets
        self._salvar_datasets()
        
        # Exibir relatório detalhado
        self._exibir_relatorio_detalhado()
        
        return self.gaps_df, self.metrics_df
    
    def _carregar_dados_gaps(self):
        """Carrega dados de gaps analisados"""
        gaps_file = f"{self.config['PROCESSED_DIR']}/gaps_analisados.csv"
        
        try:
            self.gaps_df = pd.read_csv(gaps_file, index_col=0, parse_dates=True)
            self.gaps_df = self.gaps_df[self.gaps_df['gap_absoluto'] >= self.config['GAP_MINIMO']]
            
            if len(self.gaps_df) == 0:
                print("❌ Nenhum gap significativo encontrado para classificação")
                return False
                
            print(f"✅ Dados de gaps carregados: {len(self.gaps_df)} gaps significativos")
            return True
            
        except FileNotFoundError:
            print("❌ Arquivo de gaps não encontrado. Execute primeiro a análise de gaps.")
            return False
    
    def _analisar_distribuicao(self):
        """Analisa a distribuição dos gaps"""
        print("\n🔍 ANÁLISE ESTATÍSTICA DA DISTRIBUIÇÃO")
        print("-" * 50)
        
        gaps = self.gaps_df['gap_absoluto'].values
        
        # Estatísticas básicas
        print(f"📈 Total de gaps analisados: {len(gaps):,}")
        print(f"📊 Gap mínimo: {gaps.min():.0f} pontos")
        print(f"📊 Gap máximo: {gaps.max():,.0f} pontos")
        print(f"📊 Gap médio: {gaps.mean():.1f} pontos")
        print(f"📊 Gap mediano: {np.median(gaps):.1f} pontos")
        print(f"📊 Desvio padrão: {gaps.std():.1f} pontos")
        
        # Análise de quartis
        q1, q2, q3 = np.percentile(gaps, [25, 50, 75])
        iqr = q3 - q1
        
        print(f"\n📊 ANÁLISE DE QUARTIS:")
        print(f"• Q1 (25%): {q1:.0f} pontos")
        print(f"• Q2 (50%): {q2:.0f} pontos") 
        print(f"• Q3 (75%): {q3:.0f} pontos")
        print(f"• IQR: {iqr:.0f} pontos")
        
        # Teste de normalidade
        stat, p_value = stats.normaltest(gaps)
        print(f"• Teste de normalidade: p-value = {p_value:.2e}")
        print(f"• Distribuição: {'Normal' if p_value > 0.05 else 'Não-normal'}")
        
        # Otimizar intervalos
        return self._otimizar_intervalos(gaps)
    
    def _otimizar_intervalos(self, gaps):
        """Otimiza intervalos usando métodos estatísticos"""
        print(f"\n🎯 OTIMIZAÇÃO DE INTERVALOS")
        print("-" * 50)
        
        methods = {}
        
        # Método 1: Quartis (mais balanceado)
        q1, q2, q3 = np.percentile(gaps, [25, 50, 75])
        quartil_intervals = [gaps.min(), q1, q2, q3, gaps.max()]
        methods['quartis'] = quartil_intervals
        
        # Método 2: Quantis uniformes
        percentiles = np.percentile(gaps, [0, 20, 40, 60, 80, 100])
        methods['quantis_uniformes'] = percentiles
        
        # Método 3: K-means otimizado
        optimal_k = self._encontrar_clusters_otimos(gaps)
        kmeans = SimpleKMeans(n_clusters=optimal_k, random_state=42)
        cluster_labels = kmeans.fit_predict(gaps.reshape(-1, 1))
        cluster_centers = sorted(kmeans.cluster_centers_.flatten())
        
        kmeans_intervals = [gaps.min()]
        for i in range(len(cluster_centers) - 1):
            boundary = (cluster_centers[i] + cluster_centers[i+1]) / 2
            kmeans_intervals.append(boundary)
        kmeans_intervals.append(gaps.max())
        methods['kmeans'] = kmeans_intervals
        
        # Exibir métodos
        print(f"• Quartis (4 classes): {[int(x) for x in quartil_intervals]}")
        print(f"• Quantis uniformes (5 classes): {[int(x) for x in percentiles]}")
        print(f"• K-means ({optimal_k} clusters): {[int(x) for x in kmeans_intervals]}")
        
        # Avaliar e selecionar melhor método
        best_method = self._avaliar_metodos(gaps, methods)
        print(f"\n✅ Método selecionado: {best_method.upper()}")
        
        return methods[best_method]
    
    def _encontrar_clusters_otimos(self, gaps):
        """Encontra número ótimo de clusters"""
        max_k = min(6, len(np.unique(gaps)) // 20)
        if max_k < 2:
            return 4
        
        inertias = []
        k_range = range(2, max_k + 1)
        
        for k in k_range:
            kmeans = SimpleKMeans(n_clusters=k, random_state=42)
            kmeans.fit_predict(gaps.reshape(-1, 1))
            # Calcular inércia manualmente
            labels = kmeans.fit_predict(gaps.reshape(-1, 1))
            inertia = sum(np.min(np.abs(gaps[:, np.newaxis] - kmeans.cluster_centers_.flatten())**2, axis=1))
            inertias.append(inertia)
        
        if len(inertias) >= 3:
            diffs = np.diff(inertias)
            diffs2 = np.diff(diffs)
            optimal_k = k_range[np.argmax(diffs2) + 1]
        else:
            optimal_k = 4
        
        return min(optimal_k, 5)
    
    def _avaliar_metodos(self, gaps, methods):
        """Avalia métodos usando critérios estatísticos"""
        scores = {}
        
        for method_name, intervals in methods.items():
            bins = pd.cut(gaps, bins=intervals, include_lowest=True, duplicates='drop')
            bin_counts = bins.value_counts()
            
            # Critério: distribuição balanceada
            balance_score = 1 / (bin_counts.std() / bin_counts.mean()) if bin_counts.std() > 0 else 1
            
            # Critério: observações mínimas por bin
            min_obs_score = 1 if bin_counts.min() >= 10 else bin_counts.min() / 10
            
            # Score total
            total_score = (balance_score * 0.6 + min_obs_score * 0.4)
            scores[method_name] = total_score
        
        return max(scores, key=scores.get)
    
    def _classificar_gaps(self, intervals):
        """Classifica gaps nos intervalos"""
        print(f"\n📋 CLASSIFICAÇÃO DOS GAPS EM INTERVALOS")
        print("-" * 50)
        
        # Criar labels
        labels = []
        for i in range(len(intervals) - 1):
            labels.append(f"{int(intervals[i])}-{int(intervals[i+1])}")
        
        # Classificar
        self.gaps_df['gap_class'] = pd.cut(
            self.gaps_df['gap_absoluto'],
            bins=intervals,
            labels=labels,
            include_lowest=True
        )
        
        print(f"✅ Intervalos criados: {labels}")
        print(f"✅ Gaps classificados: {len(self.gaps_df):,}")
        
        # Mostrar distribuição
        distribuicao = self.gaps_df['gap_class'].value_counts().sort_index()
        print(f"\n📊 DISTRIBUIÇÃO POR CLASSE:")
        for classe, count in distribuicao.items():
            percent = (count / len(self.gaps_df)) * 100
            print(f"   • {classe}: {count:,} gaps ({percent:.1f}%)")
        
        return intervals, labels
    
    def _calcular_metricas_por_classe(self):
        """Calcula métricas detalhadas por classe"""
        print(f"\n📈 CALCULANDO MÉTRICAS DETALHADAS POR CLASSE")
        print("-" * 50)
        
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
            
            # Amplitudes e tempos
            amplitude_max = class_data['amplitude'].max()
            amplitude_min = class_data['amplitude'].min()
            amplitude_media = class_data['amplitude'].mean()
            
            tempo_fechamento_up = gaps_fechados_up['dias_para_fechamento'].mean() if len(gaps_fechados_up) > 0 else np.nan
            tempo_fechamento_down = gaps_fechados_down['dias_para_fechamento'].mean() if len(gaps_fechados_down) > 0 else np.nan
            
            tempo_pico_up = self._calcular_tempo_pico(class_data[class_data['tipo_gap'] == 'Gap Up'])
            tempo_pico_down = self._calcular_tempo_pico(class_data[class_data['tipo_gap'] == 'Gap Down'])
            
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
                'volatilidade_media': class_data['volatilidade'].mean(),
                'gap_medio': class_data['gap_absoluto'].mean(),
                'gap_min': class_data['gap_absoluto'].min(),
                'gap_max': class_data['gap_absoluto'].max()
            }
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def _calcular_tempo_pico(self, class_data):
        """Estima tempo para pico do movimento"""
        if len(class_data) == 0:
            return np.nan
        
        gaps_with_closure = class_data[class_data['gap_fechado'] == True]
        if len(gaps_with_closure) == 0:
            return np.nan
        
        tempo_fechamento = gaps_with_closure['dias_para_fechamento']
        tempo_pico_estimado = tempo_fechamento * 0.5  # Estimativa: 50% do tempo de fechamento
        
        return tempo_pico_estimado.mean()
    
    def _gerar_graficos_classificacao(self):
        """Gera gráficos específicos da análise de classificação"""
        print(f"\n📊 GERANDO GRÁFICOS DA ANÁLISE DE CLASSIFICAÇÃO")
        print("-" * 50)
        
        # Configurar estilo
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (15, 10)
        plt.rcParams['font.size'] = 10
        
        # Gráfico 1: Distribuição dos gaps por classe
        self._plot_distribuicao_classes()
        
        # Gráfico 2: Probabilidades de fechamento
        self._plot_probabilidades_fechamento()
        
        # Gráfico 3: Tempos de fechamento por classe
        self._plot_tempos_fechamento()
        
        # Gráfico 4: Análise de volatilidade e amplitude
        self._plot_volatilidade_amplitude()
        
        print(f"✅ 4 gráficos de classificação gerados")
    
    def _plot_distribuicao_classes(self):
        """Plota distribuição dos gaps por classe"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('📊 ANÁLISE DE DISTRIBUIÇÃO DAS CLASSES DE GAPS', fontsize=16, fontweight='bold')
        
        # 1. Histograma de distribuição
        self.gaps_df['gap_absoluto'].hist(bins=30, alpha=0.7, ax=ax1, color='skyblue', edgecolor='black')
        ax1.axvline(self.gaps_df['gap_absoluto'].mean(), color='red', linestyle='--', label=f'Média: {self.gaps_df["gap_absoluto"].mean():.0f}')
        ax1.axvline(self.gaps_df['gap_absoluto'].median(), color='green', linestyle='--', label=f'Mediana: {self.gaps_df["gap_absoluto"].median():.0f}')
        ax1.set_title('Distribuição Geral dos Gaps')
        ax1.set_xlabel('Tamanho do Gap (pontos)')
        ax1.set_ylabel('Frequência')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Contagem por classe
        class_counts = self.gaps_df['gap_class'].value_counts().sort_index()
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        bars = ax2.bar(range(len(class_counts)), class_counts.values, color=colors[:len(class_counts)])
        ax2.set_title('Número de Gaps por Classe')
        ax2.set_xlabel('Classes de Gap')
        ax2.set_ylabel('Quantidade')
        ax2.set_xticks(range(len(class_counts)))
        ax2.set_xticklabels([str(idx) for idx in class_counts.index], rotation=45)
        
        # Adicionar valores nas barras
        for bar, value in zip(bars, class_counts.values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value}', ha='center', va='bottom', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # 3. Percentual por classe (pizza)
        ax3.pie(class_counts.values, labels=class_counts.index, autopct='%1.1f%%', 
                colors=colors[:len(class_counts)], startangle=90)
        ax3.set_title('Distribuição Percentual por Classe')
        
        # 4. Gap Up vs Gap Down por classe
        gap_type_data = []
        classes = []
        for gap_class in self.gaps_df['gap_class'].cat.categories:
            class_data = self.gaps_df[self.gaps_df['gap_class'] == gap_class]
            gap_up_count = len(class_data[class_data['tipo_gap'] == 'Gap Up'])
            gap_down_count = len(class_data[class_data['tipo_gap'] == 'Gap Down'])
            gap_type_data.append([gap_up_count, gap_down_count])
            classes.append(str(gap_class))
        
        gap_type_data = np.array(gap_type_data)
        x = np.arange(len(classes))
        width = 0.35
        
        ax4.bar(x - width/2, gap_type_data[:, 0], width, label='Gap Up', color='#90EE90', alpha=0.8)
        ax4.bar(x + width/2, gap_type_data[:, 1], width, label='Gap Down', color='#FFB6C1', alpha=0.8)
        ax4.set_title('Gap Up vs Gap Down por Classe')
        ax4.set_xlabel('Classes')
        ax4.set_ylabel('Quantidade')
        ax4.set_xticks(x)
        ax4.set_xticklabels(classes, rotation=45)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{self.config['OUTPUT_DIR']}/graphs/classificacao_distribuicao.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Gráfico salvo: classificacao_distribuicao.png")
    
    def _plot_probabilidades_fechamento(self):
        """Plota probabilidades de fechamento por classe"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('🎯 PROBABILIDADES DE FECHAMENTO POR CLASSE', fontsize=16, fontweight='bold')
        
        classes = self.metrics_df['intervalo'].values
        prob_up = self.metrics_df['prob_fechamento_up'].values * 100
        prob_down = self.metrics_df['prob_fechamento_down'].values * 100
        
        x = np.arange(len(classes))
        width = 0.35
        
        # Gráfico de barras
        bars1 = ax1.bar(x - width/2, prob_up, width, label='Gap Up', color='#32CD32', alpha=0.8)
        bars2 = ax1.bar(x + width/2, prob_down, width, label='Gap Down', color='#FF6347', alpha=0.8)
        
        ax1.set_title('Probabilidade de Fechamento por Tipo')
        ax1.set_xlabel('Classes de Gap')
        ax1.set_ylabel('Probabilidade (%)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(classes, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 105)
        
        # Adicionar valores nas barras
        for bar, value in zip(bars1, prob_up):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
                    
        for bar, value in zip(bars2, prob_down):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Gráfico de linha comparativo
        ax2.plot(classes, prob_up, marker='o', linewidth=2, markersize=8, label='Gap Up', color='#32CD32')
        ax2.plot(classes, prob_down, marker='s', linewidth=2, markersize=8, label='Gap Down', color='#FF6347')
        ax2.set_title('Comparação das Probabilidades')
        ax2.set_xlabel('Classes de Gap')
        ax2.set_ylabel('Probabilidade (%)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(75, 100)
        
        # Adicionar valores nos pontos
        for i, (up, down) in enumerate(zip(prob_up, prob_down)):
            ax2.annotate(f'{up:.1f}%', (i, up), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
            ax2.annotate(f'{down:.1f}%', (i, down), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(f"{self.config['OUTPUT_DIR']}/graphs/classificacao_probabilidades.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Gráfico salvo: classificacao_probabilidades.png")
    
    def _plot_tempos_fechamento(self):
        """Plota tempos de fechamento por classe"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('⏱️ ANÁLISE DE TEMPOS POR CLASSE', fontsize=16, fontweight='bold')
        
        classes = self.metrics_df['intervalo'].values
        tempo_up = self.metrics_df['tempo_fechamento_up'].values
        tempo_down = self.metrics_df['tempo_fechamento_down'].values
        tempo_pico_up = self.metrics_df['tempo_pico_up'].values
        tempo_pico_down = self.metrics_df['tempo_pico_down'].values
        
        # 1. Tempos de fechamento
        x = np.arange(len(classes))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, tempo_up, width, label='Gap Up', color='#4CAF50', alpha=0.8)
        bars2 = ax1.bar(x + width/2, tempo_down, width, label='Gap Down', color='#F44336', alpha=0.8)
        
        ax1.set_title('Tempo Médio para Fechamento')
        ax1.set_xlabel('Classes de Gap')
        ax1.set_ylabel('Dias')
        ax1.set_xticks(x)
        ax1.set_xticklabels(classes, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Adicionar valores
        for bar, value in zip(bars1, tempo_up):
            if not np.isnan(value):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{value:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
                        
        for bar, value in zip(bars2, tempo_down):
            if not np.isnan(value):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{value:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 2. Tempos para pico
        valid_up = ~np.isnan(tempo_pico_up)
        valid_down = ~np.isnan(tempo_pico_down)
        
        bars3 = ax2.bar(x[valid_up] - width/2, tempo_pico_up[valid_up], width, label='Gap Up', color='#2196F3', alpha=0.8)
        bars4 = ax2.bar(x[valid_down] + width/2, tempo_pico_down[valid_down], width, label='Gap Down', color='#FF9800', alpha=0.8)
        
        ax2.set_title('Tempo Médio para Pico')
        ax2.set_xlabel('Classes de Gap')
        ax2.set_ylabel('Dias')
        ax2.set_xticks(x)
        ax2.set_xticklabels(classes, rotation=45)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Comparação tempos (linha)
        ax3.plot(classes[valid_up], tempo_up[valid_up], marker='o', linewidth=2, markersize=8, label='Fechamento Up', color='#4CAF50')
        ax3.plot(classes[valid_down], tempo_down[valid_down], marker='s', linewidth=2, markersize=8, label='Fechamento Down', color='#F44336')
        ax3.plot(classes[valid_up], tempo_pico_up[valid_up], marker='^', linewidth=2, markersize=8, label='Pico Up', color='#2196F3', linestyle='--')
        ax3.plot(classes[valid_down], tempo_pico_down[valid_down], marker='v', linewidth=2, markersize=8, label='Pico Down', color='#FF9800', linestyle='--')
        
        ax3.set_title('Evolução dos Tempos por Classe')
        ax3.set_xlabel('Classes de Gap')
        ax3.set_ylabel('Dias')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Relação pico vs fechamento
        for i, classe in enumerate(classes):
            if not np.isnan(tempo_up[i]) and not np.isnan(tempo_pico_up[i]):
                ax4.scatter(tempo_pico_up[i], tempo_up[i], s=100, alpha=0.7, color='#4CAF50', label='Gap Up' if i == 0 else "")
            if not np.isnan(tempo_down[i]) and not np.isnan(tempo_pico_down[i]):
                ax4.scatter(tempo_pico_down[i], tempo_down[i], s=100, alpha=0.7, color='#F44336', label='Gap Down' if i == 0 else "")
        
        # Linha de referência
        max_tempo = max(np.nanmax(tempo_up), np.nanmax(tempo_down))
        ax4.plot([0, max_tempo], [0, max_tempo], 'k--', alpha=0.5, label='Linha 1:1')
        
        ax4.set_title('Relação: Tempo Pico vs Fechamento')
        ax4.set_xlabel('Tempo para Pico (dias)')
        ax4.set_ylabel('Tempo para Fechamento (dias)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{self.config['OUTPUT_DIR']}/graphs/classificacao_tempos.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Gráfico salvo: classificacao_tempos.png")
    
    def _plot_volatilidade_amplitude(self):
        """Plota análise de volatilidade e amplitude por classe"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('📊 ANÁLISE DE VOLATILIDADE E AMPLITUDE POR CLASSE', fontsize=16, fontweight='bold')
        
        classes = self.metrics_df['intervalo'].values
        volatilidade = self.metrics_df['volatilidade_media'].values
        amp_max = self.metrics_df['amplitude_maxima'].values
        amp_min = self.metrics_df['amplitude_minima'].values
        amp_media = self.metrics_df['amplitude_media'].values
        gap_medio = self.metrics_df['gap_medio'].values
        
        # 1. Volatilidade por classe
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        bars = ax1.bar(classes, volatilidade, color=colors[:len(classes)], alpha=0.8)
        ax1.set_title('Volatilidade Média por Classe')
        ax1.set_xlabel('Classes de Gap')
        ax1.set_ylabel('Volatilidade (%)')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # Adicionar valores
        for bar, value in zip(bars, volatilidade):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{value:.2f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 2. Amplitude máxima vs mínima
        x = np.arange(len(classes))
        width = 0.35
        
        ax2.bar(x - width/2, amp_max, width, label='Máxima', color='#FF4444', alpha=0.8)
        ax2.bar(x + width/2, amp_min, width, label='Mínima', color='#44FF44', alpha=0.8)
        ax2.set_title('Amplitude Máxima vs Mínima')
        ax2.set_xlabel('Classes de Gap')
        ax2.set_ylabel('Amplitude (pontos)')
        ax2.set_xticks(x)
        ax2.set_xticklabels(classes, rotation=45)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Relação gap médio vs volatilidade
        scatter = ax3.scatter(gap_medio, volatilidade, s=200, c=range(len(classes)), 
                             cmap='viridis', alpha=0.7, edgecolors='black', linewidth=2)
        
        # Adicionar labels das classes
        for i, classe in enumerate(classes):
            ax3.annotate(classe, (gap_medio[i], volatilidade[i]), 
                        textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)
        
        ax3.set_title('Gap Médio vs Volatilidade')
        ax3.set_xlabel('Gap Médio (pontos)')
        ax3.set_ylabel('Volatilidade (%)')
        ax3.grid(True, alpha=0.3)
        
        # Linha de tendência
        z = np.polyfit(gap_medio, volatilidade, 1)
        p = np.poly1d(z)
        ax3.plot(gap_medio, p(gap_medio), "r--", alpha=0.8, linewidth=2)
        
        # 4. Boxplot de amplitudes por classe
        amplitude_data = []
        for gap_class in self.gaps_df['gap_class'].cat.categories:
            class_data = self.gaps_df[self.gaps_df['gap_class'] == gap_class]
            amplitude_data.append(class_data['amplitude'].values)
        
        bp = ax4.boxplot(amplitude_data, labels=classes, patch_artist=True)
        
        # Colorir boxplots
        for patch, color in zip(bp['boxes'], colors[:len(classes)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax4.set_title('Distribuição de Amplitudes por Classe')
        ax4.set_xlabel('Classes de Gap')
        ax4.set_ylabel('Amplitude (pontos)')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{self.config['OUTPUT_DIR']}/graphs/classificacao_volatilidade.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Gráfico salvo: classificacao_volatilidade.png")
    
    def _salvar_datasets(self):
        """Salva datasets da classificação"""
        # Dataset 1: Gaps classificados
        classified_file = f"{self.config['PROCESSED_DIR']}/gaps_classificados.csv"
        self.gaps_df.to_csv(classified_file)
        
        # Dataset 2: Métricas por classe
        metrics_file = f"{self.config['PROCESSED_DIR']}/metricas_por_classe.csv"
        self.metrics_df.to_csv(metrics_file, index=False)
        
        # Dataset 3: Features para modelo
        features_df = self.gaps_df[[
            'gap_absoluto', 'gap_percentual', 'amplitude', 'volatilidade',
            'volume_total', 'retorno_diario', 'gap_fechado', 'dias_para_fechamento'
        ]].copy()
        
        features_df['tipo_gap_up'] = (self.gaps_df['tipo_gap'] == 'Gap Up').astype(int)
        features_df['gap_class_encoded'] = self.gaps_df['gap_class'].cat.codes
        
        features_file = f"{self.config['PROCESSED_DIR']}/features_para_modelo.csv"
        features_df.to_csv(features_file)
        
        print(f"✅ Datasets salvos:")
        print(f"   • {classified_file}")
        print(f"   • {metrics_file}")
        print(f"   • {features_file}")
    
    def _exibir_relatorio_detalhado(self):
        """Exibe relatório detalhado da análise"""
        print(f"\n📋 RELATÓRIO DETALHADO - ANÁLISE DE CLASSIFICAÇÃO")
        print("=" * 70)
        
        total_gaps = self.metrics_df['n_observacoes'].sum()
        total_gap_up = self.metrics_df['n_gap_up'].sum()
        total_gap_down = self.metrics_df['n_gap_down'].sum()
        
        print(f"\n📈 RESUMO GERAL:")
        print(f"   • Total de gaps classificados: {total_gaps:,}")
        print(f"   • Gaps de alta: {total_gap_up:,} ({total_gap_up/total_gaps*100:.1f}%)")
        print(f"   • Gaps de baixa: {total_gap_down:,} ({total_gap_down/total_gaps*100:.1f}%)")
        print(f"   • Classes criadas: {len(self.metrics_df)}")
        
        print(f"\n📊 MÉTRICAS POR CLASSE:")
        print("-" * 70)
        
        for idx, row in self.metrics_df.iterrows():
            print(f"\n🔹 CLASSE {row['intervalo']} pontos:")
            print(f"   📊 Observações: {row['n_observacoes']:,} ({row['n_observacoes']/total_gaps*100:.1f}%)")
            print(f"   📈 Gap Up: {row['n_gap_up']:,} ({row['perc_gap_up']:.1f}%) | Gap Down: {row['n_gap_down']:,} ({row['perc_gap_down']:.1f}%)")
            print(f"   🎯 Prob. Fechamento: Up {row['prob_fechamento_up']:.1%} | Down {row['prob_fechamento_down']:.1%}")
            print(f"   📏 Amplitude: Máx {row['amplitude_maxima']:,.0f} | Mín {row['amplitude_minima']:,.0f} | Média {row['amplitude_media']:,.0f}")
            
            if not pd.isna(row['tempo_fechamento_up']) and not pd.isna(row['tempo_fechamento_down']):
                print(f"   ⏱️  Tempo Fechamento: Up {row['tempo_fechamento_up']:.1f}d | Down {row['tempo_fechamento_down']:.1f}d")
            
            if not pd.isna(row['tempo_pico_up']) and not pd.isna(row['tempo_pico_down']):
                print(f"   ⏱️  Tempo Pico: Up {row['tempo_pico_up']:.1f}d | Down {row['tempo_pico_down']:.1f}d")
            
            print(f"   📊 Volatilidade: {row['volatilidade_media']:.2f}% | Gap Médio: {row['gap_medio']:.0f} pontos")
        
        # Insights principais
        print(f"\n🧠 INSIGHTS PRINCIPAIS:")
        print("-" * 70)
        
        # Classe com maior probabilidade
        max_prob_up = self.metrics_df.loc[self.metrics_df['prob_fechamento_up'].idxmax()]
        max_prob_down = self.metrics_df.loc[self.metrics_df['prob_fechamento_down'].idxmax()]
        
        print(f"✅ Maior prob. fechamento Gap Up: {max_prob_up['intervalo']} ({max_prob_up['prob_fechamento_up']:.1%})")
        print(f"✅ Maior prob. fechamento Gap Down: {max_prob_down['intervalo']} ({max_prob_down['prob_fechamento_down']:.1%})")
        
        # Tempos mais rápidos
        tempo_up_validos = self.metrics_df[~pd.isna(self.metrics_df['tempo_fechamento_up'])]
        tempo_down_validos = self.metrics_df[~pd.isna(self.metrics_df['tempo_fechamento_down'])]
        
        if len(tempo_up_validos) > 0:
            min_tempo_up = tempo_up_validos.loc[tempo_up_validos['tempo_fechamento_up'].idxmin()]
            print(f"⚡ Fechamento mais rápido Gap Up: {min_tempo_up['intervalo']} ({min_tempo_up['tempo_fechamento_up']:.1f} dias)")
        
        if len(tempo_down_validos) > 0:
            min_tempo_down = tempo_down_validos.loc[tempo_down_validos['tempo_fechamento_down'].idxmin()]
            print(f"⚡ Fechamento mais rápido Gap Down: {min_tempo_down['intervalo']} ({min_tempo_down['tempo_fechamento_down']:.1f} dias)")
        
        # Volatilidade
        max_vol = self.metrics_df.loc[self.metrics_df['volatilidade_media'].idxmax()]
        min_vol = self.metrics_df.loc[self.metrics_df['volatilidade_media'].idxmin()]
        
        print(f"📈 Maior volatilidade: {max_vol['intervalo']} ({max_vol['volatilidade_media']:.2f}%)")
        print(f"📉 Menor volatilidade: {min_vol['intervalo']} ({min_vol['volatilidade_media']:.2f}%)")
        
        print(f"\n💡 RECOMENDAÇÕES PARA TRADING:")
        print("-" * 70)
        print("• Gaps pequenos: Estratégia de reversão rápida (alta probabilidade, baixo risco)")
        print("• Gaps médios: Estratégia balanceada (boa probabilidade, risco moderado)")
        print("• Gaps grandes: Estratégia de longo prazo (alta volatilidade, maior tempo)")
        print("• Use stops baseados na amplitude máxima histórica de cada classe")
        print("• Monitore tempos de pico para otimizar entrada/saída")