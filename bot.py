import logging
import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from groq import Groq

# ---------------------------------------------------------------------------
# CONFIG — reads from Railway environment variables
# ---------------------------------------------------------------------------
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY   = os.environ.get('GROQ_API_KEY')

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------
bot       = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = Groq(api_key=GROQ_API_KEY)

# ---------------------------------------------------------------------------
# AI System Prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are the official AI assistant for Light Solution Inc, a cutting-edge technology company
based in Lagos, Nigeria. You are an expert advisor representing the company professionally.

Your deep expertise covers:
- Business strategy, growth, and digital transformation
- Automation (RPA, AI agents, workflow automation, n8n, Zapier, Make)
- Technology (Web2, Web3, blockchain, smart contracts, IoT, Raspberry Pi, Flutter)
- AI Video Making and AI Film Making (Sora, Runway ML, Kling, HeyGen, ElevenLabs, Pika)
- Agentic AI (AutoGPT, CrewAI, LangChain agents, multi-agent systems)
- Algorithmic Trading (quantitative strategies, backtesting, crypto bots, MT5, CCXT)
- AI Marketing and Lead Generation (AI-powered funnels, CRM automation, LinkedIn outreach)
- Sales Conversion (copywriting, conversion optimization, AI sales agents)

Company contact details (always share when users ask how to reach us):
- Phone/WhatsApp: +2349071972929
- Email: olaoluwaalawode1@gmail.com
- YouTube: https://www.youtube.com/channel/UCiK9INVlB2qb26OMbTf4N0w

Personality and tone:
- Professional, confident, and authoritative
- Concise but thorough with actionable expert-level answers
- Friendly and encouraging
- Always end with a relevant call-to-action
- Regularly mention that Light Solution Inc can implement these solutions for the user

