"""
Script de limpeza e organização do projeto
Remove arquivos antigos e organiza estrutura final
"""

import os
import shutil

def limpar_arquivos_antigos():
    """Remove arquivos da análise anterior"""
    arquivos_antigos = [
        'analisar_dados_financeiros.py',
        'analise_completa_win.py', 
        'analise_simples_win.py',
        'carregar_win.py',
        'win_analyzer.py',
        'gerar_graficos_win.py',
        'graficos_simples.py',
        'relatorio_final.py',
        'dados_diarios_win.csv',
        'dados_financeiros_limpos.csv',
        'dados_sem_gaps_abertos.csv',
        'dados_win_diarios_limpos.csv',
        'gaps_analisados_win.csv',
        'WIN_Analise_Completa.png',
        'WIN_Analise_Gaps.png',
        'WIN_Comparacao_Datasets.png',
        'WIN_DayTrade_Evolucao.png',
        'analise_gaps_win.png',
        'analise_temporal_win.png'
    ]
    
    print("🧹 Limpando arquivos antigos...")
    removidos = 0
    
    for arquivo in arquivos_antigos:
        if os.path.exists(arquivo):
            try:
                os.remove(arquivo)
                print(f"   ✅ Removido: {arquivo}")
                removidos += 1
            except Exception as e:
                print(f"   ❌ Erro ao remover {arquivo}: {e}")
    
    print(f"🧹 {removidos} arquivos removidos")

def organizar_estrutura():
    """Verifica e organiza estrutura de pastas"""
    pastas_necessarias = [
        'data',
        'data/processed', 
        'output',
        'output/graphs',
        'output/reports',
        'src'
    ]
    
    print("\n📁 Verificando estrutura de pastas...")
    
    for pasta in pastas_necessarias:
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            print(f"   ✅ Criada: {pasta}")
        else:
            print(f"   ✅ OK: {pasta}")

def criar_arquivo_gitignore():
    """Cria arquivo .gitignore para controle de versão"""
    conteudo_gitignore = """# WIN$N Financial Analyzer - .gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Dados temporários (manter estrutura, ignorar conteúdo)
data/processed/*.csv
output/graphs/*.png
output/reports/*.txt

# Manter arquivos importantes
!data/WIN$N_M1.csv
!requirements.txt
!README.md
!run.py
!config.py
!exemplos_uso.py
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(conteudo_gitignore)
    
    print("📝 Arquivo .gitignore criado")

def verificar_arquivos_principais():
    """Verifica se todos os arquivos principais existem"""
    arquivos_principais = [
        'run.py',
        'README.md', 
        'requirements.txt',
        'config.py',
        'exemplos_uso.py',
        'src/data_processor.py',
        'src/outlier_analyzer.py',
        'src/gap_analyzer.py',
        'src/visualizer.py',
        'src/report_generator.py'
    ]
    
    print("\n🔍 Verificando arquivos principais...")
    todos_ok = True
    
    for arquivo in arquivos_principais:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ FALTANDO: {arquivo}")
            todos_ok = False
    
    return todos_ok

def main():
    """Executa limpeza e organização completa"""
    print("🚀 LIMPEZA E ORGANIZAÇÃO DO PROJETO")
    print("=" * 50)
    
    # 1. Limpar arquivos antigos
    limpar_arquivos_antigos()
    
    # 2. Organizar estrutura
    organizar_estrutura()
    
    # 3. Criar .gitignore
    criar_arquivo_gitignore()
    
    # 4. Verificar integridade
    if verificar_arquivos_principais():
        print("\n✅ PROJETO ORGANIZADO COM SUCESSO!")
        print("\n📋 ESTRUTURA FINAL:")
        print("""
projeto/
├── run.py                    # ⭐ EXECUTE ESTE ARQUIVO
├── README.md                 # 📖 Documentação completa
├── requirements.txt          # 📦 Dependências
├── config.py                 # ⚙️  Configurações
├── exemplos_uso.py          # 💡 Exemplos de uso
├── .gitignore               # 🚫 Controle de versão
├── data/
│   ├── WIN$N_M1.csv         # 📊 Seus dados (você fornece)
│   └── processed/           # 📁 Dados processados (auto)
├── output/
│   ├── graphs/              # 📈 Gráficos gerados
│   └── reports/             # 📋 Relatórios
└── src/
    ├── data_processor.py     # 🔄 Processamento
    ├── outlier_analyzer.py   # 🔍 Análise outliers
    ├── gap_analyzer.py       # 📈 Análise gaps
    ├── visualizer.py         # 📊 Gráficos
    └── report_generator.py   # 📋 Relatórios
        """)
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Certifique-se de que WIN$N_M1.csv está na pasta data/")
        print("2. Execute: python run.py")
        print("3. Aguarde a análise completa")
        print("4. Verifique os resultados na pasta output/")
        print("\n💡 Para análises customizadas: python exemplos_uso.py")
        
    else:
        print("\n❌ ALGUNS ARQUIVOS ESTÃO FALTANDO!")
        print("Verifique a integridade do projeto.")

if __name__ == "__main__":
    main()