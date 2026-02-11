"""
Telegram Bot Handlers
Handles all Telegram bot commands and messages
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from config import TELEGRAM_TOKEN

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global bot statistics
bot_stats = {
    "total_users": 0,
    "total_messages": 0,
    "start_date": datetime.now().strftime("%Y-%m-%d"),
    "broadcasts": [],
    "commands_log": []
}

# Main keyboard layout
MAIN_KEYBOARD = [
    [KeyboardButton("السنة الأولى")],
    [KeyboardButton("السنة الثانية")],
    [KeyboardButton("السنة الثالثة")],
    [KeyboardButton("السنة الرابعة")],
]


def get_main_keyboard():
    """Returns the main reply keyboard"""
    return ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)


def get_year_keyboard(year_id: str) -> InlineKeyboardMarkup:
    """Returns inline keyboard for year selection"""
    keyboard = [
        [InlineKeyboardButton("السنة الأولى", callback_data="year1")],
        [InlineKeyboardButton("السنة الثانية", callback_data="year2")],
        [InlineKeyboardButton("السنة الثالثة", callback_data="year3")],
        [InlineKeyboardButton("السنة الرابعة", callback_data="year4")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Returns back button keyboard"""
    keyboard = [
        [InlineKeyboardButton("رجوع", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def format_welcome_message() -> str:
    """Formats the welcome message"""
    return (
        "╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
        "┃   بوت اصول الدين     ┃\n"
        "┃      التعليمي        ┃\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "▸ اختر السنة الدراسية\n"
        "▸ اضغط على أحد الخيارات أدناه"
    )


def format_not_available_message() -> str:
    """Formats the not available message"""
    return (
        "╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
        "┃                     ┃\n"
        "┃   عذراً، غير متوفر ┃\n"
        "┃                     ┃\n"
        "┃  يرجى المحاولة      ┃\n"
        "┃  في وقت لاحق       ┃\n"
        "┃                     ┃\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.message.from_user
    logger.info(f"User {user.first_name} started the bot")
    
    bot_stats["total_users"] += 1
    bot_stats["commands_log"].append(f"[{datetime.now()}] User {user.first_name} started the bot")
    
    await update.message.reply_text(
        format_welcome_message(),
        reply_markup=get_main_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
▸ استخدم القائمة السفلية للاختيار
▸ اضغط على السنة الدراسية المطلوبة
▸ سيتم عرض المحتوى المتاح

/help - عرض هذه الرسالة
/start - إعادة تشغيل البوت
    """
    await update.message.reply_text(help_text)


async def handle_year_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle year selection from keyboard"""
    message_text = update.message.text
    user = update.message.from_user
    
    bot_stats["total_messages"] += 1
    bot_stats["commands_log"].append(f"[{datetime.now()}] User {user.first_name} selected: {message_text}")
    
    # Send appropriate response based on selection
    await update.message.reply_text(
        format_not_available_message(),
        reply_markup=get_back_keyboard()
    )


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    bot_stats["commands_log"].append(f"[{datetime.now()}] User {user.first_name} clicked: {query.data}")
    
    if query.data == "back_main":
        await query.edit_message_text(
            format_welcome_message(),
            reply_markup=get_main_keyboard()
        )
    else:
        await query.edit_message_text(
            format_not_available_message(),
            reply_markup=get_back_keyboard()
        )


def create_bot_application():
    """Create and configure the bot application"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_year_selection))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    return application
