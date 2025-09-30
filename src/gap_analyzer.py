"""
Gap Analyzer Module
Módulo responsável pela análise de gaps de abertura e fechamento
"""

import pandas as pd
import numpy as np

class GapAnalyzer:
    """Classe para análise completa de gaps de abertura"""
    
    def __init__(self, config):
        self.config = config
        self.gaps_detectados = None
    
    def calcular_gaps(self, dados):
        """Calcula gaps de abertura entre sessões"""
        print(f"🔍 Calculando gaps de abertura...")
        
        dados = dados.copy().sort_index()
        
        # Calcular gaps
        dados['fechamento_anterior'] = dados['fechamento'].shift(1)
        dados['gap_abertura'] = dados['abertura'] - dados['fechamento_anterior']
        dados['gap_absoluto'] = abs(dados['gap_abertura'])
        dados['gap_percentual'] = (dados['gap_abertura'] / dados['fechamento_anterior']) * 100
        
        # Classificar tipos de gap
        gap_minimo = self.config['GAP_MINIMO']
        dados['tipo_gap'] = np.where(
            dados['gap_abertura'] > gap_minimo, 'Gap Up',
            np.where(dados['gap_abertura'] < -gap_minimo, 'Gap Down', 'Sem Gap')
        )
        
        # Remover primeiro registro (sem gap anterior)
        dados = dados.dropna(subset=['fechamento_anterior'])
        
        print(f"✅ Gaps calculados para {len(dados)} dias")
        return dados
    
    def filtrar_gaps_significativos(self, dados):
        """Filtra apenas gaps significativos baseado na configuração"""
        gap_minimo = self.config['GAP_MINIMO']
        
        gaps_significativos = dados[dados['gap_absoluto'] >= gap_minimo].copy()
        
        if len(gaps_significativos) == 0:
            print(f"❌ Nenhum gap >= {gap_minimo} pontos encontrado")
            return None
        
        print(f"📊 {len(gaps_significativos)} gaps significativos encontrados (>= {gap_minimo} pontos)")
        
        # Estatísticas básicas dos gaps
        gap_up = gaps_significativos[gaps_significativos['tipo_gap'] == 'Gap Up']
        gap_down = gaps_significativos[gaps_significativos['tipo_gap'] == 'Gap Down']
        
        print(f"   • Gap Up: {len(gap_up)} ({len(gap_up)/len(gaps_significativos)*100:.1f}%)")
        print(f"   • Gap Down: {len(gap_down)} ({len(gap_down)/len(gaps_significativos)*100:.1f}%)")
        print(f"   • Gap médio: {gaps_significativos['gap_absoluto'].mean():.1f} pontos")
        print(f"   • Maior gap: {gaps_significativos['gap_absoluto'].max():.0f} pontos")
        
        return gaps_significativos
    
    def verificar_fechamento_gaps(self, gaps_significativos, dados_completos):
        """Verifica se os gaps foram fechados nos dias subsequentes"""
        print(f"🔄 Verificando fechamento de gaps (limite: {self.config['DIAS_LIMITE_GAP']} dias)")
        
        gaps_com_fechamento = gaps_significativos.copy()
        gaps_com_fechamento['gap_fechado'] = False
        gaps_com_fechamento['dias_para_fechamento'] = np.nan
        gaps_com_fechamento['preco_fechamento'] = np.nan
        gaps_com_fechamento['data_fechamento'] = pd.NaT
        
        for idx, gap in gaps_significativos.iterrows():
            gap_valor = gap['gap_abertura']
            fechamento_anterior = gap['fechamento_anterior']
            
            # Definir critério de fechamento baseado no tipo de gap
            if gap_valor > 0:  # Gap Up
                nivel_fechamento = fechamento_anterior
                # Procurar quando o preço voltou ao nível anterior (mínima <= nível)
                dados_futuros = dados_completos[dados_completos.index > idx][:self.config['DIAS_LIMITE_GAP']]
                condicao_fechamento = dados_futuros['minima'] <= nivel_fechamento
            else:  # Gap Down
                nivel_fechamento = fechamento_anterior
                # Procurar quando o preço voltou ao nível anterior (máxima >= nível)
                dados_futuros = dados_completos[dados_completos.index > idx][:self.config['DIAS_LIMITE_GAP']]
                condicao_fechamento = dados_futuros['maxima'] >= nivel_fechamento
            
            # Verificar se gap foi fechado
            dias_com_fechamento = dados_futuros[condicao_fechamento]
            
            if len(dias_com_fechamento) > 0:
                primeira_data_fechamento = dias_com_fechamento.index[0]
                dias_para_fechar = (primeira_data_fechamento - idx).days
                
                gaps_com_fechamento.loc[idx, 'gap_fechado'] = True
                gaps_com_fechamento.loc[idx, 'dias_para_fechamento'] = dias_para_fechar
                gaps_com_fechamento.loc[idx, 'preco_fechamento'] = nivel_fechamento
                gaps_com_fechamento.loc[idx, 'data_fechamento'] = primeira_data_fechamento
        
        # Estatísticas de fechamento
        total_gaps = len(gaps_com_fechamento)
        gaps_fechados = gaps_com_fechamento['gap_fechado'].sum()
        taxa_fechamento = gaps_fechados / total_gaps * 100
        
        print(f"✅ Análise de fechamento concluída:")
        print(f"   • Total analisado: {total_gaps} gaps")
        print(f"   • Gaps fechados: {gaps_fechados} ({taxa_fechamento:.1f}%)")
        print(f"   • Gaps não fechados: {total_gaps - gaps_fechados}")
        
        return gaps_com_fechamento
    
    def analisar_tempo_fechamento(self, gaps_com_fechamento):
        """Analisa estatísticas do tempo para fechamento dos gaps"""
        gaps_fechados = gaps_com_fechamento[gaps_com_fechamento['gap_fechado'] == True]
        
        if len(gaps_fechados) == 0:
            print("❌ Nenhum gap fechado para análise de tempo")
            return
        
        print(f"\n⏱️  ANÁLISE DO TEMPO PARA FECHAMENTO")
        print("-" * 50)
        
        tempo_medio = gaps_fechados['dias_para_fechamento'].mean()
        tempo_mediano = gaps_fechados['dias_para_fechamento'].median()
        tempo_min = gaps_fechados['dias_para_fechamento'].min()
        tempo_max = gaps_fechados['dias_para_fechamento'].max()
        
        print(f"• Tempo médio: {tempo_medio:.1f} dias")
        print(f"• Tempo mediano: {tempo_mediano:.1f} dias")
        print(f"• Fechamento mais rápido: {tempo_min:.0f} dia(s)")
        print(f"• Fechamento mais lento: {tempo_max:.0f} dias")
        
        # Análise por tipo de gap
        for tipo in ['Gap Up', 'Gap Down']:
            subset = gaps_fechados[gaps_fechados['tipo_gap'] == tipo]
            if len(subset) > 0:
                tempo_medio_tipo = subset['dias_para_fechamento'].mean()
                print(f"• {tipo} - tempo médio: {tempo_medio_tipo:.1f} dias")
        
        # Distribuição de tempos
        print(f"\n📊 DISTRIBUIÇÃO DE TEMPOS:")
        bins = [0, 1, 3, 7, 15, 30]
        labels = ['1 dia', '2-3 dias', '4-7 dias', '8-15 dias', '16-30 dias']
        
        for i, (bin_start, bin_end) in enumerate(zip(bins[:-1], bins[1:])):
            if i == 0:
                count = (gaps_fechados['dias_para_fechamento'] <= bin_end).sum()
            else:
                count = ((gaps_fechados['dias_para_fechamento'] > bin_start) & 
                        (gaps_fechados['dias_para_fechamento'] <= bin_end)).sum()
            
            pct = count / len(gaps_fechados) * 100
            print(f"   • {labels[i]}: {count} gaps ({pct:.1f}%)")
    
    def analisar_por_tipo_gap(self, gaps_com_fechamento):
        """Analisa estatísticas separadas por tipo de gap"""
        print(f"\n📈 ANÁLISE POR TIPO DE GAP")
        print("-" * 50)
        
        for tipo in ['Gap Up', 'Gap Down']:
            subset = gaps_com_fechamento[gaps_com_fechamento['tipo_gap'] == tipo]
            
            if len(subset) == 0:
                continue
            
            gaps_fechados_tipo = subset['gap_fechado'].sum()
            taxa_fechamento = gaps_fechados_tipo / len(subset) * 100
            gap_medio = subset['gap_absoluto'].mean()
            gap_maximo = subset['gap_absoluto'].max()
            
            print(f"\n{tipo}:")
            print(f"   • Quantidade total: {len(subset)}")
            print(f"   • Fechados: {gaps_fechados_tipo} ({taxa_fechamento:.1f}%)")
            print(f"   • Gap médio: {gap_medio:.1f} pontos")
            print(f"   • Maior gap: {gap_maximo:.0f} pontos")
            
            # Tempo médio para fechamento (apenas fechados)
            fechados_tipo = subset[subset['gap_fechado'] == True]
            if len(fechados_tipo) > 0:
                tempo_medio = fechados_tipo['dias_para_fechamento'].mean()
                print(f"   • Tempo médio fechamento: {tempo_medio:.1f} dias")
    
    def filtrar_dados_sem_gaps_abertos(self, dados_originais, gaps_com_fechamento):
        """Remove dias com gaps que não fecharam do dataset"""
        gaps_nao_fechados = gaps_com_fechamento[~gaps_com_fechamento['gap_fechado']]
        
        if len(gaps_nao_fechados) == 0:
            print("✅ Todos os gaps foram fechados - nenhuma remoção necessária")
            return dados_originais
        
        print(f"\n🗑️  REMOVENDO GAPS NÃO FECHADOS")
        print("-" * 50)
        
        # Índices dos gaps não fechados
        indices_remover = gaps_nao_fechados.index
        
        print(f"• Gaps não fechados: {len(indices_remover)}")
        print(f"• Datas: {[data.strftime('%d/%m/%Y') for data in indices_remover[:5]]}")
        if len(indices_remover) > 5:
            print(f"  ... e mais {len(indices_remover) - 5} datas")
        
        # Remover do dataset original
        dados_limpos = dados_originais.drop(indices_remover)
        
        reducao_pct = len(indices_remover) / len(dados_originais) * 100
        
        print(f"• Dados antes: {len(dados_originais)} dias")
        print(f"• Dados depois: {len(dados_limpos)} dias")
        print(f"• Redução: {len(indices_remover)} dias ({reducao_pct:.1f}%)")
        
        return dados_limpos
    
    def salvar_analise_gaps(self, gaps_com_fechamento, dados_finais):
        """Salva os resultados da análise de gaps"""
        try:
            # Salvar análise completa dos gaps
            caminho_gaps = f"{self.config['PROCESSED_DIR']}/gaps_analisados.csv"
            gaps_com_fechamento.to_csv(caminho_gaps)
            
            # Salvar dados finais sem gaps abertos
            caminho_dados_limpos = f"{self.config['PROCESSED_DIR']}/dados_limpos_finais.csv"
            dados_finais.to_csv(caminho_dados_limpos)
            
            print(f"💾 Análise de gaps salva: {caminho_gaps}")
            print(f"💾 Dados finais salvos: {caminho_dados_limpos}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar análise de gaps: {e}")
            return False
    
    def analisar_gaps(self, dados_sem_outliers):
        """Método principal para análise completa de gaps"""
        print("\n📈 INICIANDO ANÁLISE DE GAPS")
        print("=" * 50)
        
        if dados_sem_outliers is None or len(dados_sem_outliers) == 0:
            print("❌ Dados não disponíveis para análise de gaps")
            return None, dados_sem_outliers
        
        # 1. Calcular gaps
        dados_com_gaps = self.calcular_gaps(dados_sem_outliers)
        
        # 2. Filtrar gaps significativos
        gaps_significativos = self.filtrar_gaps_significativos(dados_com_gaps)
        
        if gaps_significativos is None:
            print("❌ Nenhum gap significativo encontrado")
            return None, dados_sem_outliers
        
        # 3. Verificar fechamento dos gaps
        gaps_com_fechamento = self.verificar_fechamento_gaps(gaps_significativos, dados_com_gaps)
        
        # 4. Análises estatísticas
        self.analisar_tempo_fechamento(gaps_com_fechamento)
        self.analisar_por_tipo_gap(gaps_com_fechamento)
        
        # 5. Filtrar dados finais (remover gaps não fechados)
        dados_finais = self.filtrar_dados_sem_gaps_abertos(dados_sem_outliers, gaps_com_fechamento)
        
        # 6. Salvar resultados
        self.salvar_analise_gaps(gaps_com_fechamento, dados_finais)
        
        # Armazenar para uso posterior
        self.gaps_detectados = gaps_com_fechamento
        
        print(f"\n✅ Análise de gaps concluída!")
        print(f"📊 Gaps analisados: {len(gaps_com_fechamento)}")
        print(f"📊 Dados finais: {len(dados_finais)} dias")
        
        return gaps_com_fechamento, dados_finais