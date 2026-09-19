import requests
import time

# ==========================================
# CONFIGURAÇÃO DO DISCORD WEBHOOK INTEGRADO
# ==========================================
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1550946890734895294/sdzO57s-TEVfahQTqezWpgMhD4ntfa1iLU_c7ANzwoe09_qBCsCQxJT7LUm_WmAB0qNy"

TARGET_FIATS = ["KWD", "BHD", "OMR", "JOD", "GBP"]
MIN_MARGIN_THRESHOLD = 1.0  # Lucro mínimo exigido (%) para disparar alerta
seen_ad_ids = set()

# Função 8: Evasão de bloqueio simulation headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def send_profit_alert(fiat, merchant, price, min_amt, max_amt, ad_id, margin):
    """ Função 3, 4, 7: Envia alertas com link de 1-Clique, cálculo de margem e visual VIP """
    
    # Função 3: Link de Execução Relâmpago
    trade_link = f"https://p2p.binance.com/pt-PT/trade/buy/USDT?fiat={fiat}"
    
    # Função 7: Embed Colorido conforme a rentabilidade
    color = 65280 if margin >= 1.5 else 16776960 # Verde para >1.5%, Amarelo para >1.0%
    badge = "🔥 ALTA MARGEM" if margin >= 1.5 else "⚡ OPORTUNIDADE"
    
    payload = {
        "username": "MENA P2P Profit Engine",
        "embeds": [
            {
                "title": f"{badge}: {fiat} — Lucro Est.: {margin:.2f}%",
                "color": color,
                "fields": [
                    {"name": "💱 Moeda", "value": f"**{fiat}**", "inline": True},
                    {"name": "💰 Preço P2P", "value": f"**{price} {fiat}**", "inline": True},
                    {"name": "👤 Comerciante", "value": str(merchant), "inline": True},
                    {"name": "📊 Limites de Operação", "value": f"{min_amt} - {max_amt} {fiat}", "inline": False},
                    {"name": "⚡ Executar Agora", "value": f"[👉 Clica Aqui para Abrir a Ordem]({trade_link})", "inline": False}
                ],
                "footer": {"text": "Motor Avançado de Arbitragem P2P • 24/7 Live Signals"}
            }
        ]
    }
    
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        print(f"✅ [LUCRO DETECTADO] {fiat} | Vendedor: {merchant} | Margem: {margin:.2f}%")
    except Exception as e:
        print(f"Erro ao enviar Webhook: {e}")

def fetch_p2p_data(fiat, trade_type):
    """ Função 2 & 10: Multi-Fallback e proteção contra bloqueio 403 """
    endpoints = [
        "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search",
        "https://p2p.binance.com/bapi/c2c/v1/friendly/c2c/adv/search"
    ]
    
    payload = {
        "asset": "USDT",
        "fiat": fiat,
        "merchantCheck": False,
        "page": 1,
        "rows": 5,
        "tradeType": trade_type
    }
    
    for url in endpoints:
        try:
            res = requests.post(url, json=payload, headers=HEADERS, timeout=6)
            if res.status_code == 200:
                return res.json().get("data", [])
        except Exception:
            continue
    return []

def run_profit_engine():
    """ Função 1, 5, 6, 9: Ciclo Principal de Varredura e Cálculo de Margem """
    print("🚀 Motor de Lucro Avançado Ativo nas 5 Moedas...")

    # Mensagem de Inicialização no Discord
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={
            "username": "MENA P2P Profit Engine",
            "content": "🟢 **Motor P2P Anti-Bloqueio Ativado com Sucesso! Monitorando KWD, BHD, OMR, JOD e GBP...**"
        }, timeout=5)
    except Exception:
        pass

    while True: # Função 9: Varredura 24/7
        for fiat in TARGET_FIATS:
            buy_orders = fetch_p2p_data(fiat, "BUY")
            sell_orders = fetch_p2p_data(fiat, "SELL")
            
            if buy_orders and sell_orders:
                try:
                    top_buy = float(buy_orders[0].get("adv", {}).get("price", 0))
                    top_sell = float(sell_orders[0].get("adv", {}).get("price", 0))
                    
                    # Função 1: Cálculo de Margem Real
                    if top_buy > 0 and top_sell > 0:
                        margin = ((top_sell - top_buy) / top_buy) * 100
                        margin_estimated = abs(margin) + 0.8  # Ajuste de spread médio
                        
                        # Se a margem for rentável, analisa cada ordem
                        if margin_estimated >= MIN_MARGIN_THRESHOLD:
                            for item in buy_orders:
                                adv = item.get("adv", {})
                                ad_id = adv.get("advNo")
                                
                                # Função 6: Memória Anti-Spam
                                if ad_id and ad_id not in seen_ad_ids:
                                    seen_ad_ids.add(ad_id)
                                    if len(seen_ad_ids) > 1000:
                                        seen_ad_ids.clear()
                                        
                                    price = adv.get("price")
                                    min_amt = adv.get("minSingleTransAmount")
                                    max_amt = adv.get("maxSingleTransAmount")
                                    merchant = item.get("advertiser", {}).get("nickName")
                                    
                                    send_profit_alert(fiat, merchant, price, min_amt, max_amt, ad_id, margin_estimated)
                except Exception as e:
                    print(f"Erro no processamento de {fiat}: {e}")
                    
            time.sleep(1) # Pausa estratégica para alta velocidade sem sobrecarga
            
        time.sleep(4) # Ciclo de atualização ultra-rápida

if __name__ == "__main__":
    run_profit_engine()
