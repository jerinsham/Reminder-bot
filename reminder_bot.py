import telebot
import time
import threading
from datetime import datetime
import json
import os
from telebot import types  # ✅ Needed for buttons

bot = telebot.TeleBot("7718694973:AAGlNMVOdDF7NN109J0rD9tyquuRenDYAlk")
FILE = "reminders.json"

def load_reminders():
    if os.path.exists(FILE):
        with open(FILE, 'r') as f:
            return json.load(f)
    return {}

def save_reminders():
    with open(FILE, 'w') as f:
        json.dump(user_reminders, f)

user_reminders = load_reminders()

# ✅ /start with buttons
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🕒 Set Reminder")
    btn2 = types.KeyboardButton("📋 My Reminders")
    btn3 = types.KeyboardButton("❌ Delete Reminder")
    markup.add(btn1, btn2, btn3)

    bot.send_message(message.chat.id,
        "👋 Welcome! Choose an option below:",
        reply_markup=markup)

# ✅ /remind with day support (Mon,Tue,Fri 07:00 Task)
@bot.message_handler(commands=['remind'])
def set_reminder(message):
    try:
        parts = message.text.split(' ', 3)
        days_part = parts[1]
        time_part = parts[2]
        task = parts[3]
        user_id = str(message.chat.id)

        days = [d.strip().lower() for d in days_part.split(',')]

        if user_id not in user_reminders:
            user_reminders[user_id] = []

        user_reminders[user_id].append([days, time_part, task])
        save_reminders()
        bot.reply_to(message, f"✅ Reminder set for {days_part} at {time_part}: {task}")
    except:
        bot.reply_to(message, "⚠️ Use: /remind Mon,Wed HH:MM Task")

# ✅ Show reminders
@bot.message_handler(commands=['myreminders'])
def show_reminders(message):
    user_id = str(message.chat.id)
    if user_id not in user_reminders or not user_reminders[user_id]:
        bot.reply_to(message, "📭 No reminders set.")
    else:
        text = "📝 Your Reminders:\n"
        for i, entry in enumerate(user_reminders[user_id], start=1):
            if len(entry) == 3:
                days, t, task = entry
                day_str = ','.join(days).capitalize()
                text += f"{i}. 📆 {day_str} ⏰ {t} - {task}\n"
        bot.reply_to(message, text)

# ✅ Delete reminder
@bot.message_handler(commands=['delete'])
def delete_reminder(message):
    user_id = str(message.chat.id)
    try:
        index = int(message.text.split()[1]) - 1
        if user_id in user_reminders and 0 <= index < len(user_reminders[user_id]):
            removed = user_reminders[user_id].pop(index)
            save_reminders()
            bot.reply_to(message, f"❌ Deleted: {removed[2]} at {removed[1]}")
        else:
            bot.reply_to(message, "❗ Invalid number.")
    except:
        bot.reply_to(message, "⚠️ Use: /delete number")

# ✅ Reminder checker (now checks weekday too)
def check_reminders():
    while True:
        now = datetime.now().strftime("%H:%M")
        today = datetime.now().strftime("%a").lower()
        for user_id in user_reminders:
            for entry in user_reminders[user_id]:
                if len(entry) == 3:
                    days, t, task = entry
                    if today[:3] in [d[:3] for d in days] and t == now:
                        bot.send_message(int(user_id), f"⏰ Reminder: {task}")
        time.sleep(60)

threading.Thread(target=check_reminders).start()

# ✅ Button handling
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    text = message.text

    if text == "📋 My Reminders":
        show_reminders(message)

    elif text == "❌ Delete Reminder":
        bot.reply_to(message, "ℹ️ To delete, type:\n/delete 1 (or the number of the reminder)")

    elif text == "🕒 Set Reminder":
        bot.reply_to(message, "📝 To set a reminder, type:\n/remind Mon,Wed HH:MM Task\nExample:\n/remind Mon,Fri 07:00 Study Math")

print("Bot is running...")
bot.polling()
