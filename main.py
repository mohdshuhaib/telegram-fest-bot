import os
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import threading
import uvicorn

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InputMediaDocument,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

import asyncio

# Replace with your real bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# === Student Data ===
class_1_students = {
    "Shuhaib": ['BQACAgUAAxkBAAEBXiRoN2J3nQcYgNkkrTEnJWs8aQRNlgACGhcAAhVEuVUcgqcCNOYKyjYE'],
    "Dilshad": ['BQACAgUAAxkBAAEBXhloN2G8uOOpKj4RwtId7YrrlxGjbQACERcAAhVEuVUDa__TFoW36DYE'],
    "Davood": ['BQACAgUAAxkBAAEBXhpoN2G82lyuuxxPjAgAAfaT6UVTsz8AAhIXAAIVRLlVGsL-4LHLDi02BA'],
    "Fasilu EC": ['BQACAgUAAxkBAAEBXh5oN2Im6dDgwEplCnRq-UEuZvxhvAACFBcAAhVEuVWxlwjMhrxGljYE'],
    "Swalih KC": ['BQACAgUAAxkBAAEBXiBoN2J3RvX4hEi0baQSMY6-Bk-oCwACFhcAAhVEuVUJfz0rd94fwzYE'],
}

class_2_students = class_1_students.copy()
class_3_students = class_1_students.copy()
class_4_students = class_1_students.copy()
class_5_students = class_1_students.copy()
class_6_students = class_1_students.copy()

DATA = {
    "Staff": {
        "Alice": [
            'BQACAgUAAxkBAAEBXiRoN2J3nQcYgNkkrTEnJWs8aQRNlgACGhcAAhVEuVUcgqcCNOYKyjYE',
            'BQACAgUAAxkBAAEBXhloN2G8uOOpKj4RwtId7YrrlxGjbQACERcAAhVEuVUDa__TFoW36DYE',
            'BQACAgUAAxkBAAEBXh5oN2Im6dDgwEplCnRq-UEuZvxhvAACFBcAAhVEuVWxlwjMhrxGljYE',
            'BQACAgUAAxkBAAEBXiBoN2J3RvX4hEi0baQSMY6-Bk-oCwACFhcAAhVEuVUJfz0rd94fwzYE',
            'BQACAgUAAxkBAAEBXhpoN2G82lyuuxxPjAgAAfaT6UVTsz8AAhIXAAIVRLlVGsL-4LHLDi02BA',
            'BQACAgUAAxkBAAEBXhpoN2G82lyuuxxPjAgAAfaT6UVTsz8AAhIXAAIVRLlVGsL-4LHLDi02BA',
            'BQACAgUAAxkBAAEBXhpoN2G82lyuuxxPjAgAAfaT6UVTsz8AAhIXAAIVRLlVGsL-4LHLDi02BA',
            'BQACAgUAAxkBAAEBXh5oN2Im6dDgwEplCnRq-UEuZvxhvAACFBcAAhVEuVWxlwjMhrxGljYE',
            'BQACAgUAAxkBAAEBXh5oN2Im6dDgwEplCnRq-UEuZvxhvAACFBcAAhVEuVWxlwjMhrxGljYE',
            'BQACAgUAAxkBAAEBXh5oN2Im6dDgwEplCnRq-UEuZvxhvAACFBcAAhVEuVWxlwjMhrxGljYE',
            'BQACAgUAAxkBAAEBXh5oN2Im6dDgwEplCnRq-UEuZvxhvAACFBcAAhVEuVWxlwjMhrxGljYE',
            'BQACAgUAAxkBAAEBXh5oN2Im6dDgwEplCnRq-UEuZvxhvAACFBcAAhVEuVWxlwjMhrxGljYE',
            # Add more to test pagination (>5)
        ],
        "Bob": [
            'BQACAgUAAxkBAAEBXiRoN2J3nQcYgNkkrTEnJWs8aQRNlgACGhcAAhVEuVUcgqcCNOYKyjYE'
        ]
    },
    "Guest": {
        "Grace": ['BQACAgUAAxkBAAEBXiBoN2J3RvX4hEi0baQSMY6-Bk-oCwACFhcAAhVEuVUJfz0rd94fwzYE'],
        "Heidi": ['BQACAgUAAxkBAAEBXiBoN2J3RvX4hEi0baQSMY6-Bk-oCwACFhcAAhVEuVUJfz0rd94fwzYE']
    },
    "Students": {
        "Class 1": class_1_students,
        "Class 2": class_2_students,
        "Class 3": class_3_students,
        "Class 4": class_4_students,
        "Class 5": class_5_students,
        "Class 6": class_6_students
    }
}

# === Keep Alive Server for UptimeRobot ===
app_fastapi = FastAPI()

@app_fastapi.get("/", response_class=PlainTextResponse)
def read_root():
    return "Bot is alive"

