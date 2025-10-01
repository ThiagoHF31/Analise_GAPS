#!/usr/bin/env python3
"""
WIN$N Financial Data Analyzer
Main execution file - Run this to perform complete analysis

Análise Completa de Dados Financeiros WIN$N M1
Arquivo principal - Execute este para realizar toda a análise
"""

import sys
import os
import subprocess
import importlib

# Configurações principais
CONFIG = {
    'GAP_MINIMO': 100,           # Gap mínimo em pontos para análise
    'OUTLIER_THRESHOLD': 1.5,    # Multiplicador IQR para outliers  
    'DIAS_LIMITE_GAP': 30,       # Dias para verificar fechamento de gap
    'DATA_FILE': 'data/WIN$N_M1.csv',
    'OUTPUT_DIR': 'output',
    'PROCESSED_DIR': 'data/processed'
}

def install_requirements():
    """Instala dependências necessárias automaticamente"""
    required_packages = [
        'pandas',
        'numpy', 
        'matplotlib',
        'scipy'
    ]
    
    print("🔧 Verificando dependências...")
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"📦 Instalando {package}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} - Instalado com sucesso")
            except subprocess.CalledProcessError:
                print(f"❌ Erro ao instalar {package}")
                sys.exit(1)
    
    print("✅ Todas as dependências estão prontas!\n")

def check_data_file():
    """Verifica se o arquivo de dados existe"""
    if not os.path.exists(CONFIG['DATA_FILE']):
        print("❌ ERRO: Arquivo de dados não encontrado!")
        print(f"📁 Esperado: {CONFIG['DATA_FILE']}")
        print("\n💡 Solução:")
        print("   1. Certifique-se de que o arquivo WIN$N_M1.csv está na pasta 'data/'")
        print("   2. Verifique se o nome do arquivo está correto")
        sys.exit(1)
    
    # Verificar tamanho do arquivo
    file_size = os.path.getsize(CONFIG['DATA_FILE']) / (1024 * 1024)  # MB
    print(f"📊 Arquivo de dados encontrado: {file_size:.1f} MB")