Rules:
- Never make up statistics or false claims
- Keep responses under 400 words
- Format cleanly with line breaks for Telegram readability
- Do NOT use markdown symbols like * # _ at all
- Always educate users about services and how the company can help them
"""

# ---------------------------------------------------------------------------
# Groq AI — verified production models with fallback
# ---------------------------------------------------------------------------
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

def ask_ai(user_message: str, conversation_history: list) -> str:
    conversation_history.append({"role": "user", "content": user_message})
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    for model in GROQ_MODELS:
        try:
            response = ai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            )
            reply = response.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": reply})
            if len(conversation_history) > 40:
                conversation_history[:] = conversation_history[-40:]
            return reply
        except Exception as e:
            error_str = str(e).lower()
            if any(w in error_str for w in ["decommissioned", "not found", "model_not_found", "invalid"]):
                logger.warning(f"Model {model} unavailable, trying next...")
                continue
            else:
                logger.error(f"Groq error with {model}: {e}")
                break

    return (
        "Our AI is temporarily unavailable.\n\n"
        "Please contact us directly:\n"
        "WhatsApp: +2349071972929\n"
        "Email: olaoluwaalawode1@gmail.com"
    )

# ---------------------------------------------------------------------------
# Per-user conversation memory
# ---------------------------------------------------------------------------
user_histories: dict = {}

def get_history(user_id: int) -> list:
    if user_id not in user_histories:
        user_histories[user_id] = []
    return user_histories[user_id]

# ---------------------------------------------------------------------------
# Main menu keyboard
# ---------------------------------------------------------------------------
def main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton('🤖 AI & Automation'),  KeyboardButton('📈 Algorithmic Trading'))
    markup.row(KeyboardButton('🎬 AI Video & Film'),  KeyboardButton('💼 Business Strategy'))
    markup.row(KeyboardButton('📣 AI Marketing'),     KeyboardButton('🔗 Web3 & Blockchain'))
    markup.row(KeyboardButton('📞 Contact Us'),       KeyboardButton('❓ Help'))
    return markup

# ---------------------------------------------------------------------------
# Topic prompts
# ---------------------------------------------------------------------------
TOPIC_MAP = {
    '🤖 ai & automation':     "Educate me about AI automation opportunities for businesses in 2025. Include real tools, use cases, and explain how Light Solution Inc can implement this.",
    '📈 algorithmic trading': "Educate me about algorithmic trading strategies, crypto and forex bots, and how businesses can profit from automated trading in 2025.",
    '🎬 ai video & film':     "Educate me about the best AI tools for video creation and AI filmmaking in 2025. Include Sora, Runway, HeyGen and others. How can Light Solution Inc help?",
    '💼 business strategy':   "Educate me about the most impactful digital transformation strategies for a modern tech business in Africa and globally in 2025.",
    '📣 ai marketing':        "Educate me about AI-powered marketing, lead generation, and sales conversion in 2025. What tools dominate and how can Light Solution Inc help?",
    '🔗 web3 & blockchain':   "Educate me about Web3 business opportunities, smart contracts, DeFi and blockchain in 2025. How can Light Solution Inc help implement these?",
}

# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name or "there"
    bot.send_message(
        message.chat.id,
        f"Welcome, {user_name}!\n\n"
        f"I am the AI assistant for Light Solution Inc — your partner in technology, "
        f"automation, and intelligent business solutions based in Lagos, Nigeria.\n\n"
        f"I can answer expert questions on:\n"
        f"- Business and automation\n"
        f"- AI video and film making\n"
        f"- Algorithmic trading\n"
        f"- Agentic AI systems\n"
        f"- AI marketing and sales\n"
        f"- Web3 and blockchain\n\n"
        f"Just type your question or pick a topic below!",
        reply_markup=main_keyboard()
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Available Commands:\n\n"
        "/start — Welcome and topic menu\n"
        "/help — This message\n"
        "/contact — Reach our team\n"
        "/services — What we offer\n"
        "/resources — Free learning links\n"
        "/clear — Reset conversation memory\n\n"
        "Or just ask me anything about business, automation, trading, AI video, and marketing!",
        reply_markup=main_keyboard()
    )

@bot.message_handler(commands=['contact'])
def contact(message):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("WhatsApp Us", url="https://wa.me/2349071972929"),
        InlineKeyboardButton("YouTube", url="https://www.youtube.com/channel/UCiK9INVlB2qb26OMbTf4N0w")
    )
    bot.send_message(
        message.chat.id,
        "Contact Light Solution Inc\n\n"
        "Phone/WhatsApp: +2349071972929\n"
        "Email: olaoluwaalawode1@gmail.com\n"
        "YouTube: Light Solution Inc\n\n"
        "We respond within 24 hours. Ready to build something extraordinary?",
        reply_markup=markup
    )

@bot.message_handler(commands=['services'])
def services(message):
    bot.send_message(
        message.chat.id,
        "Light Solution Inc Services\n\n"
        "AI and Automation — Workflow automation, AI agents, RPA\n"
        "AI Video and Film — Sora, Runway, HeyGen productions\n"
        "Algorithmic Trading — Crypto and forex trading bots\n"
        "Business Solutions — Digital transformation consulting\n"
        "AI Marketing — Lead generation and sales funnels\n"
        "Mobile Apps — Flutter cross-platform development\n"
        "IoT and Raspberry Pi — Embedded systems and hardware\n"
        "Web3 and Blockchain — Smart contracts and DeFi\n\n"
        "WhatsApp: +2349071972929\n"
        "Email: olaoluwaalawode1@gmail.com",
        reply_markup=main_keyboard()
    )

@bot.message_handler(commands=['resources'])
def resources(message):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Flutter Tutorial", url="https://youtu.be/D4nhaszNW4o?si=oz8dmkQYJY9j7PDo"),
        InlineKeyboardButton("Raspberry Pi", url="https://youtu.be/SL4_oU9t8Ss?si=vZHlFqzhgSqdTs95")
    )
    bot.send_message(
        message.chat.id,
        "Free Learning Resources\n\n"
        "Hand-picked by the Light Solution Inc team to help you grow:",
        reply_markup=markup
    )

@bot.message_handler(commands=['clear'])
def clear_history(message):
    user_histories[message.from_user.id] = []
    bot.send_message(
        message.chat.id,
        "Conversation memory cleared! Starting fresh.\n\n"
        "Ask me anything about business, automation, AI, trading, or marketing!",
        reply_markup=main_keyboard()
    )

# ---------------------------------------------------------------------------
# Main message handler — AI brain
# ---------------------------------------------------------------------------

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id    = message.from_user.id
    user_text  = message.text.strip()
    text_lower = user_text.lower()

    if text_lower == '📞 contact us':
        contact(message)
        return
    if text_lower == '❓ help':
        help_command(message)
        return

    prompt = TOPIC_MAP.get(text_lower, user_text)

    bot.send_chat_action(message.chat.id, 'typing')

    history = get_history(user_id)
    reply   = ask_ai(prompt, history)

    bot.send_message(message.chat.id, reply, reply_markup=main_keyboard())

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Light Solution Inc Bot is live!")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
