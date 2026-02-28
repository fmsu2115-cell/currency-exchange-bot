import os
import logging
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
EXCHANGE_API_KEY = os.environ.get("EXCHANGE_API_KEY", "")

# Key currencies for BD users
KEY_CURRENCIES = ["USD", "EUR", "GBP", "CNY", "SAR", "AED", "MYR", "SGD", "JPY", "CAD", "AUD", "INR", "BDT"]

CURRENCY_FLAGS = {
    "USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "CNY": "🇨🇳",
    "SAR": "🇸🇦", "AED": "🇦🇪", "MYR": "🇲🇾", "SGD": "🇸🇬",
    "JPY": "🇯🇵", "CAD": "🇨🇦", "AUD": "🇦🇺", "INR": "🇮🇳",
    "BDT": "🇧🇩", "KWD": "🇰🇼", "QAR": "🇶🇦", "OMR": "🇴🇲",
    "CHF": "🇨🇭", "SEK": "🇸🇪", "NOK": "🇳🇴", "RUB": "🇷🇺"
}

CURRENCY_NAMES = {
    "USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound",
    "CNY": "Chinese Yuan (RMB)", "SAR": "Saudi Riyal", "AED": "UAE Dirham",
    "MYR": "Malaysian Ringgit", "SGD": "Singapore Dollar", "JPY": "Japanese Yen",
    "CAD": "Canadian Dollar", "AUD": "Australian Dollar", "INR": "Indian Rupee",
    "BDT": "Bangladeshi Taka", "KWD": "Kuwaiti Dinar", "QAR": "Qatari Riyal",
    "OMR": "Omani Rial", "CHF": "Swiss Franc"
}

def get_rates(base="BDT"):
    """Fetch exchange rates from API."""
    try:
        if EXCHANGE_API_KEY:
            url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{base}"
            r = requests.get(url, timeout=10)
            data = r.json()
            if data.get("result") == "success":
                return data["conversion_rates"]
        # Fallback: Frankfurter API (free, no key needed)
        url = f"https://api.frankfurter.app/latest?from={base}"
        r = requests.get(url, timeout=10)
        data = r.json()
        rates = data.get("rates", {})
        rates[base] = 1.0
        return rates
    except Exception as e:
        logger.error(f"Rate fetch error: {e}")
        return None

def format_rate(value):
    """Format rate nicely."""
    if value >= 100:
        return f"{value:,.2f}"
    elif value >= 1:
        return f"{value:.4f}"
    else:
        return f"{value:.6f}"