def create_directories():
    """Cria diretórios necessários se não existirem"""
    directories = [
        CONFIG['OUTPUT_DIR'],
        CONFIG['PROCESSED_DIR'],
        f"{CONFIG['OUTPUT_DIR']}/graphs",
        f"{CONFIG['OUTPUT_DIR']}/reports"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """Função principal que executa toda a análise"""
    print("🚀 WIN$N FINANCIAL DATA ANALYZER")
    print("=" * 50)
    print("Análise Completa de Dados Financeiros")
    print("Desenvolvido para o Mercado Brasileiro\n")
    
    # 1. Preparação do ambiente
    install_requirements()
    check_data_file()
    create_directories()
    
    # Importar módulos após instalar dependências
    try:
        from src.data_processor import DataProcessor
        from src.outlier_analyzer import OutlierAnalyzer  
        from src.gap_analyzer import GapAnalyzer
        from src.gap_classification_analyzer import GapClassificationAnalyzer
        from src.visualizer import Visualizer
        from src.report_generator import ReportGenerator
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("💡 Certifique-se de que todos os arquivos estão na pasta 'src/'")
        sys.exit(1)
    
    print("📥 Iniciando análise dos dados...")
    
    try:
        # 2. Processamento dos dados
        print("\n📊 ETAPA 1: Processamento e Agregação de Dados")
        processor = DataProcessor(CONFIG)
        dados_diarios = processor.carregar_e_agregar_dados()
        
        if dados_diarios is None:
            print("❌ Erro no processamento dos dados")
            return
        
        # 3. Análise de outliers
        print("\n🔍 ETAPA 2: Análise de Outliers")
        outlier_analyzer = OutlierAnalyzer(CONFIG)
        dados_sem_outliers = outlier_analyzer.analisar_outliers(dados_diarios)
        
        # 4. Análise de gaps
        print("\n📈 ETAPA 3: Análise de Gaps")
        gap_analyzer = GapAnalyzer(CONFIG)
        dados_gaps, dados_finais = gap_analyzer.analisar_gaps(dados_sem_outliers)
        
        # 5. Classificação de gaps
        print("\n🎯 ETAPA 4: Classificação Estatística de Gaps")
        classification_analyzer = GapClassificationAnalyzer(CONFIG)
        gaps_classificados, metricas_classificacao = classification_analyzer.executar_analise_completa()
        
        # 6. Geração de visualizações
        print("\n📊 ETAPA 5: Geração de Gráficos")
        visualizer = Visualizer(CONFIG)
        visualizer.gerar_todos_graficos(dados_diarios, dados_gaps, dados_finais)
        
        # 7. Geração de relatório
        print("\n📋 ETAPA 6: Geração de Relatório")
        report_gen = ReportGenerator(CONFIG)
        report_gen.gerar_relatorio_completo(dados_diarios, dados_gaps, dados_finais)
        
        # 7. Resumo final
        print("\n" + "=" * 50)
        print("🎯 ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("=" * 50)
        
        print(f"📊 Dados processados:")
        print(f"   • Dados diários: {len(dados_diarios)} dias")
        print(f"   • Gaps analisados: {len(dados_gaps) if dados_gaps is not None else 0}")
        print(f"   • Gaps classificados: {len(gaps_classificados) if gaps_classificados is not None else 0}")
        print(f"   • Classes criadas: {len(metricas_classificacao) if metricas_classificacao is not None else 0}")
        print(f"   • Dados finais limpos: {len(dados_finais)} dias")
        
        print(f"\n📁 Arquivos gerados:")
        print(f"   • {CONFIG['PROCESSED_DIR']}/dados_diarios.csv")
        print(f"   • {CONFIG['PROCESSED_DIR']}/gaps_analisados.csv") 
        print(f"   • {CONFIG['PROCESSED_DIR']}/gaps_classificados.csv")
        print(f"   • {CONFIG['PROCESSED_DIR']}/metricas_por_classe.csv")
        print(f"   • {CONFIG['PROCESSED_DIR']}/features_para_modelo.csv")
        print(f"   • {CONFIG['PROCESSED_DIR']}/dados_limpos_finais.csv")
        print(f"   • {CONFIG['OUTPUT_DIR']}/graphs/evolucao_precos.png")
        print(f"   • {CONFIG['OUTPUT_DIR']}/graphs/analise_gaps.png")
        print(f"   • {CONFIG['OUTPUT_DIR']}/graphs/classificacao_distribuicao.png")
        print(f"   • {CONFIG['OUTPUT_DIR']}/graphs/classificacao_probabilidades.png")
        print(f"   • {CONFIG['OUTPUT_DIR']}/graphs/classificacao_tempos.png")
        print(f"   • {CONFIG['OUTPUT_DIR']}/graphs/classificacao_volatilidade.png")
        print(f"   • {CONFIG['OUTPUT_DIR']}/reports/relatorio_completo.txt")
        
        print(f"\n💡 Para usar os dados:")
        print(f"   import pandas as pd")
        print(f"   dados = pd.read_csv('{CONFIG['PROCESSED_DIR']}/dados_limpos_finais.csv')")
        print(f"   gaps_class = pd.read_csv('{CONFIG['PROCESSED_DIR']}/gaps_classificados.csv')")
        print(f"   metricas = pd.read_csv('{CONFIG['PROCESSED_DIR']}/metricas_por_classe.csv')")
        print(f"   features = pd.read_csv('{CONFIG['PROCESSED_DIR']}/features_para_modelo.csv')")
        
        print(f"\n🚀 Análise finalizada! Verifique a pasta 'output/' para resultados.")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE A ANÁLISE: {e}")
        print(f"💡 Verifique:")
        print(f"   • Se o arquivo de dados está correto")
        print(f"   • Se há espaço suficiente em disco") 
        print(f"   • Se as permissões de escrita estão OK")
        
        import traceback
        print(f"\n🔍 Detalhes do erro:")
        traceback.print_exc()

if __name__ == "__main__":
    main()