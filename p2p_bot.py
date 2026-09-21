import os
import time
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from google import genai

# ==========================================
# 1. SERVIDOR DE MANUTENÇÃO (HEALTH CHECK RENDER)
# ==========================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Maquina de Lucro - Radar Duplo Active 24/7")

    def log_message(self, format, *args):
        return

def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# ==========================================
# 2. VARIÁVEIS DE AMBIENTE E CONFIGURAÇÕES
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

TARGET_CURRENCIES = ["KWD", "BHD", "OMR", "JOD", "GBP"]
MIN_SPREAD = 0.8
POLL_INTERVAL = 12

LOCAL_CONFIG = {
    "KWD": {"lang": "Arabic", "greeting": "السلام عليكم ورحمة الله وبركاته", "tone": "VIP High Trust"},
    "BHD": {"lang": "Arabic", "greeting": "مرحبا بك أخي العزيز", "tone": "Ultra Professional & Fast"},
    "OMR": {"lang": "Arabic", "greeting": "أهلاً وسهلاً بك", "tone": "Direct & Secure"},
    "JOD": {"lang": "Arabic", "greeting": "مرحبتين يا غالي", "tone": "Urgent & High Security"},
    "GBP": {"lang": "English", "greeting": "Hello! Express VIP Trade", "tone": "Institutional Fast"}
}

def send_discord_radar(content):
    print(f"[MAQUINA-LUCRO]: {content}")
    if DISCORD_WEBHOOK_URL:
        try:
            requests.post(DISCORD_WEBHOOK_URL, json={"content": content}, timeout=5)
        except Exception as e:
            print(f"Erro no envio para Discord: {e}")

def get_p2p_prices(fiat, trade_type):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    payload = {
        "asset": "USDT",
        "fiat": fiat,
        "merchantCheck": False,
        "page": 1,
        "payTypes": [],
        "rows": 5,
        "tradeType": trade_type
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=8)
        if r.status_code == 200:
            return r.json().get("data", [])
    except Exception as e:
        print(f"Erro ao buscar preços de {fiat} ({trade_type}): {e}")
    return []

# ==========================================
# 3. GERAÇÃO DE SCRIPT PSICOLÓGICO COM GEMINI IA
# ==========================================
def generate_psychological_dm(fiat, spread):
    info = LOCAL_CONFIG.get(fiat, {"lang": "English", "greeting": "Hello", "tone": "Direct VIP"})
    
    if not gemini_client:
        return f"{info['greeting']}! Tenho cotação VIP disponível para troca rápida e segura em {fiat}. Garantia de execução imediata."

    prompt = f"""
    Atua como um negociador experiente de intermediação e arbitragem OTC/P2P.
    Idioma obrigatório: {info['lang']}
    Saudação inicial obrigatória: {info['greeting']}
    Tom: {info['tone']}
    Moeda envolvida: {fiat}
    Margem de vantagem da taxa: {spread:.2f}%

    Cria uma mensagem curta de Abordagem Direta (DM) para enviar a um potencial cliente nas redes sociais ou chats que deseja trocar {fiat}.
    Regras estritas:
    1. Transmitir máxima autoridade, segurança e rapidez.
    2. Motivar a conclusão do negócio em menos de 2 minutos.
    3. No máximo 3 linhas de texto corrido.
    """
    try:
        res = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return res.text.strip()
    except Exception as e:
        return f"{info['greeting']} - VIP exchange service available for {fiat}. Best rates and instant execution."

# ==========================================
# 4. MOTOR PRINCIPAL DE VARREDURA E NOTIFICAÇÃO
# ==========================================
def dual_radar_engine():
    send_discord_radar("🚀 **MÁQUINA DE LUCRO: RADAR DUPLO DE INTERMEDIAÇÃO E ARBITRAGEM ATIVO (24/7)!**")
    send_discord_radar("📡 Monitorização ativa para KWD, BHD, OMR, JOD e GBP. A gerar scripts de conversão e alertas de margem.")

    while True:
        try:
            for fiat in TARGET_CURRENCIES:
                buys = get_p2p_prices(fiat, "BUY")
                sells = get_p2p_prices(fiat, "SELL")

                if buys and sells:
                    top_buy = float(buys[0]["adv"]["price"])
                    top_sell = float(sells[0]["adv"]["price"])
                    spread = ((top_sell - top_buy) / top_buy) * 100

                    if spread >= MIN_SPREAD:
                        dm_script = generate_psychological_dm(fiat, spread)
                        binance_p2p_url = f"https://p2p.binance.com/en/trade/all-payments/USDT?fiat={fiat}"

                        msg = (
                            f"🚨 **RADAR 1: OPORTUNIDADE DE MARGEM ({fiat})**\n"
                            f"📈 **Spread Estimado:** `{spread:.2f}%` | Compra: `{top_buy}` | Venda: `{top_sell}`\n"
                            f"🔗 **Mercado P2P:** [Abrir Livro {fiat} na Binance]({binance_p2p_url})\n\n"
                            f"📩 **RADAR 2: MENSAGEM PSICOLÓGICA PRONTA PARA ENVIAR (DM):**\n"
                            f"```{dm_script}```\n"
                            f"💡 *Execução:* Copia a mensagem acima, aborda o contacto direto que quer trocar {fiat} e retém a tua comissão com segurança!"
                        )
                        send_discord_radar(msg)

            time.sleep(POLL_INTERVAL)

        except Exception as e:
            send_discord_radar(f"⚠️ Aviso no ciclo do radar: {e}")
            time.sleep(10)

if __name__ == "__main__":
    dual_radar_engine()
