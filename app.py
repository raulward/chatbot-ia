from flask import Flask, request, jsonify

from bot.bot import AIBot
from services.waha import Waha


app = Flask(__name__)


@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    data = request.json

    if not data:
        print("❌ Nenhum dado recebido!")
        return jsonify({'status': 'error', 'message': 'Nenhum evento recebido.'}), 400

    print(f"📩 Evento recebido: {data}")

    waha = Waha()
    ai_bot = AIBot()

    try:
        chat_id = data['payload']['from']
        received_message = data['payload']['body']
        print(f"👤 ID do chat: {chat_id}")
        print(f"💬 Mensagem recebida: {received_message}")
    except KeyError as e:
        print(f"❌ Erro: Campo ausente {e}")
        return jsonify({'status': 'error', 'message': 'Formato de evento inválido'}), 400

    is_group = '@g.us' in chat_id
    is_status = 'status@broadcast' in chat_id

    if is_group or is_status:
        print("🚫 Mensagem ignorada (grupo ou status).")
        return jsonify({'status': 'success', 'message': 'Mensagem ignorada.'}), 200

    waha.start_typing(chat_id=chat_id)
    response = ai_bot.invoke(question=received_message)
    waha.send_message(chat_id=chat_id, message=response)
    waha.stop_typing(chat_id=chat_id)

    print(f"✅ Resposta enviada: {response}")

    return jsonify({'status': 'success'}), 200
