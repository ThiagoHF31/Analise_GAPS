# 🚨 MONITOR DE SINAIS DE COMPRA E VENDA - WIN$N
# Script simplificado para monitoramento diário

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calcular_indicadores_basicos(df):
    """Calcula indicadores essenciais para sinais"""
    df = df.copy()
    
    # RSI (14 períodos)
    delta = df['fechamento'].diff()
    ganho = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    perda = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = ganho / perda
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = df['fechamento'].ewm(span=12).mean()
    ema26 = df['fechamento'].ewm(span=26).mean()
    df['macd'] = ema12 - ema26
    df['macd_sinal'] = df['macd'].ewm(span=9).mean()
    
    # Médias Móveis
    df['sma_20'] = df['fechamento'].rolling(window=20).mean()
    df['sma_50'] = df['fechamento'].rolling(window=50).mean()
    
    # Bollinger Bands
    bb_media = df['fechamento'].rolling(window=20).mean()
    bb_std = df['fechamento'].rolling(window=20).std()
    df['bb_superior'] = bb_media + (bb_std * 2)
    df['bb_inferior'] = bb_media - (bb_std * 2)
    
    # Volume
    df['volume_ma'] = df['volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma']
    
    return df

def verificar_sinais_hoje(dados, mostrar_historico=False):
    """Verifica sinais para o último dia disponível"""
    
    print("🚨 MONITOR DE SINAIS WIN$N")
    print("=" * 50)
    
    if len(dados) < 50:
        print("❌ Dados insuficientes para análise!")
        return
    
    # Calcular indicadores
    dados = calcular_indicadores_basicos(dados)
    
    # Último dia (mais recente)
    ultimo_dia = dados.iloc[-1]
    dia_anterior = dados.iloc[-2] if len(dados) > 1 else ultimo_dia
    
    print(f"📅 Análise para: {ultimo_dia['data'].strftime('%d/%m/%Y')}")
    print(f"💰 Preço atual: {ultimo_dia['fechamento']:,.0f} pontos")
    print(f"📊 Volume: {ultimo_dia['volume']:,.0f} (ratio: {ultimo_dia['volume_ratio']:.1f}x)")
    
    # Verificar cada indicador
    print(f"\n🔍 INDICADORES TÉCNICOS:")
    
    # 1. RSI
    rsi_atual = ultimo_dia['rsi']
    if rsi_atual < 30:
        print(f"   📊 RSI: {rsi_atual:.1f} → 🟢 SOBREVENDA (COMPRA)")
        sinal_rsi = "COMPRA"
    elif rsi_atual > 70:
        print(f"   📊 RSI: {rsi_atual:.1f} → 🔴 SOBRECOMPRA (VENDA)")
        sinal_rsi = "VENDA"
    else:
        print(f"   📊 RSI: {rsi_atual:.1f} → ⚪ NEUTRO")
        sinal_rsi = "NEUTRO"
    
    # 2. MACD
    macd_atual = ultimo_dia['macd']
    macd_sinal_atual = ultimo_dia['macd_sinal']
    macd_anterior = dia_anterior['macd']
    macd_sinal_anterior = dia_anterior['macd_sinal']
    
    if macd_atual > macd_sinal_atual and macd_anterior <= macd_sinal_anterior:
        print(f"   📈 MACD: Cruzamento para cima → 🟢 COMPRA")
        sinal_macd = "COMPRA"
    elif macd_atual < macd_sinal_atual and macd_anterior >= macd_sinal_anterior:
        print(f"   📉 MACD: Cruzamento para baixo → 🔴 VENDA")
        sinal_macd = "VENDA"
    else:
        print(f"   📊 MACD: {macd_atual:.0f} vs {macd_sinal_atual:.0f} → ⚪ NEUTRO")
        sinal_macd = "NEUTRO"
    
    # 3. Médias Móveis
    preco = ultimo_dia['fechamento']
    sma20 = ultimo_dia['sma_20']
    sma50 = ultimo_dia['sma_50']
    
    if preco > sma20 > sma50:
        print(f"   📈 Médias: Tendência de alta → 🟢 COMPRA")
        sinal_ma = "COMPRA"
    elif preco < sma20 < sma50:
        print(f"   📉 Médias: Tendência de baixa → 🔴 VENDA")
        sinal_ma = "VENDA"
    else:
        print(f"   📊 Médias: Sem tendência clara → ⚪ NEUTRO")
        sinal_ma = "NEUTRO"
    
    # 4. Bollinger Bands
    bb_sup = ultimo_dia['bb_superior']
    bb_inf = ultimo_dia['bb_inferior']
    
    if preco < bb_inf:
        print(f"   📊 Bollinger: Preço abaixo banda inferior → 🟢 COMPRA")
        sinal_bb = "COMPRA"
    elif preco > bb_sup:
        print(f"   📊 Bollinger: Preço acima banda superior → 🔴 VENDA")
        sinal_bb = "VENDA"
    else:
        print(f"   📊 Bollinger: Preço dentro das bandas → ⚪ NEUTRO")
        sinal_bb = "NEUTRO"
    
    # DECISÃO FINAL
    sinais = [sinal_rsi, sinal_macd, sinal_ma, sinal_bb]
    compras = sinais.count("COMPRA")
    vendas = sinais.count("VENDA")
    
    print(f"\n🎯 ANÁLISE FINAL:")
    print(f"   🟢 Indicadores para COMPRA: {compras}/4")
    print(f"   🔴 Indicadores para VENDA: {vendas}/4")
    
    # Volume como confirmação
    volume_alto = ultimo_dia['volume_ratio'] > 1.2
    volume_status = "ALTO ✅" if volume_alto else "NORMAL ⚪"
    print(f"   📦 Volume: {volume_status}")
    
    if compras >= 2:
        decisao = "🟢 COMPRAR"
        confianca = compras / 4 * 100
        if volume_alto:
            decisao += " (Volume confirma! 🚀)"
            confianca += 20
    elif vendas >= 2:
        decisao = "🔴 VENDER"
        confianca = vendas / 4 * 100
        if volume_alto:
            decisao += " (Volume confirma! 🚀)"
            confianca += 20
    else:
        decisao = "⚪ AGUARDAR"
        confianca = 0
    
    print(f"\n🚨 DECISÃO: {decisao}")
    print(f"💪 Confiança: {min(confianca, 100):.0f}%")
    
    # Stop Loss sugerido
    if compras >= 2:
        stop_loss = preco * 0.98  # 2% abaixo
        take_profit = preco * 1.04  # 4% acima
        print(f"🛡️  Stop Loss sugerido: {stop_loss:,.0f}")
        print(f"🎯 Take Profit sugerido: {take_profit:,.0f}")
    elif vendas >= 2:
        stop_loss = preco * 1.02  # 2% acima
        take_profit = preco * 0.96  # 4% abaixo
        print(f"🛡️  Stop Loss sugerido: {stop_loss:,.0f}")
        print(f"🎯 Take Profit sugerido: {take_profit:,.0f}")
    
    # Histórico dos últimos sinais
    if mostrar_historico:
        print(f"\n📊 ÚLTIMOS 5 DIAS:")
        for i in range(5, 0, -1):
            if len(dados) >= i:
                dia = dados.iloc[-i]
                print(f"   {dia['data'].strftime('%d/%m')}: {dia['fechamento']:,.0f} pts")

