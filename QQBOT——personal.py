import asyncio
import websockets
import json
import ollama
import httpx

# ===================== Configuration =====================
NAPCAT_WS_URL = "ws://127.0.0.1:3001"
OLLAMA_MODEL = "qwen3-coder:480b-cloud"  #enter name of model in ollama

SYSTEM_PROMPT = '#' # your can tell the bot what character you want it to be

ALLOWED_SENDER = "#"  # enter certain QQ number if you do not want strangers to interact with your bot
NAPCAT_HTTP_API = "http://127.0.0.1:3000/send_private_msg"

conversation_history = {}

async def send_reply(user_id, reply_text):
    """Send private message reply via NapCat HTTP API"""
    payload = {
        "user_id": int(user_id),
        "message": reply_text
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(NAPCAT_HTTP_API, json=payload, timeout=10)
            if resp.status_code == 200:
                print(f"Reply sent to {user_id}: {reply_text[:100]}...")
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

                if data.get("post_type") == "message" and data.get("message_type") == "private":
                    sender_id = str(data.get("user_id", ""))
                    raw_msg = data.get("raw_message", "").strip()

                    if not raw_msg:
                        continue

                    print(f"[Private Message Received] {sender_id}: {raw_msg}")

                    if sender_id not in conversation_history:
                        conversation_history[sender_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

                    conversation_history[sender_id].append({"role": "user", "content": raw_msg})

                    try:
                        resp = ollama.chat(
                            model=OLLAMA_MODEL,
                            messages=conversation_history[sender_id],
                            options={"temperature": 0.7, "max_tokens": 1024}
                        )
                        reply = resp['message']['content'].strip()

                        conversation_history[sender_id].append({"role": "assistant", "content": reply})

                        await send_reply(sender_id, reply)

                    except Exception as e:
                        print(f"Ollama generation failed: {str(e)}")
                        await send_reply(sender_id, "Sorry, I am experiencing a technical issue... Please try again later.")

            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed, attempting to reconnect...")
                await asyncio.sleep(5)
                break

            except Exception as e:
                print(f"Error processing event: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())