from flask import Flask, request, jsonify
import os

app = Flask(__name__)

ADMIN_ID = U7974bab51efca36d881fc5e6fb11f502  # 管理者のLINE ID
blacklist = set()  # ブラックリスト
invite_tracker = {}  # 招待を記録する辞書

@app.route("/", methods=["GET"])
def home():
    return "LINE Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "events" in data:
        for event in data["events"]:
            event_type = event["type"]
            user_id = event["source"]["userId"]
            group_id = event["source"].get("groupId")

            # ✅ 管理者以外がメッセージを送ったら強制退会
            if event_type == "message" and user_id != ADMIN_ID:
                kick_user(group_id, user_id)

            # ✅ 新しいメンバーが参加したらルール確認 & ノート確認を促す
            elif event_type == "memberJoined":
                mention_user(group_id, user_id, "グループへようこそ！ノートを確認してください。")
                invite_tracker[user_id] = group_id  # 招待記録

            # ✅ 誰かが退会させられたら、その人をブラックリストに追加 & 強制退会
            elif event_type == "memberLeft":
                if user_id in invite_tracker:  # もし直前に招待された人が退会していたら強制退会
                    blacklist.add(user_id)
                    send_message(group_id, f"招待キャンセルが検出されました。{user_id} を強制退会しました。")
                    kick_user(group_id, user_id)
                    del invite_tracker[user_id]

    return jsonify({"status": "ok"})

def send_message(group_id, text):
    """ LINEグループにメッセージを送る """
    print(f"メッセージ送信: {text}")

def mention_user(group_id, user_id, text):
    """ 新メンバーをメンションしてメッセージを送る """
    mention_text = f"@{user_id} {text}"
    send_message(group_id, mention_text)

def kick_user(group_id, user_id):
    """ ユーザーを強制退会させる """
    print(f"強制退会: {user_id}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
