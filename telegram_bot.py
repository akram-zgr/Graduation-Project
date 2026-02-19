"""
University Academic Chatbot — Telegram Bot
Supports multi-university, multi-faculty, multi-department selection
flow driven entirely from the database.
"""

import os
import sys
import logging
import traceback
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db
from models.university import University
from models.faculty import Faculty
from models.department import Department
from services.knowledge_service import knowledge_service
from services.openai_service import generate_chat_response

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MAX_HISTORY_MESSAGES = 10          # keep last N turns in memory
CALLBACK_UNI    = "uni"            # callback prefix: university selection
CALLBACK_FAC    = "fac"            # callback prefix: faculty selection
CALLBACK_DEPT   = "dept"           # callback prefix: department selection
CALLBACK_SKIP   = "skip_dept"      # callback: skip department selection

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory session store
# Structure per user_id:
# {
#   "university_id":   int | None,
#   "university_name": str | None,
#   "faculty_id":      int | None,
#   "faculty_name":    str | None,
#   "department_id":   int | None,
#   "department_name": str | None,
#   "session_start":   datetime,
#   "history":         list[dict],   # [{role, content}, ...]
# }
# ---------------------------------------------------------------------------

sessions: dict[int, dict] = {}


def _new_session() -> dict:
    return {
        "university_id":   None,
        "university_name": None,
        "faculty_id":      None,
        "faculty_name":    None,
        "department_id":   None,
        "department_name": None,
        "session_start":   datetime.now(),
        "history":         [],
    }


def _session(user_id: int) -> dict:
    if user_id not in sessions:
        sessions[user_id] = _new_session()
    return sessions[user_id]


def _is_setup_complete(user_id: int) -> bool:
    s = sessions.get(user_id, {})
    return bool(s.get("university_id") and s.get("faculty_id"))


def _append_history(user_id: int, role: str, content: str) -> None:
    history = _session(user_id)["history"]
    history.append({"role": role, "content": content})
    if len(history) > MAX_HISTORY_MESSAGES:
        sessions[user_id]["history"] = history[-MAX_HISTORY_MESSAGES:]


def _session_summary(user_id: int) -> str:
    s = sessions.get(user_id, {})
    lines = []
    if s.get("university_name"):
        lines.append(f"🏛 University : {s['university_name']}")
    if s.get("faculty_name"):
        lines.append(f"🏫 Faculty    : {s['faculty_name']}")
    if s.get("department_name"):
        lines.append(f"📂 Department : {s['department_name']}")
    return "\n".join(lines) if lines else "No active session."


# ---------------------------------------------------------------------------
# Keyboard builders  (all DB calls are wrapped in app_context)
# ---------------------------------------------------------------------------

def _build_university_keyboard(app) -> InlineKeyboardMarkup | None:
    with app.app_context():
        unis = (
            University.query
            .filter_by(is_active=True)
            .order_by(University.name)
            .all()
        )
        if not unis:
            return None
        keyboard = [
            [InlineKeyboardButton(
                f"🏛 {u.name}" + (f"  ({u.city})" if u.city else ""),
                callback_data=f"{CALLBACK_UNI}_{u.id}",
            )]
            for u in unis
        ]
        return InlineKeyboardMarkup(keyboard)


def _build_faculty_keyboard(app, university_id: int) -> InlineKeyboardMarkup | None:
    with app.app_context():
        faculties = (
            Faculty.query
            .filter_by(university_id=university_id, is_active=True)
            .order_by(Faculty.name)
            .all()
        )
        if not faculties:
            return None
        keyboard = [
            [InlineKeyboardButton(
                f"🏫 {f.name}",
                callback_data=f"{CALLBACK_FAC}_{f.id}",
            )]
            for f in faculties
        ]
        return InlineKeyboardMarkup(keyboard)


