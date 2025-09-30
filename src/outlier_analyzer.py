"""
Outlier Analyzer Module
Módulo responsável pela detecção e tratamento de outliers nos dados
"""

import pandas as pd
import numpy as np
from scipy import stats

class OutlierAnalyzer:
    """Classe para análise e tratamento de outliers"""
    
    def __init__(self, config):
        self.config = config
        self.outliers_detectados = None
    
    def detectar_outliers_iqr(self, dados, colunas_analise=None):
        """Detecta outliers usando método IQR (Interquartile Range)"""
        if colunas_analise is None:
            colunas_analise = ['amplitude', 'retorno_diario', 'volatilidade', 'volume_total']
        
        print(f"🔍 Detectando outliers usando método IQR (threshold: {self.config['OUTLIER_THRESHOLD']})")
        
        outliers_indices = set()
        outliers_por_coluna = {}
        
        for coluna in colunas_analise:
            if coluna not in dados.columns:
                print(f"⚠️  Coluna '{coluna}' não encontrada, ignorando...")
                continue
            
            # Calcular quartis e IQR
            Q1 = dados[coluna].quantile(0.25)
            Q3 = dados[coluna].quantile(0.75)
            IQR = Q3 - Q1
            
            # Definir limites
            limite_inferior = Q1 - self.config['OUTLIER_THRESHOLD'] * IQR
            limite_superior = Q3 + self.config['OUTLIER_THRESHOLD'] * IQR
            
            # Identificar outliers
            outliers_coluna = dados[
                (dados[coluna] < limite_inferior) | 
                (dados[coluna] > limite_superior)
            ].index
            
            outliers_por_coluna[coluna] = {
                'indices': list(outliers_coluna),
                'quantidade': len(outliers_coluna),
                'percentual': len(outliers_coluna) / len(dados) * 100,
                'limite_inferior': limite_inferior,
                'limite_superior': limite_superior
            }
            
            outliers_indices.update(outliers_coluna)
            print(f"   • {coluna}: {len(outliers_coluna)} outliers ({len(outliers_coluna)/len(dados)*100:.1f}%)")
        
        self.outliers_detectados = outliers_por_coluna
        return outliers_indices
    
    def detectar_outliers_zscore(self, dados, colunas_analise=None, threshold=3):
        """Detecta outliers usando Z-Score"""
        if colunas_analise is None:
            colunas_analise = ['amplitude', 'retorno_diario', 'volatilidade', 'volume_total']
        
        print(f"🔍 Detectando outliers usando Z-Score (threshold: {threshold})")
        
        outliers_indices = set()
        
        for coluna in colunas_analise:
            if coluna not in dados.columns:
                continue
                
            # Calcular Z-scores
            z_scores = np.abs(stats.zscore(dados[coluna].dropna()))
            outliers_coluna = dados.iloc[np.where(z_scores > threshold)[0]].index
            
            outliers_indices.update(outliers_coluna)
            print(f"   • {coluna}: {len(outliers_coluna)} outliers")
        
        return outliers_indices
    
    def analisar_impacto_remocao(self, dados_originais, outliers_indices):
        """Analisa o impacto da remoção de outliers nas estatísticas"""
        print(f"\n🔬 ANÁLISE DE IMPACTO DA REMOÇÃO DE OUTLIERS")
        print("-" * 50)
        
        dados_sem_outliers = dados_originais.drop(outliers_indices)
        
        # Métricas para comparação
        metricas = ['retorno_diario', 'volatilidade', 'amplitude', 'volume_total']
        
        impactos = {}
        
        for metrica in metricas:
            if metrica not in dados_originais.columns:
                continue
                
            # Estatísticas originais vs sem outliers
            original_mean = dados_originais[metrica].mean()
            original_std = dados_originais[metrica].std()
            
            sem_outliers_mean = dados_sem_outliers[metrica].mean()
            sem_outliers_std = dados_sem_outliers[metrica].std()
            
            # Calcular mudanças percentuais
            mudanca_media = abs(sem_outliers_mean - original_mean) / abs(original_mean) * 100 if original_mean != 0 else 0
            mudanca_std = abs(sem_outliers_std - original_std) / abs(original_std) * 100 if original_std != 0 else 0
            
            impactos[metrica] = {
                'original_mean': original_mean,
                'sem_outliers_mean': sem_outliers_mean,
                'mudanca_media': mudanca_media,
                'original_std': original_std,
                'sem_outliers_std': sem_outliers_std,
                'mudanca_std': mudanca_std
            }
            
            print(f"\n📊 {metrica.upper()}:")
            print(f"   • Média original: {original_mean:.4f}")
            print(f"   • Média sem outliers: {sem_outliers_mean:.4f}")
            print(f"   • Mudança na média: {mudanca_media:.2f}%")
            print(f"   • Mudança no desvio: {mudanca_std:.2f}%")
        
        return impactos, dados_sem_outliers
    
    def decidir_remocao_outliers(self, dados_originais, outliers_indices):
        """Decide se deve remover outliers baseado em critérios estatísticos"""
        outliers_pct = len(outliers_indices) / len(dados_originais) * 100
        
        print(f"\n📊 DECISÃO SOBRE REMOÇÃO DE OUTLIERS")
        print("-" * 50)
        print(f"• Total de outliers: {len(outliers_indices)} ({outliers_pct:.1f}% dos dados)")
        
        # Critérios para decisão
        LIMITE_PERCENTUAL = 5.0  # Se > 5% são outliers, manter
        LIMITE_IMPACTO = 10.0    # Se impacto > 10% nas métricas, manter
        
        # Analisar impacto
        impactos, dados_sem_outliers = self.analisar_impacto_remocao(dados_originais, outliers_indices)
        
        # Verificar se alguma métrica tem impacto alto
        impacto_alto = any(
            impactos[metrica]['mudanca_media'] > LIMITE_IMPACTO 
            for metrica in impactos
        )
        
        if outliers_pct <= LIMITE_PERCENTUAL and not impacto_alto:
            decisao = "REMOVER"
            dados_finais = dados_sem_outliers
            print(f"\n✅ DECISÃO: REMOVER outliers")
            print(f"   • Percentual baixo ({outliers_pct:.1f}% < {LIMITE_PERCENTUAL}%)")
            print(f"   • Impacto estatístico aceitável")
        else:
            decisao = "MANTER"
            dados_finais = dados_originais
            print(f"\n⚠️  DECISÃO: MANTER outliers")
            if outliers_pct > LIMITE_PERCENTUAL:
                print(f"   • Percentual alto ({outliers_pct:.1f}% > {LIMITE_PERCENTUAL}%)")
            if impacto_alto:
                print(f"   • Impacto estatístico significativo")
        
        return decisao, dados_finais
    
    def salvar_analise_outliers(self, dados_finais, outliers_indices, decisao):
        """Salva os resultados da análise de outliers"""
        try:
            # Salvar dados finais
            caminho_dados = f"{self.config['PROCESSED_DIR']}/dados_sem_outliers.csv"
            dados_finais.to_csv(caminho_dados)
            
            # Salvar relatório de outliers
            caminho_relatorio = f"{self.config['OUTPUT_DIR']}/reports/analise_outliers.txt"
            
            with open(caminho_relatorio, 'w', encoding='utf-8') as f:
                f.write("RELATÓRIO DE ANÁLISE DE OUTLIERS\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"Método utilizado: IQR (Interquartile Range)\n")
                f.write(f"Threshold: {self.config['OUTLIER_THRESHOLD']}\n")
                f.write(f"Total de outliers detectados: {len(outliers_indices)}\n")
                f.write(f"Decisão: {decisao}\n\n")
                
                if self.outliers_detectados:
                    f.write("OUTLIERS POR COLUNA:\n")
                    f.write("-" * 30 + "\n")
                    for coluna, info in self.outliers_detectados.items():
                        f.write(f"{coluna}:\n")
                        f.write(f"  - Quantidade: {info['quantidade']}\n")
                        f.write(f"  - Percentual: {info['percentual']:.2f}%\n")
                        f.write(f"  - Limite inferior: {info['limite_inferior']:.4f}\n")
                        f.write(f"  - Limite superior: {info['limite_superior']:.4f}\n\n")
            
            print(f"💾 Análise de outliers salva: {caminho_relatorio}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar análise de outliers: {e}")
            return False
    
    def analisar_outliers(self, dados_diarios):
        """Método principal para análise completa de outliers"""
        print("\n🔍 INICIANDO ANÁLISE DE OUTLIERS")
        print("=" * 50)
        
        if dados_diarios is None or len(dados_diarios) == 0:
            print("❌ Dados diários não disponíveis para análise de outliers")
            return dados_diarios
        
        # 1. Detectar outliers
        outliers_indices = self.detectar_outliers_iqr(dados_diarios)
        
        if len(outliers_indices) == 0:
            print("✅ Nenhum outlier detectado")
            return dados_diarios
        
        # 2. Analisar impacto e decidir
        decisao, dados_finais = self.decidir_remocao_outliers(dados_diarios, outliers_indices)
        
        # 3. Salvar resultados
        self.salvar_analise_outliers(dados_finais, outliers_indices, decisao)
        
        print(f"\n✅ Análise de outliers concluída!")
        print(f"📊 Dados finais: {len(dados_finais)} registros")
        
        return dados_finais