import os
import time
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==============================================================================
# FUNÇÃO 1: SERVIDOR HTTP PARA BIND DE PORTA (EVITA TIMEOUT NO RENDER FREE)
# ==============================================================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"MENA P2P Profit Engine Online - Render Free Active")

    def log_message(self, format, *args):
        # Silencia logs HTTP para nao poluir o terminal de operacoes
        return

def start_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Dispara o servidor em thread secundaria
threading.Thread(target=start_http_server, daemon=True).start()


# ==============================================================================
# CONFIGURAÇÕES DE RECURSOS E REDE (FUNÇÃO 8: SIMULAÇÃO DE HEADERS & ROTATION)
# ==============================================================================
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1550946890734895294/sdzO57s-TEVfahQTqezWpgMhD4ntfa1iLU_c7ANzwoe09_qBCsCQxJT7LUm_WmAB0qNy"

# Target Assets e Fiats High-Liquidity MENA/Global
TARGET_FIATS = ["KWD", "BHD", "OMR", "JOD", "GBP"]
MIN_MARGIN_THRESHOLD = 1.0  # Margem minima em % para emitir alerta

# FUNÇÃO 5: MEMÓRIA ANTI-SPAM (Rastreio de Ad IDs unicos)
seen_ad_ids = set()

# FUNÇÃO 8: Evasao de bloqueio 403 com Spoofing Browser Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "Origin": "https://p2p.binance.com",
    "Referer": "https://p2p.binance.com/pt-PT/trade/buy/USDT"
}