def _build_department_keyboard(app, faculty_id: int) -> InlineKeyboardMarkup | None:
    with app.app_context():
        depts = (
            Department.query
            .filter_by(faculty_id=faculty_id, is_active=True)
            .order_by(Department.name)
            .all()
        )
        if not depts:
            return None
        keyboard = [
            [InlineKeyboardButton(
                f"📂 {d.name}",
                callback_data=f"{CALLBACK_DEPT}_{d.id}",
            )]
            for d in depts
        ]
        # Allow user to skip department and proceed without selecting one
        keyboard.append([
            InlineKeyboardButton("⏭ Skip (no specific department)", callback_data=CALLBACK_SKIP)
        ])
        return InlineKeyboardMarkup(keyboard)


# ---------------------------------------------------------------------------
# /start  — step 1: choose university
# ---------------------------------------------------------------------------

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    sessions[user_id] = _new_session()          # fresh session on every /start

    try:
        from app import app
        markup = _build_university_keyboard(app)

        if markup is None:
            await update.message.reply_text(
                "⚠️ No universities are currently available. Please try again later."
            )
            return

        await update.message.reply_text(
            "🎓 *Welcome to the University Academic Chatbot!*\n\n"
            "I can help you with course registration, grades, fees, campus facilities, "
            "exams, and more.\n\n"
            "*Step 1 of 3 — Please select your university:*",
            parse_mode="Markdown",
            reply_markup=markup,
        )

    except Exception:
        logger.exception("Error in /start")
        await update.message.reply_text(
            "❌ Something went wrong. Please try /start again."
        )


# ---------------------------------------------------------------------------
# Callback: university selected  — step 2: choose faculty
# ---------------------------------------------------------------------------

async def _handle_university_selected(
    query, user_id: int, university_id: int
) -> None:
    try:
        from app import app
        with app.app_context():
            uni = University.query.get(university_id)
            if not uni or not uni.is_active:
                await query.edit_message_text("❌ University not found. Please /start again.")
                return

            sessions[user_id]["university_id"]   = uni.id
            sessions[user_id]["university_name"] = uni.name

        markup = _build_faculty_keyboard(app, university_id)

        if markup is None:
            # No faculties → skip straight to ready
            sessions[user_id]["faculty_id"]   = None
            sessions[user_id]["faculty_name"] = "N/A"
            await query.edit_message_text(
                f"✅ *University selected:* {uni.name}\n\n"
                "ℹ️ No faculties are registered for this university yet.\n\n"
                "You can now ask me anything about your institution!",
                parse_mode="Markdown",
            )
            return

        await query.edit_message_text(
            f"✅ *University:* {uni.name}\n\n"
            "*Step 2 of 3 — Please select your faculty:*",
            parse_mode="Markdown",
            reply_markup=markup,
        )

    except Exception:
        logger.exception("Error handling university selection")
        await query.edit_message_text("❌ Error. Please /start again.")


# ---------------------------------------------------------------------------
# Callback: faculty selected  — step 3: choose department
# ---------------------------------------------------------------------------

async def _handle_faculty_selected(
    query, user_id: int, faculty_id: int
) -> None:
    try:
        from app import app
        with app.app_context():
            fac = Faculty.query.get(faculty_id)
            if not fac or not fac.is_active:
                await query.edit_message_text("❌ Faculty not found. Please /start again.")
                return

            sessions[user_id]["faculty_id"]   = fac.id
            sessions[user_id]["faculty_name"] = fac.name

        uni_name = sessions[user_id].get("university_name", "")
        markup = _build_department_keyboard(app, faculty_id)

        if markup is None:
            # No departments → skip to ready
            sessions[user_id]["department_id"]   = None
            sessions[user_id]["department_name"] = "N/A"
            await query.edit_message_text(
                f"✅ *University:* {uni_name}\n"
                f"✅ *Faculty:* {fac.name}\n\n"
                "ℹ️ No departments are registered for this faculty yet.\n\n"
                "You're all set! Ask me anything 🎓",
                parse_mode="Markdown",
            )
            return

        await query.edit_message_text(
            f"✅ *University:* {uni_name}\n"
            f"✅ *Faculty:* {fac.name}\n\n"
            "*Step 3 of 3 — Please select your department:*",
            parse_mode="Markdown",
            reply_markup=markup,
        )

    except Exception:
        logger.exception("Error handling faculty selection")
        await query.edit_message_text("❌ Error. Please /start again.")


