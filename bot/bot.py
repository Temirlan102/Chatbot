import logging
import requests
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

logging.basicConfig(level=logging.INFO)

appointments = {}

available_dates = ["Monday 14:00", "Tuesday 15:00", "Wednesday 11:30", "Thursday 12:00", "Friday 14:30"]

BACKEND_URL = "https://chatbot-snowy-psi.vercel.app/api"

STICKER_SUCCESS = "CAACAgUAAxkBAAICgGabcdEXAMPLE"
STICKER_CANCEL = "CAACAgUAAxkBAAICgWaabcdEXAMPLE"

def build_date_keyboard(user_id):
    keyboard = []

    for date in available_dates:
        if appointments.get(user_id) == date:
            text = f"🔴 {date} (selected)"
        elif date in appointments.values():
            text = f"❌ ~~{date} (booked)~~"
        else:
            text = f"🟢 {date} (free)"

        keyboard.append([
            InlineKeyboardButton(text=text, callback_data=f"DATE_{date}")
        ])

    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I can help you book an appointment.\n"
        "Use /book to begin.\nUse /help to see all commands."
    )

async def miniapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                text="Open Mini App",
                web_app=WebAppInfo(url="https://chatbot-snowy-psi.vercel.app/")
            )
        ]
    ]

    await update.message.reply_text(
        "Open the Mini App below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 *Available Commands:*\n\n"
        "/start – Welcome message\n"
        "/help – Show all commands\n"
        "/book – Book an appointment\n"
        "/view – View your appointment\n"
        "/edit – Change your appointment\n"
        "/miniapp – Open Web App to see appointment\n"
        "/cancel – Cancel your appointment\n",
        parse_mode="Markdown"
    )


async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    await update.message.reply_text(
        "📅 Please choose a date:",
        reply_markup=build_date_keyboard(user_id)
    )


async def view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    appt = appointments.get(update.message.chat_id)

    if not appt:
        await update.message.reply_text("😕 You don't have any appointment yet.")
    else:
        await update.message.reply_text(f"📌 Your appointment: *{appt}*", parse_mode="Markdown")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    if user_id in appointments:
        del appointments[user_id]
        await update.message.reply_text("❌ Your appointment was cancelled.")

        try:
            await update.message.reply_sticker(STICKER_CANCEL)
        except:
            pass
    else:
        await update.message.reply_text("You have no appointment to cancel.")


async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await book(update, context)


async def on_date_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.message.chat_id
    selected_date = query.data.replace("DATE_", "")
    date_part, time_part = selected_date.split()    

    try:
        backend_slots = requests.get(f"{BACKEND_URL}/slots").json()
    except:
        await query.edit_message_text("❌ Backend unavailable.")
        return

    slot = next((s for s in backend_slots if s["date"] == date_part and s["time"] == time_part), None)

    if not slot:
        await query.edit_message_text(f"❌ Slot *{selected_date}* not found.", parse_mode="Markdown")
        return

    slot_id = slot["id"]

    response = requests.post(
        f"{BACKEND_URL}/book",
        json={"slotId": slot_id, "user": user_id}
    )

    if response.status_code != 200:
        await query.edit_message_text(f"❌ {response.json().get('error', 'Booking failed')}")
        return

    appointments[user_id] = selected_date

    await query.edit_message_text(
        f"🎉 Appointment booked for *{selected_date}*!\n"
        f"Use /view to see it or /edit to change.",
        parse_mode="Markdown"
    )

    try:
        await query.message.reply_sticker(STICKER_SUCCESS)
    except:
        pass

def main():
    app = Application.builder().token("8558046922:AAFaaLo109S3ompgqYK-Q3pcTaYGkCVNBbs").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("book", book))
    app.add_handler(CommandHandler("view", view))
    app.add_handler(CommandHandler("edit", edit))
    app.add_handler(CommandHandler("miniapp", miniapp))
    app.add_handler(CommandHandler("cancel", cancel))

    app.add_handler(CallbackQueryHandler(on_date_selected))

    app.run_polling()


if __name__ == "__main__":
    main()
