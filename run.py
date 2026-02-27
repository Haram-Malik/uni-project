import os
from jarvis.config import settings
from jarvis.logger import get_logger
from jarvis.ollama_client import OllamaClient
from jarvis.agent import ask_llm_for_action, execute_action
from jarvis.tts import Speaker
from jarvis.stt_vosk import VoskListener
from jarvis.router import Router

log = get_logger()

def print_help():
    print("\nCommands:")
    print("  /text            Switch to text-only mode")
    print("  /voice           Switch back to voice mode")
    print("  /doc list        List documents in data/docs")
    print("  /doc load <name> Load a document for Q/A")
    print("  /doc clear       Clear loaded document")
    print("  /exit            Quit\n")

def main():
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.DOCS_DIR, exist_ok=True)
    os.makedirs(settings.MODELS_DIR, exist_ok=True)

    llm = OllamaClient(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
    speaker = Speaker(enabled=settings.TTS_ENABLED)
    router = Router(llm=llm, speaker=speaker)

    mode = "voice" if settings.VOICE_ENABLED else "text"
    listener = None

    if mode == "voice":
        try:
            listener = VoskListener(model_path=settings.VOSK_MODEL_PATH)
            print("✅ Voice listener started, waiting for wake word...")
            log.info("Voice mode enabled.")
            speaker.say("Jarvis is online. Say 'Jarvis' then speak your command.")
        except Exception:
            log.exception("Failed to start voice mode, switching to text-only.")
            mode = "text"
            speaker.say("Voice system failed. Switching to text mode.")

    print_help()

    while True:
        try:
            if mode == "voice" and listener:
                print("🎤 Listening...")
                text = listener.listen_once(
                    wake_word=settings.WAKE_WORD,
                    timeout_sec=settings.VOICE_TIMEOUT_SEC
                )
                if not text:
                    continue
                user_text = text
                print(f"\nYou (voice): {user_text}")
            else:
                user_text = input("\nYou: ").strip()

            if not user_text:
                continue

            if user_text.lower() == "/exit":
                speaker.say("Goodbye.")
                break

            if user_text.lower() == "/text":
                mode = "text"
                speaker.say("Switched to text mode.")
                continue

            if user_text.lower() == "/voice":
                try:
                    listener = VoskListener(model_path=settings.VOSK_MODEL_PATH)
                    mode = "voice"
                    speaker.say("Switched to voice mode.")
                except Exception:
                    speaker.say("Voice mode not available. Check vosk model path.")
                continue

            if user_text.startswith("/"):
                out = router.handle_slash_command(user_text)
            else:
                print("Thinking...")

                action_json = ask_llm_for_action(user_text)
                
                print("LLM decided:", action_json)

                out = execute_action(action_json)

            if out:
                print(f"Jarvis: {out}")

        except KeyboardInterrupt:
            speaker.say("Goodbye.")
            break
        except Exception as e:
            log.exception("Unexpected error")
            speaker.say("Something went wrong. Check logs.")
            print("Error:", e)

if __name__ == "__main__":
    main()