# ---------------------------------------------------------------------------
# Callback: department selected  — setup complete
# ---------------------------------------------------------------------------

async def _handle_department_selected(
    query, user_id: int, department_id: int
) -> None:
    try:
        from app import app
        with app.app_context():
            dept = Department.query.get(department_id)
            if not dept or not dept.is_active:
                await query.edit_message_text("❌ Department not found. Please /start again.")
                return

            sessions[user_id]["department_id"]   = dept.id
            sessions[user_id]["department_name"] = dept.name

        s = sessions[user_id]
        await query.edit_message_text(
            f"🎉 *Setup complete!*\n\n"
            f"🏛 *University :* {s['university_name']}\n"
            f"🏫 *Faculty    :* {s['faculty_name']}\n"
            f"📂 *Department :* {s['department_name']}\n\n"
            "I'm ready to help you. Ask me anything about your academic journey!\n\n"
            "_Use /status to review your selection or /reset to start over._",
            parse_mode="Markdown",
        )

    except Exception:
        logger.exception("Error handling department selection")
        await query.edit_message_text("❌ Error. Please /start again.")


# ---------------------------------------------------------------------------
# Callback: skip department
# ---------------------------------------------------------------------------

async def _handle_skip_department(query, user_id: int) -> None:
    sessions[user_id]["department_id"]   = None
    sessions[user_id]["department_name"] = None

    s = sessions[user_id]
    await query.edit_message_text(
        f"✅ *Setup complete!*\n\n"
        f"🏛 *University :* {s['university_name']}\n"
        f"🏫 *Faculty    :* {s['faculty_name']}\n"
        f"📂 *Department :* Not specified\n\n"
        "I'm ready to help you. Ask me anything!\n\n"
        "_Use /status to review your selection or /reset to start over._",
        parse_mode="Markdown",
    )


# ---------------------------------------------------------------------------
# Main callback router
# ---------------------------------------------------------------------------

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data    = query.data

    if data.startswith(f"{CALLBACK_UNI}_"):
        uni_id = int(data.split("_", 1)[1])
        await _handle_university_selected(query, user_id, uni_id)

    elif data.startswith(f"{CALLBACK_FAC}_"):
        fac_id = int(data.split("_", 1)[1])
        await _handle_faculty_selected(query, user_id, fac_id)

    elif data.startswith(f"{CALLBACK_DEPT}_"):
        dept_id = int(data.split("_", 1)[1])
        await _handle_department_selected(query, user_id, dept_id)

    elif data == CALLBACK_SKIP:
        await _handle_skip_department(query, user_id)

    else:
        await query.edit_message_text("❓ Unknown action. Please /start again.")


# ---------------------------------------------------------------------------
# /help
# ---------------------------------------------------------------------------

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    summary = _session_summary(user_id)

    await update.message.reply_text(
        f"🤖 *University Academic Chatbot — Help*\n\n"
        f"*Your current session:*\n{summary}\n\n"
        "*What I can help with:*\n"
        "📚 Course registration & enrollment\n"
        "💰 Tuition fees & payments\n"
        "📊 Grades & academic records\n"
        "🏢 Campus facilities & services\n"
        "📝 Exams & schedules\n"
        "🎫 Student services & ID cards\n\n"
        "*Commands:*\n"
        "/start  — Select university › faculty › department\n"
        "/status — Show your current session details\n"
        "/reset  — Clear session and start over\n"
        "/help   — Show this message\n\n"
        "💬 Supports Arabic, English and French.",
        parse_mode="Markdown",
    )


