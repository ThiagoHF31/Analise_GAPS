"""
Configurações do WIN$N Financial Analyzer
Este arquivo contém todas as configurações modificáveis do sistema
"""

# ============================================================================
# CONFIGURAÇÕES PRINCIPAIS
# ============================================================================

# Análise de Gaps
GAP_MINIMO = 100              # Gap mínimo em pontos para considerar significativo
DIAS_LIMITE_GAP = 30          # Dias máximos para verificar fechamento de gap

# Análise de Outliers  
OUTLIER_THRESHOLD = 1.5       # Multiplicador IQR para detecção de outliers
OUTLIER_METHOD = 'iqr'        # Método: 'iqr' ou 'zscore'

# Caminhos de arquivos
DATA_FILE = 'data/WIN$N_M1.csv'      # Arquivo de dados original
OUTPUT_DIR = 'output'                 # Pasta de saída
PROCESSED_DIR = 'data/processed'      # Pasta de dados processados

# Gráficos
GRAPH_DPI = 300               # Resolução dos gráficos (300 = alta qualidade)
GRAPH_FORMAT = 'png'          # Formato dos gráficos

# ============================================================================
# CONFIGURAÇÕES AVANÇADAS
# ============================================================================

# Processamento de dados
REMOVE_WEEKENDS = True        # Remover fins de semana (se houver)
MIN_VOLUME = 100             # Volume mínimo para considerar sessão válida

# Análise estatística
CONFIDENCE_LEVEL = 0.95       # Nível de confiança para intervalos
ANNUALIZATION_FACTOR = 252    # Dias úteis por ano para anualização

# Relatórios
REPORT_ENCODING = 'utf-8'     # Codificação dos relatórios
INCLUDE_RAW_DATA = False      # Incluir dados brutos nos relatórios

# ============================================================================
# CONFIGURAÇÕES DE DISPLAY
# ============================================================================

# Formatação de números
DECIMAL_PLACES_PRICE = 2      # Casas decimais para preços
DECIMAL_PLACES_PERCENT = 3    # Casas decimais para percentuais  
DECIMAL_PLACES_VOLUME = 0     # Casas decimais para volume

# Cores dos gráficos (opcional - usar com matplotlib)
COLOR_POSITIVE = 'green'      # Cor para valores positivos
COLOR_NEGATIVE = 'red'        # Cor para valores negativos
COLOR_NEUTRAL = 'blue'        # Cor neutra

# ============================================================================
# VALIDAÇÕES E LIMITES
# ============================================================================

# Validações de entrada
MAX_FILE_SIZE_MB = 500        # Tamanho máximo do arquivo em MB
MIN_RECORDS = 100             # Número mínimo de registros para análise
MAX_GAP_SIZE = 10000          # Gap máximo considerado válido (pontos)

# Limites de processamento
MAX_MEMORY_USAGE_PCT = 80     # % máximo de uso de memória
CHUNK_SIZE = 10000            # Tamanho do chunk para arquivos grandes

# ============================================================================
# CONFIGURAÇÕES DE DEBUG
# ============================================================================

DEBUG_MODE = False            # Ativar modo debug
VERBOSE_OUTPUT = True         # Saída detalhada
SAVE_INTERMEDIATE = True      # Salvar dados intermediários
LOG_PERFORMANCE = False       # Log de performance

# ============================================================================
# CONFIGURAÇÕES CUSTOMIZÁVEIS POR USUÁRIO
# ============================================================================

# Você pode modificar estas configurações conforme sua necessidade:

# Para gaps menores (mais sensível):
# GAP_MINIMO = 50

# Para análise mais longa de fechamento:
# DIAS_LIMITE_GAP = 60

# Para outliers mais rigorosos:
# OUTLIER_THRESHOLD = 2.0

# Para gráficos de alta resolução:
# GRAPH_DPI = 600