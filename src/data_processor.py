"""
Data Processor Module
Módulo responsável pelo carregamento e agregação dos dados de minuto para diário
"""

import pandas as pd
import numpy as np
import os

class DataProcessor:
    """Classe para processamento e agregação de dados financeiros"""
    
    def __init__(self, config):
        self.config = config
        self.dados_originais = None
        self.dados_diarios = None
    
    def carregar_dados_brutos(self):
        """Carrega os dados originais do arquivo CSV"""
        try:
            print(f"📥 Carregando dados de: {self.config['DATA_FILE']}")
            
            # Carregar dados brutos
            dados_brutos = pd.read_csv(self.config['DATA_FILE'], sep='\t')
            
            # Verificar estrutura do arquivo
            colunas_esperadas = ['<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<TICKVOL>', '<VOL>', '<SPREAD>']
            
            if not all(col in dados_brutos.columns for col in colunas_esperadas):
                raise ValueError("Estrutura do arquivo CSV não está conforme esperado")
            
            print(f"✅ {len(dados_brutos):,} registros carregados")
            return dados_brutos
            
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {self.config['DATA_FILE']}")
            return None
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return None
    
    def processar_dados(self, dados_brutos):
        """Processa e limpa os dados brutos"""
        print("🔄 Processando dados...")
        
        # Renomear colunas para português
        mapeamento_colunas = {
            '<DATE>': 'data',
            '<TIME>': 'hora',
            '<OPEN>': 'abertura', 
            '<HIGH>': 'maxima',
            '<LOW>': 'minima',
            '<CLOSE>': 'fechamento',
            '<TICKVOL>': 'volume_ticks',
            '<VOL>': 'volume',
            '<SPREAD>': 'spread'
        }
        
        dados = dados_brutos.rename(columns=mapeamento_colunas)
        
        # Converter tipos de dados
        try:
            dados['data_clean'] = pd.to_datetime(dados['data'], format='%Y.%m.%d')
            
            # Converter colunas numéricas
            colunas_numericas = ['abertura', 'maxima', 'minima', 'fechamento', 'volume', 'volume_ticks', 'spread']
            dados[colunas_numericas] = dados[colunas_numericas].astype(float)
            
        except Exception as e:
            print(f"❌ Erro na conversão de tipos: {e}")
            return None
        
        print(f"✅ Dados processados: {len(dados)} registros")
        return dados
    
    def agregar_por_dia(self, dados_processados):
        """Agrega dados de minuto para diário"""
        print("📊 Agregando dados por dia...")
        
        try:
            # Definir agregações
            agregacoes = {
                'abertura': 'first',    # Primeira abertura do dia
                'maxima': 'max',        # Máxima do dia
                'minima': 'min',        # Mínima do dia
                'fechamento': 'last',   # Último fechamento do dia
                'volume': ['sum', 'mean', 'std'],  # Volume: soma, média, desvio
                'volume_ticks': ['sum', 'mean'],
                'spread': ['mean', 'min', 'max']
            }
            
            # Agrupar por data
            dados_agrupados = dados_processados.groupby('data_clean').agg(agregacoes)
            
            # Simplificar nomes das colunas
            dados_agrupados.columns = [
                'abertura', 'maxima', 'minima', 'fechamento',
                'volume_total', 'volume_medio', 'volume_desvio',
                'volume_ticks_total', 'volume_ticks_medio',
                'spread_medio', 'spread_minimo', 'spread_maximo'
            ]
            
            # Calcular métricas adicionais
            dados_agrupados['amplitude'] = dados_agrupados['maxima'] - dados_agrupados['minima']
            dados_agrupados['retorno_diario'] = dados_agrupados['fechamento'].pct_change()
            dados_agrupados['corpo_candle'] = abs(dados_agrupados['fechamento'] - dados_agrupados['abertura'])
            dados_agrupados['volatilidade'] = dados_agrupados['amplitude'] / dados_agrupados['abertura'] * 100
            
            # Classificar tipo de dia
            dados_agrupados['tipo_dia'] = np.where(
                dados_agrupados['fechamento'] > dados_agrupados['abertura'], 
                'Alta', 'Baixa'
            )
            
            # Remover NaN do primeiro retorno
            dados_agrupados = dados_agrupados.dropna()
            
            print(f"✅ Agregação concluída: {len(dados_agrupados)} dias")
            return dados_agrupados
            
        except Exception as e:
            print(f"❌ Erro na agregação: {e}")
            return None
    
    def salvar_dados_diarios(self, dados_diarios):
        """Salva os dados diários processados"""
        try:
            caminho_saida = f"{self.config['PROCESSED_DIR']}/dados_diarios.csv"
            dados_diarios.to_csv(caminho_saida)
            print(f"💾 Dados diários salvos: {caminho_saida}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar dados diários: {e}")
            return False
    
    def exibir_estatisticas_basicas(self, dados_diarios):
        """Exibe estatísticas básicas dos dados processados"""
        print("\n📊 ESTATÍSTICAS BÁSICAS DOS DADOS DIÁRIOS")
        print("-" * 50)
        
        print(f"📅 Período: {dados_diarios.index.min().strftime('%d/%m/%Y')} até {dados_diarios.index.max().strftime('%d/%m/%Y')}")
        print(f"📊 Total de dias: {len(dados_diarios)}")
        
        print(f"\n💰 PREÇOS:")
        print(f"   • Fechamento médio: {dados_diarios['fechamento'].mean():,.2f}")
        print(f"   • Maior máxima: {dados_diarios['maxima'].max():,.0f}")
        print(f"   • Menor mínima: {dados_diarios['minima'].min():,.0f}")
        print(f"   • Amplitude média: {dados_diarios['amplitude'].mean():,.2f}")
        print(f"   • Volatilidade média: {dados_diarios['volatilidade'].mean():.2f}%")
        
        print(f"\n📊 RETORNOS:")
        print(f"   • Retorno médio diário: {dados_diarios['retorno_diario'].mean()*100:.3f}%")
        print(f"   • Maior ganho: {dados_diarios['retorno_diario'].max()*100:.2f}%")
        print(f"   • Maior perda: {dados_diarios['retorno_diario'].min()*100:.2f}%")
        print(f"   • Volatilidade dos retornos: {dados_diarios['retorno_diario'].std()*100:.2f}%")
        
        print(f"\n📈 DISTRIBUIÇÃO:")
        tipo_dias = dados_diarios['tipo_dia'].value_counts()
        for tipo, count in tipo_dias.items():
            print(f"   • Dias de {tipo}: {count} ({count/len(dados_diarios)*100:.1f}%)")
    
    def carregar_e_agregar_dados(self):
        """Método principal que executa todo o pipeline de processamento"""
        print("\n📊 INICIANDO PROCESSAMENTO DE DADOS")
        print("=" * 50)
        
        # 1. Carregar dados brutos
        dados_brutos = self.carregar_dados_brutos()
        if dados_brutos is None:
            return None
        
        # 2. Processar dados
        dados_processados = self.processar_dados(dados_brutos)
        if dados_processados is None:
            return None
        
        # 3. Agregar por dia
        dados_diarios = self.agregar_por_dia(dados_processados)
        if dados_diarios is None:
            return None
        
        # 4. Salvar dados processados
        self.salvar_dados_diarios(dados_diarios)
        
        # 5. Exibir estatísticas
        self.exibir_estatisticas_basicas(dados_diarios)
        
        # Armazenar para uso posterior
        self.dados_diarios = dados_diarios
        
        print("\n✅ Processamento de dados concluído com sucesso!")
        return dados_diarios