# ---------------------------------------------------------------------------
# /status
# ---------------------------------------------------------------------------

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    s = sessions.get(user_id)

    if not s or not s.get("university_id"):
        await update.message.reply_text(
            "❌ No active session.\nUse /start to set up your profile."
        )
        return

    duration   = datetime.now() - s["session_start"]
    minutes    = int(duration.total_seconds() / 60)
    msg_count  = len(s["history"])

    await update.message.reply_text(
        f"📊 *Session Status*\n\n"
        f"🏛 University  : {s.get('university_name', '—')}\n"
        f"🏫 Faculty     : {s.get('faculty_name') or 'Not selected'}\n"
        f"📂 Department  : {s.get('department_name') or 'Not selected'}\n"
        f"⏱ Duration    : {minutes} minute(s)\n"
        f"💬 Messages    : {msg_count // 2} exchange(s)\n\n"
        "_Use /reset to start a new session._",
        parse_mode="Markdown",
    )


# ---------------------------------------------------------------------------
# /reset
# ---------------------------------------------------------------------------

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    s = sessions.get(user_id, {})

    # Build a short farewell summary
    lines = []
    if s.get("university_name"):
        lines.append(f"🏛 {s['university_name']}")
    if s.get("faculty_name") and s["faculty_name"] != "N/A":
        lines.append(f"🏫 {s['faculty_name']}")
    if s.get("department_name") and s["department_name"] not in (None, "N/A"):
        lines.append(f"📂 {s['department_name']}")

    if s.get("session_start"):
        duration = datetime.now() - s["session_start"]
        minutes  = int(duration.total_seconds() / 60)
        lines.append(f"⏱ Session lasted {minutes} minute(s)")

    sessions[user_id] = _new_session()

    summary = "\n".join(lines) if lines else "No previous session."
    await update.message.reply_text(
        f"🔄 *Session reset.*\n\n{summary}\n\n"
        "Use /start to select your university and begin a new session.",
        parse_mode="Markdown",
    )


# ---------------------------------------------------------------------------
# Message handler — AI response
# ---------------------------------------------------------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id      = update.effective_user.id
    user_message = update.message.text

    # Guard: setup must be complete
    if not _is_setup_complete(user_id):
        await update.message.reply_text(
            "⚠️ Please complete your profile first.\n"
            "Use /start to select your university and faculty."
        )
        return

    s = _session(user_id)

    try:
        from app import app
        with app.app_context():
            university_id = s["university_id"]

            # Fetch university context and relevant KB entries
            university_context = knowledge_service.get_university_context(university_id)
            knowledge_results  = knowledge_service.search_knowledge(
                user_message, university_id, limit=3
            )

            knowledge_context = None
            if knowledge_results:
                pieces = [
                    f"- {r['title']}: {r['content'][:300]}"
                    for r in knowledge_results
                ]
                knowledge_context = "\n".join(pieces)

        # Record user turn
        _append_history(user_id, "user", user_message)

        # Generate AI response
        ai_response, _ = generate_chat_response(
            s["history"],
            university_context=university_context,
            knowledge_context=knowledge_context,
        )

        # Record assistant turn
        _append_history(user_id, "assistant", ai_response)

        await update.message.reply_text(ai_response)

    except Exception:
        logger.exception("Error generating response for user %s", user_id)
        await update.message.reply_text(
            "❌ Sorry, I encountered an error. Please try again or use /reset."
        )


# ---------------------------------------------------------------------------
# Global error handler
# ---------------------------------------------------------------------------

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Unhandled exception: %s", context.error, exc_info=context.error)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def create_telegram_application():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set.")

    telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    telegram_app.add_handler(CommandHandler("start",  start_command))
    telegram_app.add_handler(CommandHandler("help",   help_command))
    telegram_app.add_handler(CommandHandler("reset",  reset_command))
    telegram_app.add_handler(CommandHandler("status", status_command))
    telegram_app.add_handler(CallbackQueryHandler(callback_router))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    telegram_app.add_error_handler(error_handler)

    return telegram_app


