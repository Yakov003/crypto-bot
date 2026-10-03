import os
import telebot
from google import genai
import ccxt

# Получаем ключи из переменных окружения
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
BINANCE_KEY = os.environ.get('BINANCE_KEY')
BINANCE_SECRET = os.environ.get('BINANCE_SECRET')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
gemini_client = genai.Client(api_key=GEMINI_KEY)

exchange = ccxt.binance({
    'apiKey': BINANCE_KEY,
    'secret': BINANCE_SECRET,
})

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне торговую пару (например, BTC/USDT), и я проанализирую последние свечи с Binance через Gemini.")

@bot.message_handler(func=lambda message: True)
def analyze_pair(message):
    pair = message.text.strip().upper()
    bot.reply_to(message, f"Запрашиваю данные Binance для {pair}...")
    
    try:
        # Запрос 15 часовых свечей с Binance
        ohlcv = exchange.fetch_ohlcv(pair, timeframe='1h', limit=15)
        
        prompt = (
            f"Ты — опытный криптоаналитик. Вот 15 последних часовых свечей (OHLCV) для {pair}:\n"
            f"{ohlcv}\n\n"
            f"Проанализируй тренд, уровни поддержки/сопротивления и дай краткое заключение."
        )
        
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Ошибка при получении данных: {e}")

bot.infinity_polling()