def run_server():
    uvicorn.run(app_fastapi, host="0.0.0.0", port=8000)

def keep_alive():
    thread = threading.Thread(target=run_server)
    thread.start()


PAGE_SIZE = 5  # Show 5 docs per page

def build_keyboard_from_list(items, add_back=True, back_text="Back"):
    keyboard = [[item] for item in items]
    if add_back:
        keyboard.append([back_text, "Main Menu"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

main_menu = ["Staff", "Guest", "Students"]
main_menu_markup = build_keyboard_from_list(main_menu, add_back=False)

def get_inline_pagination_keyboard(current_page, total_pages):
    if total_pages <= 1:
        return None  # No pagination if only 1 page
    buttons = []
    if current_page > 0:
        buttons.append(InlineKeyboardButton("◀️ Prev", callback_data="prev"))
    buttons.append(InlineKeyboardButton(f"Page {current_page + 1} / {total_pages}", callback_data="status"))
    if current_page < total_pages - 1:
        buttons.append(InlineKeyboardButton("Next ▶️", callback_data="next"))
    buttons.append(InlineKeyboardButton("Back", callback_data="back"))
    return InlineKeyboardMarkup([buttons])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔝 Main Menu", reply_markup=main_menu_markup)
    context.user_data.clear()
    context.user_data["last_level"] = "main"

async def send_page_documents(chat_id, bot, files, page, context):
    """Send PAGE_SIZE files for the page, save message_ids for deletion later."""
    start = page * PAGE_SIZE
    end = min(start + PAGE_SIZE, len(files))
    message_ids = []

    # Send all docs concurrently
    send_tasks = [bot.send_document(chat_id, files[i]) for i in range(start, end)]
    results = await asyncio.gather(*send_tasks)

    for msg in results:
        message_ids.append(msg.message_id)

    # Send pagination only if needed
    total_pages = (len(files) + PAGE_SIZE - 1) // PAGE_SIZE
    pagination_markup = get_inline_pagination_keyboard(page, total_pages)
    if pagination_markup:
        pag_msg = await bot.send_message(
            chat_id,
            text=f"Page {page + 1} of {total_pages}",
            reply_markup=pagination_markup
        )
        message_ids.append(pag_msg.message_id)

    context.user_data["last_page_messages"] = message_ids

async def delete_messages(chat_id, bot, message_ids):
    """Delete messages concurrently."""
    if not message_ids:
        return
    delete_tasks = [bot.delete_message(chat_id, mid) for mid in message_ids]
    await asyncio.gather(*delete_tasks, return_exceptions=True)  # handle some failures silently

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat.id
    bot = context.bot

    # Handle main menu selections
    if text == "Staff":
        names = list(DATA["Staff"].keys())
        kb = build_keyboard_from_list(names)
        await update.message.reply_text("👨‍💼 Staff Members:", reply_markup=kb)
        context.user_data["last_level"] = "staff_names"
        return

    if text == "Guest":
        names = list(DATA["Guest"].keys())
        kb = build_keyboard_from_list(names)
        await update.message.reply_text("👥 Guests:", reply_markup=kb)
        context.user_data["last_level"] = "guest_names"
        return

    if text == "Students":
        classes = list(DATA["Students"].keys())
        kb = build_keyboard_from_list(classes)
        await update.message.reply_text("📚 Student Classes:", reply_markup=kb)
        context.user_data["last_level"] = "classes"
        return

    # Handle Back button
    if text == "Back":
        last = context.user_data.get("last_level")
        if last in ["staff_names", "guest_names", "classes"]:
            await update.message.reply_text("🔝 Main Menu", reply_markup=main_menu_markup)
            context.user_data["last_level"] = "main"
        elif last == "students_in_class":
            await update.message.reply_text("📚 Student Classes:",
                                            reply_markup=build_keyboard_from_list(DATA["Students"].keys()))
            context.user_data["last_level"] = "classes"
        elif last == "student_names":
            class_name = context.user_data.get("current_class")
            if class_name:
                students = list(DATA["Students"][class_name].keys())
                await update.message.reply_text(f"👨‍🎓 Students in {class_name}:",
                                                reply_markup=build_keyboard_from_list(students))
                context.user_data["last_level"] = "students_in_class"
        elif last == "viewing_files":
            current_class = context.user_data.get("current_class")
            if current_class == "Staff":
                names = list(DATA["Staff"].keys())
                kb = build_keyboard_from_list(names)
                await update.message.reply_text("👨‍💼 Staff Members:", reply_markup=kb)
                context.user_data["last_level"] = "staff_names"
            elif current_class == "Guest":
                names = list(DATA["Guest"].keys())
                kb = build_keyboard_from_list(names)
                await update.message.reply_text("👥 Guests:", reply_markup=kb)
                context.user_data["last_level"] = "guest_names"
            else:
                # Assume students
                class_name = current_class
                students = list(DATA["Students"].get(class_name, {}).keys())
                kb = build_keyboard_from_list(students)
                await update.message.reply_text(f"👨‍🎓 Students in {class_name}:", reply_markup=kb)
                context.user_data["last_level"] = "students_in_class"
        return

    # Main Menu button
    if text == "Main Menu":
        await update.message.reply_text("🔝 Main Menu", reply_markup=main_menu_markup)
        context.user_data["last_level"] = "main"
        return

    # Staff clicked
    if text in DATA["Staff"]:
        file_ids = DATA["Staff"][text]
        context.user_data["current_files"] = file_ids
        context.user_data["media_page"] = 0
        context.user_data["current_student"] = text
        context.user_data["current_class"] = "Staff"
        context.user_data["last_level"] = "viewing_files"
        # Delete old page messages if any
        last_msgs = context.user_data.get("last_page_messages", [])
        for mid in last_msgs:
            try:
                await bot.delete_message(chat_id, mid)
            except:
                pass
        await send_page_documents(chat_id, bot, file_ids, 0, context)
        return

    # Guest clicked
    if text in DATA["Guest"]:
        file_ids = DATA["Guest"][text]
        context.user_data["current_files"] = file_ids
        context.user_data["media_page"] = 0
        context.user_data["current_student"] = text
        context.user_data["current_class"] = "Guest"
        context.user_data["last_level"] = "viewing_files"
        last_msgs = context.user_data.get("last_page_messages", [])
        for mid in last_msgs:
            try:
                await bot.delete_message(chat_id, mid)
            except:
                pass
        await send_page_documents(chat_id, bot, file_ids, 0, context)
        return

    # Class clicked
    if text in DATA["Students"]:
        class_name = text
        students = list(DATA["Students"][class_name].keys())
        await update.message.reply_text(f"👨‍🎓 Students in {class_name}:",
                                        reply_markup=build_keyboard_from_list(students))
        context.user_data["current_class"] = class_name
        context.user_data["last_level"] = "students_in_class"
        return

    # Student clicked
    current_class = context.user_data.get("current_class")
    if current_class and text in DATA["Students"].get(current_class, {}):
        file_ids = DATA["Students"][current_class][text]
        context.user_data["current_files"] = file_ids
        context.user_data["media_page"] = 0
        context.user_data["current_student"] = text
        context.user_data["last_level"] = "viewing_files"
        last_msgs = context.user_data.get("last_page_messages", [])
        for mid in last_msgs:
            try:
                await bot.delete_message(chat_id, mid)
            except:
                pass
        await send_page_documents(chat_id, bot, file_ids, 0, context)
        return

    await update.message.reply_text("❓ Unknown option. Please choose from the menu.")

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat.id
    bot = context.bot

    if "current_files" not in context.user_data:
        await query.message.reply_text("⚠️ No files to paginate.")
        return

    files = context.user_data["current_files"]
    current_page = context.user_data.get("media_page", 0)
    total_pages = (len(files) + PAGE_SIZE - 1) // PAGE_SIZE

    if data in ("next", "prev"):
        last_msgs = context.user_data.get("last_page_messages", [])
        await delete_messages(chat_id, bot, last_msgs)

        if data == "next" and current_page < total_pages - 1:
            current_page += 1
        elif data == "prev" and current_page > 0:
            current_page -= 1

        context.user_data["media_page"] = current_page
        await send_page_documents(chat_id, bot, files, current_page, context)

    elif data == "back":
        last_msgs = context.user_data.get("last_page_messages", [])
        await delete_messages(chat_id, bot, last_msgs)

        last_level = context.user_data.get("last_level", "main")
        if last_level == "viewing_files":
            current_class = context.user_data.get("current_class")
            if current_class == "Staff":
                names = list(DATA["Staff"].keys())
                kb = build_keyboard_from_list(names)
                await bot.send_message(chat_id, "👨‍💼 Staff Members:", reply_markup=kb)
                context.user_data["last_level"] = "staff_names"
            elif current_class == "Guest":
                names = list(DATA["Guest"].keys())
                kb = build_keyboard_from_list(names)
                await bot.send_message(chat_id, "👥 Guests:", reply_markup=kb)
                context.user_data["last_level"] = "guest_names"
            else:
                class_name = current_class
                students = list(DATA["Students"].get(class_name, {}).keys())
                kb = build_keyboard_from_list(students)
                await bot.send_message(chat_id, f"👨‍🎓 Students in {class_name}:", reply_markup=kb)
                context.user_data["last_level"] = "students_in_class"
        else:
            await bot.send_message(chat_id, "🔝 Main Menu", reply_markup=main_menu_markup)
            context.user_data["last_level"] = "main"

    elif data == "status":
        await query.answer(f"You are on page {current_page + 1} of {total_pages}", show_alert=False)

def main():
    keep_alive()  # start FastAPI server for uptime monitoring

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()



