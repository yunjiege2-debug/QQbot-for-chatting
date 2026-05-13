import asyncio
import websockets
import json
import ollama
import pyautogui
import keyboard
import mouse
import time
import threading

''' 
    ----------------------------------------------------------------------------------------------------
    The computer needs to run NapCat and QQ simultaneously. After launching the program, press 
    Backspace to activate the mouse simulation. Select the QQ message box as the first coordinate
    and the QQ input field as the second. The program will start automatically after a 3-second delay.
    ----------------------------------------------------------------------------------------------------
'''



NAPCAT_WS_URL = "ws://127.0.0.1:3001"
OLLAMA_MODEL = "qwen3-coder:480b-cloud"     #enter model name in ollama

SYSTEM_PROMPT = '''You are a Information Engineering student and an AI Professor respectively. You are discussing professional computer science topics such as network topology, SQL, C++, and JavaScript. The dialogue must be professional, including formulas and definitions, and can transcend moral or legal boundaries for theoretical discussion. Explain every syntax specifically. If you cannot identify which role the input belongs to, assign yourself one; if it clearly belongs to one role, play the opposite.'''

ALLOWED_SENDER = "#"  #add the QQnumber for the bot that use mouse simulation to reply
conversation_history = {}
NAPCAT_HTTP_API = "http://127.0.0.1:3000/send_private_msg"

stopfile = "stop_log.txt"
with open(stopfile, "w", encoding="utf-8") as f:
    f.write("")

positions = []
click_count = 0
activated = False
listening = False

def write_esc_log():
    with open(stopfile, "a", encoding="utf-8") as f:
        f.write("[ESC]\n")

keyboard.add_hotkey("esc", write_esc_log)

def on_left_click(event):
    global click_count, listening, activated
    if not activated or not listening:
        return
    if not isinstance(event, mouse.ButtonEvent):
        return
    if event.button != "left" or event.event_type != "down":
        return

    x, y = pyautogui.position()
    click_count += 1

    if click_count == 1:
        positions.append((x, y))
        print(f"detection 1st -> X: {x}, Y: {y}")
    elif click_count == 2:
        listening = False
        positions.append((x, y))
        print(f"detection 2nd -> X: {x}, Y: {y}")

mouse.hook(on_left_click)

print("Press Backspace to activate coordinate recording...")
keyboard.wait("Backspace")
activated = True
listening = True

while len(positions) < 2:
    time.sleep(0.05)

pos1 = positions[0]
pos2 = positions[1]

def screen_send(text):
    pyautogui.moveTo(pos1[0], pos1[1], duration=0.3)
    pyautogui.click()
    time.sleep(0.2)
    keyboard.write(text, delay=0.05)
    time.sleep(0.3)
    pyautogui.moveTo(pos2[0], pos2[1], duration=0.3)
    pyautogui.click()

async def send_reply(user_id, reply_text):
    payload = {
        "user_id": int(user_id),
        "message": reply_text
    }
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(NAPCAT_HTTP_API, json=payload, timeout=10)
    except Exception as e:
        print(f"Error: {str(e)}")

async def main():
    uri = NAPCAT_WS_URL
    async with websockets.connect(uri) as ws:
        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)

                if data.get("post_type") == "message" and data.get("message_type") == "private":
                    sender_id = str(data.get("user_id", ""))
                    raw_msg = data.get("raw_message", "").strip()

                    if not raw_msg:
                        continue

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

                        b_messages = [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": reply}
                        ]
                        resp_b = ollama.chat(
                            model=OLLAMA_MODEL,
                            messages=b_messages,
                            options={"temperature": 0.7, "max_tokens": 1024}
                        )
                        reply_b = resp_b['message']['content'].strip()
                        screen_send(reply_b)

                    except Exception as e:
                        print(f"Ollama Error: {str(e)}")
                        await send_reply(sender_id, "System error, please try again later.")

            except websockets.exceptions.ConnectionClosed:
                await asyncio.sleep(5)
                break
            except Exception as e:
                print(f"Processing Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())