def main():
    """Função principal do monitor"""
    
    try:
        # Carregar dados
        try:
            dados = pd.read_csv('dados_diarios_WIN.csv')
            dados['data'] = pd.to_datetime(dados['data'])
        except FileNotFoundError:
            print("Processando dados brutos...")
            dados_brutos = pd.read_csv('WIN$N_M1.csv', sep='\t')
            dados_brutos['data'] = pd.to_datetime(dados_brutos['<DATE>'])
            
            dados = dados_brutos.groupby(dados_brutos['data'].dt.date).agg({
                '<OPEN>': 'first',
                '<HIGH>': 'max', 
                '<LOW>': 'min',
                '<CLOSE>': 'last',
                '<VOL>': 'sum'
            }).reset_index()
            
            dados.columns = ['data', 'abertura', 'maxima', 'minima', 'fechamento', 'volume']
            dados['data'] = pd.to_datetime(dados['data'])
        
        # Verificar sinais
        verificar_sinais_hoje(dados, mostrar_historico=True)
        
        print(f"\n💡 COMO USAR ESTE MONITOR:")
        print(f"   1. Execute diariamente: python monitor_sinais.py")
        print(f"   2. Aguarde 2+ indicadores concordarem")
        print(f"   3. Confirme com volume alto (>1.2x)")
        print(f"   4. Use stops sugeridos para proteção")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()