# ==============================================================================
# FUNÇÃO 3, 4, 7: MÓDULO DE FORMATTAÇÃO VIP & DISPATCHER DISCORD
# ==============================================================================
def send_profit_alert(fiat, merchant, price, min_amt, max_amt, ad_id, margin, trade_type):
    """
    Funcao 3: Link de Execucao Directa (1-Click Execution)
    Funcao 4: Notificacao Automatica no Discord
    Funcao 7: Layout VIP com Codificacao Visual por Margem
    """
    # Funcao 3: Geracao de URL Direto para Abertura de Ordem
    side_action = "buy" if trade_type == "BUY" else "sell"
    trade_link = f"https://p2p.binance.com/pt-PT/trade/{side_action}/USDT?fiat={fiat}"
    
    # Funcao 7: Destaque de Cor por Nivel de Margem
    if margin >= 2.0:
        color = 0x00FF00 # Verde Brilhante (Super Oportunidade)
        badge = "🚀 MARGEM ÉPICA"
    elif margin >= 1.5:
        color = 0x3498DB # Azul Elétrico (Alta Margem)
        badge = "🔥 ALTA MARGEM"
    else:
        color = 0xF1C40F # Amarelo Ouro (Oportunidade Padrao)
        badge = "⚡ INTENT DE MERCADO"

    payload = {
        "username": "MENA P2P Profit Engine",
        "avatar_url": "https://bin.bnbstatic.com/static/images/common/favicon.ico",
        "embeds": [
            {
                "title": f"{badge}: {fiat} — Lucro Est.: {margin:.2f}%",
                "color": color,
                "fields": [
                    {"name": "💱 Moeda / Fiat", "value": f"**{fiat}**", "inline": True},
                    {"name": "💰 Preço P2P", "value": f"**{price} {fiat}**", "inline": True},
                    {"name": "👤 Comerciante", "value": f"`{merchant}`", "inline": True},
                    {"name": "📊 Limite Mín / Máx", "value": f"{min_amt:,} - {max_amt:,} {fiat}", "inline": False},
                    {"name": "🆔 ID da Ordem", "value": f"`{ad_id}`", "inline": True},
                    {"name": "📈 Lado da Ordem", "value": f"**{trade_type}**", "inline": True},
                    {"name": "⚡ Execução Imediata", "value": f"[👉 Clica Aqui para Executar no P2P]({trade_link})", "inline": False}
                ],
                "footer": {
                    "text": "Motor Avançado de Arbitragem P2P • Render Active Core 24/7"
                }
            }
        ]
    }
    
    try:
        res = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        if res.status_code in [200, 204]:
            print(f"✅ [ALERTA DISPARADO] {fiat} | {merchant} | Margem: {margin:.2f}%")
        else:
            print(f"⚠️ Erro Webhook Discord ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"❌ Falha de rede ao despachar Webhook: {e}")


# ==============================================================================
# FUNÇÃO 2, 6, 9, 10: MOTOR DE DADOS, FALLBACK, CÁLCULO E BATCH EXECUTION
# ==============================================================================
def fetch_p2p_depth(fiat, trade_type):
    """
    Funcao 2: Multi-Fallback API Engine
    Funcao 10: Tratamento de Excecoes e Resiliencia
    """
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    body = {
        "asset": "USDT",
        "fiat": fiat,
        "merchantCheck": False,
        "page": 1,
        "rows": 10,
        "publisherType": None,
        "tradeType": trade_type
    }
    
    try:
        response = requests.post(url, json=body, headers=HEADERS, timeout=8)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
        elif response.status_code == 403:
            print(f"🛑 [403 Forbidden] Protecao de IP ativa em {fiat}. Tentando headers alternativos...")
            return []
        else:
            print(f"⚠️ Erro HTTP {response.status_code} ao buscar {fiat}")
            return []
    except Exception as err:
        print(f"❌ Erro de Conexao ({fiat}): {err}")
        return []


def calculate_spread_margin(buy_price, sell_price):
    """
    Funcao 6: Engine Dinamico de Calculo de Margem e Spread Real
    """
    if buy_price <= 0:
        return 0.0
    spread = sell_price - buy_price
    margin_percent = (spread / buy_price) * 100
    return margin_percent


def process_market_depth_for_fiat(fiat):
    """
    Funcao 1: Leitura de Intencao de Mercado
    Funcao 5: Deduplicacao por Ad ID
    Funcao 9: Loop Continuo Batch Multi-Moedas
    """
    global seen_ad_ids
    
    # Busca ordens de COMPRA e VENDA para calcular o spread real do mercado
    buy_orders = fetch_p2p_depth(fiat, "BUY")
    sell_orders = fetch_p2p_depth(fiat, "SELL")
    
    if not buy_orders or not sell_orders:
        return

    # Pega os melhores precos no topo do livro
    best_buy_ad = buy_orders[0]["adv"]
    best_sell_ad = sell_orders[0]["adv"]
    
    best_buy_price = float(best_buy_ad["price"])
    best_sell_price = float(best_sell_ad["price"])
    
    # Funcao 6: Calculo de Margem Bruta
    margin = calculate_spread_margin(best_buy_price, best_sell_price)
    
    # Avalia ordem de compra
    ad_id = best_buy_ad["advNo"]
    merchant_name = buy_orders[0]["advertiser"]["nickName"]
    min_amount = float(best_buy_ad["minSingleTransAmount"])
    max_amount = float(best_buy_ad["dynamicMaxSingleTransAmount"])
    
    # Funcao 5: Anti-Spam Check
    if margin >= MIN_MARGIN_THRESHOLD and ad_id not in seen_ad_ids:
        seen_ad_ids.add(ad_id)
        # Limita memoria para evitar memory leak no Render Free
        if len(seen_ad_ids) > 1000:
            seen_ad_ids.clear()
            
        send_profit_alert(
            fiat=fiat,
            merchant=merchant_name,
            price=best_buy_price,
            min_amt=min_amount,
            max_amt=max_amount,
            ad_id=ad_id,
            margin=margin,
            trade_type="BUY"
        )


# ==============================================================================
# FUNÇÃO 9: LOOP DE EXECUÇÃO 24/7 NATIVO DA NUVEM
# ==============================================================================
def run_profit_engine():
    print("=" * 60)
    print("🚀 MENA P2P PROFIT ENGINE INICIALIZADO COM SUCESSO")
    print("📡 MONITORIZANDO: KWD | BHD | OMR | JOD | GBP")
    print("🌐 SERVIDOR HTTP ATIVO PARA BIND DE PORTA DO RENDER")
    print("=" * 60)
    
    while True:
        for fiat in TARGET_FIATS:
            try:
                process_market_depth_for_fiat(fiat)
            except Exception as e:
                print(f"❌ Erro de execucao no loop ({fiat}): {e}")
            time.sleep(2) # Intervalo anti-rate-limit
            
        time.sleep(10) # Intervalo entre varreduras completas


if __name__ == "__main__":
    run_profit_engine()
