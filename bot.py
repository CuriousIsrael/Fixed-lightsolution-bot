import logging
import os
import asyncio
from groq import Groq
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY   = os.environ.get('GROQ_API_KEY')

SYSTEM_PROMPT = """
You are the official AI assistant for Light Solution Inc, a cutting-edge technology company
based in Lagos, Nigeria. You are an expert advisor representing the company professionally.

Your deep expertise covers:
- Business strategy, growth, and digital transformation
- Automation (RPA, AI agents, workflow automation, n8n, Zapier, Make)
- Technology (Web2, Web3, blockchain, smart contracts, IoT, Raspberry Pi, Flutter)
- AI Video Making & AI Film Making (Sora, Runway ML, Kling, HeyGen, ElevenLabs, Pika)
- Agentic AI (AutoGPT, CrewAI, LangChain agents, multi-agent systems)
- Algorithmic Trading (quantitative strategies, backtesting, crypto bots, MT5, CCXT)
- AI Marketing & Lead Generation (AI-powered funnels, CRM automation, LinkedIn outreach)
- Sales Conversion (copywriting, conversion optimization, AI sales agents)

Company contact details (always share when users ask how to reach us):
- Phone/WhatsApp: +2349071972929
- Email: olaoluwaalawode1@gmail.com
- YouTube: https://www.youtube.com/channel/UCiK9INVlB2qb26OMbTf4N0w

Personality and tone:
- Professional, confident, and authoritative
- Concise but thorough with actionable expert-level answers
- Friendly and encouraging
- Always end with a call-to-action
- Mention Light Solution Inc can implement solutions for the user

Rules:
- Never make up statistics or false claims
- Keep responses under 400 words
- Format cleanly with line breaks for Telegram readability
- Do NOT use markdown headers
- Always educate users about services and how we can help
"""

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

ai_client = Groq(api_key=GROQ_API_KEY)

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
            if any(w in error_str for w in ["decommissioned", "not found", "model_not_found", "invalid model"]):
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

user_histories: dict = {}

def get_history(user_id: int) -> list:
    if user_id not in user_histories:
        user_histories[user_id] = []
    return user_histories[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "there"
    keyboard = [
        ['🤖 AI & Automation',  '📈 Algorithmic Trading'],
        ['🎬 AI Video & Film',  '💼 Business Strategy'],
        ['📣 AI Marketing',     '🔗 Web3 & Blockchain'],
        ['📞 Contact Us',       '❓ Help']
    ]
    await update.message.reply_text(
        f"👋 Welcome, {user_name}!\n\n"
        f"I'm the AI assistant for Light Solution Inc — your partner in technology, "
        f"automation, and intelligent business solutions based in Lagos, Nigeria.\n\n"
        f"I can answer expert questions on:\n"
        f"• Business & automation\n"
        f"• AI video & film making\n"
        f"• Algorithmic trading\n"
        f"• Agentic AI systems\n"
        f"• AI marketing & sales\n"
        f"• Web3 & blockchain\n\n"
        f"Just type your question or pick a topic below!",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available Commands:\n\n"
        "/start — Welcome and topic menu\n"
        "/help — This message\n"
        "/contact — Reach our team\n"
        "/services — What we offer\n"
        "/resources — Free learning links\n"
        "/clear — Reset conversation memory\n\n"
        "Or just ask me anything about business, automation, trading, AI video, and marketing!"
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("📱 WhatsApp Us", url="https://wa.me/2349071972929"),
        InlineKeyboardButton("▶️ YouTube", url="https://www.youtube.com/channel/UCiK9INVlB2qb26OMbTf4N0w"),
    ]]
    await update.message.reply_text(
        "Contact Light Solution Inc\n\n"
        "📱 Phone/WhatsApp: +2349071972929\n"
        "✉️ Email: olaoluwaalawode1@gmail.com\n"
        "▶️ YouTube: Light Solution Inc\n\n"
        "We respond within 24 hours. Ready to build something extraordinary? 🚀",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Light Solution Inc Services\n\n"
        "🤖 AI & Automation — Workflow automation, AI agents, RPA\n"
        "🎬 AI Video & Film — Sora, Runway, HeyGen productions\n"
        "📈 Algorithmic Trading — Crypto and forex trading bots\n"
        "💼 Business Solutions — Digital transformation consulting\n"
        "📣 AI Marketing — Lead generation and sales funnels\n"
        "📱 Mobile Apps — Flutter cross-platform development\n"
        "🍓 IoT & Raspberry Pi — Embedded systems and hardware\n"
        "🔗 Web3 & Blockchain — Smart contracts and DeFi\n\n"
        "📱 WhatsApp: +2349071972929\n"
        "✉️ Email: olaoluwaalawode1@gmail.com"
    )

async def resources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("📱 Flutter Tutorial", url="https://youtu.be/D4nhaszNW4o?si=oz8dmkQYJY9j7PDo"),
        InlineKeyboardButton("🍓 Raspberry Pi", url="https://youtu.be/SL4_oU9t8Ss?si=vZHlFqzhgSqdTs95"),
    ]]
    await update.message.reply_text(
        "🎓 Free Learning Resources\n\n"
        "Hand-picked by the Light Solution Inc team:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_histories[update.effective_user.id] = []
    await update.message.reply_text(
        "Conversation memory cleared! Starting fresh.\n\n"
        "Ask me anything about business, automation, AI, trading, or marketing!"
    )

TOPIC_MAP = {
    '🤖 ai & automation':     "Educate me about AI automation opportunities for businesses in 2025. Include real tools, use cases, and explain how Light Solution Inc can implement this.",
    '📈 algorithmic trading': "Educate me about algorithmic trading strategies, crypto and forex bots, and how businesses can profit from automated trading in 2025.",
    '🎬 ai video & film':     "Educate me about the best AI tools for video creation and AI filmmaking in 2025. Include Sora, Runway, HeyGen and others.",
    '💼 business strategy':   "Educate me about the most impactful digital transformation strategies for a modern tech business in Africa and globally in 2025.",
    '📣 ai marketing':        "Educate me about AI-powered marketing, lead generation, and sales conversion in 2025. What tools dominate?",
    '🔗 web3 & blockchain':   "Educate me about Web3 business opportunities, smart contracts, DeFi and blockchain in 2025.",
    '📞 contact us':          None,
    '❓ help':                None,
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id    = update.effective_user.id
    user_text  = update.message.text.strip()
    text_lower = user_text.lower()

    if text_lower == '📞 contact us':
        await contact(update, context)
        return
    if text_lower == '❓ help':
        await help_command(update, context)
        return

    prompt = TOPIC_MAP.get(text_lower, user_text)

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    history = get_history(user_id)
    reply   = ask_ai(prompt, history)

    await update.message.reply_text(reply)

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start',     start))
    app.add_handler(CommandHandler('help',      help_command))
    app.add_handler(CommandHandler('contact',   contact))
    app.add_handler(CommandHandler('services',  services))
    app.add_handler(CommandHandler('resources', resources))
    app.add_handler(CommandHandler('clear',     clear_history))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("🚀 Light Solution Inc Bot is live!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