# ── /start ────────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("💱 Convert Currency", callback_data="help_convert"),
            InlineKeyboardButton("📊 All Rates to BDT", callback_data="all_rates"),
        ],
        [
            InlineKeyboardButton("🇺🇸 USD → BDT", callback_data="quick_USD"),
            InlineKeyboardButton("🇪🇺 EUR → BDT", callback_data="quick_EUR"),
        ],
        [
            InlineKeyboardButton("🇬🇧 GBP → BDT", callback_data="quick_GBP"),
            InlineKeyboardButton("🇸🇦 SAR → BDT", callback_data="quick_SAR"),
        ],
        [
            InlineKeyboardButton("🇨🇳 RMB → BDT", callback_data="quick_CNY"),
            InlineKeyboardButton("🇦🇪 AED → BDT", callback_data="quick_AED"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = (
        "🏦 *Currency Exchange BD Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "আপনাকে স্বাগতম! Welcome! 🎉\n\n"
        "I provide *real-time* exchange rates with a focus on BDT (Bangladeshi Taka).\n\n"
        "📌 *Quick Commands:*\n"
        "• /rate `USD BDT` — get exchange rate\n"
        "• /convert `100 USD BDT` — convert amount\n"
        "• /rates — all rates to BDT\n"
        "• /help — show all commands\n\n"
        "👇 Or tap a button below to get started:"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

# ── /help ─────────────────────────────────────────────────────────────────────
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📖 *How to Use Currency Exchange BD Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔹 *Get exchange rate:*\n"
        "`/rate USD BDT`\n"
        "`/rate EUR BDT`\n"
        "`/rate GBP USD`\n\n"
        "🔹 *Convert an amount:*\n"
        "`/convert 100 USD BDT`\n"
        "`/convert 500 EUR BDT`\n"
        "`/convert 1000 BDT USD`\n\n"
        "🔹 *All rates to BDT:*\n"
        "`/rates`\n\n"
        "🔹 *Rates from any base:*\n"
        "`/rates USD`\n"
        "`/rates EUR`\n\n"
        "💡 *Supported currencies:*\n"
        "USD 🇺🇸 EUR 🇪🇺 GBP 🇬🇧 CNY 🇨🇳\n"
        "SAR 🇸🇦 AED 🇦🇪 MYR 🇲🇾 SGD 🇸🇬\n"
        "JPY 🇯🇵 CAD 🇨🇦 AUD 🇦🇺 INR 🇮🇳\n"
        "BDT 🇧🇩 KWD 🇰🇼 QAR 🇶🇦 OMR 🇴🇲\n\n"
        "📡 Rates updated in real-time"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ── /rate ─────────────────────────────────────────────────────────────────────
async def rate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Usage: `/rate USD BDT`\nExample: `/rate EUR BDT`",
            parse_mode="Markdown"
        )
        return

    from_cur = args[0].upper()
    to_cur = args[1].upper()

    msg = await update.message.reply_text("⏳ Fetching rate...")

    rates = get_rates(from_cur)
    if not rates:
        await msg.edit_text("❌ Could not fetch rates. Please try again.")
        return

    if to_cur not in rates:
        await msg.edit_text(f"❌ Currency `{to_cur}` not found.", parse_mode="Markdown")
        return

    rate = rates[to_cur]
    from_flag = CURRENCY_FLAGS.get(from_cur, "🏳")
    to_flag = CURRENCY_FLAGS.get(to_cur, "🏳")
    from_name = CURRENCY_NAMES.get(from_cur, from_cur)
    to_name = CURRENCY_NAMES.get(to_cur, to_cur)
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    reply = (
        f"💱 *Exchange Rate*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{from_flag} *1 {from_cur}* = {to_flag} *{format_rate(rate)} {to_cur}*\n\n"
        f"📌 {from_name}\n"
        f"📌 {to_name}\n\n"
        f"🔄 *Quick conversions:*\n"
        f"• 10 {from_cur} = {format_rate(rate * 10)} {to_cur}\n"
        f"• 50 {from_cur} = {format_rate(rate * 50)} {to_cur}\n"
        f"• 100 {from_cur} = {format_rate(rate * 100)} {to_cur}\n"
        f"• 500 {from_cur} = {format_rate(rate * 500)} {to_cur}\n"
        f"• 1000 {from_cur} = {format_rate(rate * 1000)} {to_cur}\n\n"
        f"🕐 Updated: {now}"
    )
    await msg.edit_text(reply, parse_mode="Markdown")

# ── /convert ──────────────────────────────────────────────────────────────────
async def convert_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "❌ Usage: `/convert 100 USD BDT`\nExample: `/convert 500 SAR BDT`",
            parse_mode="Markdown"
        )
        return

    try:
        amount = float(args[0].replace(",", ""))
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Example: `/convert 100 USD BDT`", parse_mode="Markdown")
        return

    from_cur = args[1].upper()
    to_cur = args[2].upper()

    msg = await update.message.reply_text("⏳ Converting...")

    rates = get_rates(from_cur)
    if not rates:
        await msg.edit_text("❌ Could not fetch rates. Please try again.")
        return

    if to_cur not in rates:
        await msg.edit_text(f"❌ Currency `{to_cur}` not found.", parse_mode="Markdown")
        return

    rate = rates[to_cur]
    result = amount * rate
    from_flag = CURRENCY_FLAGS.get(from_cur, "🏳")
    to_flag = CURRENCY_FLAGS.get(to_cur, "🏳")
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    reply = (
        f"💰 *Currency Conversion*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{from_flag} *{amount:,.2f} {from_cur}*\n"
        f"⬇️\n"
        f"{to_flag} *{result:,.2f} {to_cur}*\n\n"
        f"📊 Rate: 1 {from_cur} = {format_rate(rate)} {to_cur}\n\n"
        f"🕐 Updated: {now}"
    )
    await msg.edit_text(reply, parse_mode="Markdown")

# ── /rates ────────────────────────────────────────────────────────────────────
async def rates_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    base = "BDT"
    if context.args:
        base = context.args[0].upper()

    msg = await update.message.reply_text(f"⏳ Fetching rates for {base}...")

    rates = get_rates(base)
    if not rates:
        await msg.edit_text("❌ Could not fetch rates. Please try again.")
        return

    base_flag = CURRENCY_FLAGS.get(base, "🏳")
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    lines = [
        f"📊 *Exchange Rates — Base: {base_flag} {base}*",
        f"━━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    # Show key currencies first
    shown = set()
    for cur in KEY_CURRENCIES:
        if cur == base or cur not in rates:
            continue
        flag = CURRENCY_FLAGS.get(cur, "🏳")
        val = rates[cur]
        name = CURRENCY_NAMES.get(cur, cur)
        lines.append(f"{flag} *{cur}* — {format_rate(val)}")
        shown.add(cur)

    lines.append("")
    lines.append(f"🕐 Updated: {now}")
    lines.append(f"💡 Use `/rate {base} USD` for detailed view")

    await msg.edit_text("\n".join(lines), parse_mode="Markdown")

# ── Callback buttons ──────────────────────────────────────────────────────────
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "all_rates":
        rates = get_rates("BDT")
        if not rates:
            await query.edit_message_text("❌ Could not fetch rates.")
            return
        now = datetime.now().strftime("%d %b %Y, %I:%M %p")
        lines = ["📊 *All Rates — Base: 🇧🇩 BDT*", "━━━━━━━━━━━━━━━━━━━━", ""]
        for cur in KEY_CURRENCIES:
            if cur == "BDT" or cur not in rates:
                continue
            flag = CURRENCY_FLAGS.get(cur, "🏳")
            val = rates[cur]
            lines.append(f"{flag} *{cur}* — {format_rate(val)}")
        lines += ["", f"🕐 {now}"]
        keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="all_rates")]]
        await query.edit_message_text(
            "\n".join(lines), parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("quick_"):
        cur = data.replace("quick_", "")
        rates = get_rates(cur)
        if not rates or "BDT" not in rates:
            await query.edit_message_text("❌ Could not fetch rate.")
            return
        rate = rates["BDT"]
        flag = CURRENCY_FLAGS.get(cur, "🏳")
        now = datetime.now().strftime("%d %b %Y, %I:%M %p")
        reply = (
            f"💱 *{flag} {cur} → 🇧🇩 BDT*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*1 {cur} = {format_rate(rate)} BDT*\n\n"
            f"🔄 *Quick conversions:*\n"
            f"• 10 {cur} = {format_rate(rate*10)} BDT\n"
            f"• 50 {cur} = {format_rate(rate*50)} BDT\n"
            f"• 100 {cur} = {format_rate(rate*100)} BDT\n"
            f"• 500 {cur} = {format_rate(rate*500)} BDT\n"
            f"• 1000 {cur} = {format_rate(rate*1000)} BDT\n\n"
            f"🕐 {now}"
        )
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data=f"quick_{cur}"),
             InlineKeyboardButton("🏠 Back to Menu", callback_data="back_home")]
        ]
        await query.edit_message_text(
            reply, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "back_home":
        keyboard = [
            [InlineKeyboardButton("💱 Convert Currency", callback_data="help_convert"),
             InlineKeyboardButton("📊 All Rates to BDT", callback_data="all_rates")],
            [InlineKeyboardButton("🇺🇸 USD → BDT", callback_data="quick_USD"),
             InlineKeyboardButton("🇪🇺 EUR → BDT", callback_data="quick_EUR")],
            [InlineKeyboardButton("🇬🇧 GBP → BDT", callback_data="quick_GBP"),
             InlineKeyboardButton("🇸🇦 SAR → BDT", callback_data="quick_SAR")],
            [InlineKeyboardButton("🇨🇳 RMB → BDT", callback_data="quick_CNY"),
             InlineKeyboardButton("🇦🇪 AED → BDT", callback_data="quick_AED")],
        ]
        msg = (
            "🏦 *Currency Exchange BD Bot*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "👇 Choose a currency or use commands:\n"
            "• /rate `USD BDT`\n"
            "• /convert `100 USD BDT`\n"
            "• /rates"
        )
        await query.edit_message_text(
            msg, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "help_convert":
        msg = (
            "💱 *How to Convert Currency*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Type this command:\n"
            "`/convert [amount] [from] [to]`\n\n"
            "📌 *Examples:*\n"
            "`/convert 100 USD BDT`\n"
            "`/convert 500 SAR BDT`\n"
            "`/convert 1000 BDT USD`\n"
            "`/convert 200 EUR GBP`\n\n"
            "Or get a rate:\n"
            "`/rate USD BDT`\n"
            "`/rate SAR BDT`"
        )
        keyboard = [[InlineKeyboardButton("🏠 Back to Menu", callback_data="back_home")]]
        await query.edit_message_text(
            msg, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ── Text message handler ──────────────────────────────────────────────────────
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()
    parts = text.split()

    # If user just types "USD BDT" or "USD TO BDT"
    if len(parts) == 2 and all(len(p) == 3 for p in parts):
        context.args = parts
        await rate_cmd(update, context)
        return

    if len(parts) == 3 and parts[1] == "TO":
        context.args = [parts[0], parts[2]]
        await rate_cmd(update, context)
        return

    # If user types "100 USD BDT"
    if len(parts) == 3:
        try:
            float(parts[0].replace(",",""))
            context.args = parts
            await convert_cmd(update, context)
            return
        except:
            pass

    await update.message.reply_text(
        "👋 I can help you with exchange rates!\n\n"
        "Try:\n"
        "• `/rate USD BDT`\n"
        "• `/convert 100 USD BDT`\n"
        "• `/rates`\n"
        "• Type `USD BDT` directly",
        parse_mode="Markdown"
    )

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN environment variable not set!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("rate", rate_cmd))
    app.add_handler(CommandHandler("convert", convert_cmd))
    app.add_handler(CommandHandler("rates", rates_cmd))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("✅ Currency Exchange BD Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
