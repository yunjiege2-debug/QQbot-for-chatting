import asyncio
import websockets
import json
import ollama
import httpx

# ===================== Configuration =====================
NAPCAT_WS_URL = "ws://127.0.0.1:3001"
OLLAMA_MODEL = "gpt-oss:20b"          #model name

SYSTEM_PROMPT = "you are a cute 18 years girl"

ALLOWED_USERS = {""} # enter allowed users in your group that can interact with the bot if you want
BOT_QQ = "" # enter the bot QQ number

NAPCAT_SEND_PRIVATE = "http://127.0.0.1:3000/send_private_msg"
NAPCAT_SEND_GROUP = "http://127.0.0.1:3000/send_group_msg"

conversation_history = {}

def get_chat_id(event):
    if event.get("message_type") == "private":
        return f"private_{event['user_id']}"
    elif event.get("message_type") == "group":
        return f"group_{event['group_id']}"
    return None

async def send_reply(chat_type, target_id, reply_text, sender_id=None):
    if chat_type == "private":
        payload = {"user_id": int(target_id), "message": reply_text}
        api = NAPCAT_SEND_PRIVATE
    elif chat_type == "group":
        at_text = f"[CQ:at,qq={sender_id}] " if sender_id else ""
        payload = {
            "group_id": int(target_id),
            "message": at_text + reply_text
        }
        api = NAPCAT_SEND_GROUP
    else:
        return

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(api, json=payload, timeout=10)
            if resp.status_code == 200:
                print(f"Reply sent to {chat_type} {target_id}: {reply_text[:100]}...")
            else:
                print(f"Failed to send {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"Error sending reply: {str(e)}")

async def main():
    uri = NAPCAT_WS_URL
    print(f"Attempting to connect to NapCat WS: {uri}")

    async with websockets.connect(uri) as ws:
        print("Connected to NapCat WS. Listening for events...")

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                print("Received event:", json.dumps(data, ensure_ascii=False, indent=2))

                post_type = data.get("post_type")
                if post_type != "message":
                    continue

                message_type = data.get("message_type")
                sender_id = str(data.get("user_id", ""))
                raw_msg = data.get("raw_message", "").strip()

                if not raw_msg:
                    continue

                if message_type == "group":
                    mentions = data.get("message", [])
                    is_at_bot = False
                    for seg in mentions:
                        if seg.get("type") == "at" and str(seg.get("data", {}).get("qq")) == BOT_QQ:
                            is_at_bot = True
                            break
                    if not is_at_bot:
                        print("Group message did not mention bot, ignoring.")
                        continue

                chat_id = get_chat_id(data)
                if not chat_id:
                    continue

                print(f"[Message Received] {message_type} - {sender_id}: {raw_msg}")

                if chat_id not in conversation_history:
                    conversation_history[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

                conversation_history[chat_id].append({"role": "user", "content": raw_msg})

                try:
                    resp = ollama.chat(
                        model=OLLAMA_MODEL,
                        messages=conversation_history[chat_id],
                        options={"temperature": 0.7, "max_tokens": 1024}
                    )
                    reply = resp['message']['content'].strip()

                    conversation_history[chat_id].append({"role": "assistant", "content": reply})

                    target_id = data.get("user_id") if message_type == "private" else data.get("group_id")
                    await send_reply(message_type, target_id, reply, sender_id)

                except Exception as e:
                    print(f"Ollama generation failed: {str(e)}")
                    target_id = data.get("user_id") if message_type == "private" else data.get("group_id")
                    await send_reply(message_type, target_id, "Sorry, I am experiencing a technical issue... Please try again later.", sender_id)

            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed, attempting to reconnect...")
                await asyncio.sleep(5)
                break

            except Exception as e:
                print(f"Error processing event: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())