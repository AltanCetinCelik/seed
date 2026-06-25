#!/usr/bin/env python3
from pathlib import Path
import json
import re

MODULES = json.loads("{\"seed_live_voice_v731.py\": \"\\nimport json\\nimport os\\nimport re\\nimport shutil\\nimport subprocess\\nfrom datetime import datetime\\nfrom pathlib import Path\\n\\nVOICE_DIR = Path(\\\"seed_voice_recordings_v731\\\")\\nVOICE_DIR.mkdir(exist_ok=True)\\n\\nJOURNAL_FILE = Path(\\\"seed_voice_journal_v731.jsonl\\\")\\nSETTINGS_FILE = Path(\\\"seed_voice_settings_v731.json\\\")\\n\\n\\ndef now_timestamp():\\n    return datetime.now().isoformat(timespec=\\\"seconds\\\")\\n\\n\\ndef tool_path(name):\\n    return shutil.which(name)\\n\\n\\ndef load_settings():\\n    if SETTINGS_FILE.exists():\\n        try:\\n            return json.loads(SETTINGS_FILE.read_text(errors=\\\"ignore\\\"))\\n        except Exception:\\n            pass\\n    return {\\n        \\\"version\\\": \\\"v73.1.0\\\",\\n        \\\"ffmpeg_avfoundation_audio_device\\\": \\\":0\\\",\\n        \\\"whisper_model\\\": os.environ.get(\\\"SEED_WHISPER_MODEL\\\", \\\"tiny.en\\\"),\\n        \\\"speak_reply\\\": True,\\n    }\\n\\n\\ndef save_settings(data):\\n    data[\\\"updated_at\\\"] = now_timestamp()\\n    SETTINGS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))\\n    return data\\n\\n\\ndef voice_status():\\n    data = {\\n        \\\"created_at\\\": now_timestamp(),\\n        \\\"version\\\": \\\"v73.1.0\\\",\\n        \\\"ok\\\": True,\\n        \\\"tools\\\": {\\n            \\\"ffmpeg\\\": tool_path(\\\"ffmpeg\\\"),\\n            \\\"macos_say\\\": tool_path(\\\"say\\\"),\\n            \\\"faster_whisper\\\": False,\\n        },\\n        \\\"settings\\\": load_settings(),\\n        \\\"commands\\\": [\\n            \\\"voice once\\\",\\n            \\\"voice once 8\\\",\\n            \\\"voice devices\\\",\\n            \\\"voice test say\\\",\\n            \\\"voice status\\\",\\n        ],\\n        \\\"path\\\": \\\"record -> transcribe -> Seed local chat -> optional macOS say -> journal\\\",\\n    }\\n\\n    try:\\n        import faster_whisper  # noqa: F401\\n        data[\\\"tools\\\"][\\\"faster_whisper\\\"] = True\\n    except Exception:\\n        data[\\\"tools\\\"][\\\"faster_whisper\\\"] = False\\n\\n    return data\\n\\n\\ndef show_voice_status():\\n    print(\\\"\\\\n=== SEED v73.1 LIVE VOICE ===\\\")\\n    print(json.dumps(voice_status(), indent=4, ensure_ascii=False))\\n    print(\\\"To record: type 'voice once' or 'voice once 8'.\\\")\\n    return \\\"handled\\\"\\n\\n\\ndef list_voice_devices():\\n    ffmpeg = tool_path(\\\"ffmpeg\\\")\\n    if not ffmpeg:\\n        print(\\\"ffmpeg not found.\\\")\\n        return \\\"handled\\\"\\n\\n    print(\\\"\\\\n=== macOS audio/video devices from ffmpeg ===\\\")\\n    proc = subprocess.run(\\n        [ffmpeg, \\\"-f\\\", \\\"avfoundation\\\", \\\"-list_devices\\\", \\\"true\\\", \\\"-i\\\", \\\"\\\"],\\n        capture_output=True,\\n        text=True,\\n        timeout=20,\\n    )\\n\\n    output = (proc.stderr or proc.stdout or \\\"\\\").strip()\\n    print(output[-5000:] if output else \\\"No device output.\\\")\\n    print(\\\"\\\\nFor Mac audio, Seed tries :0, :1, :2 automatically.\\\")\\n    return \\\"handled\\\"\\n\\n\\ndef _record_with_device(seconds, device):\\n    ffmpeg = tool_path(\\\"ffmpeg\\\")\\n    if not ffmpeg:\\n        raise RuntimeError(\\\"ffmpeg not found.\\\")\\n\\n    stamp = datetime.now().strftime(\\\"%Y%m%d_%H%M%S\\\")\\n    out = VOICE_DIR / f\\\"voice_{stamp}.wav\\\"\\n\\n    cmd = [\\n        ffmpeg,\\n        \\\"-y\\\",\\n        \\\"-loglevel\\\",\\n        \\\"error\\\",\\n        \\\"-f\\\",\\n        \\\"avfoundation\\\",\\n        \\\"-i\\\",\\n        device,\\n        \\\"-t\\\",\\n        str(int(seconds)),\\n        \\\"-ar\\\",\\n        \\\"16000\\\",\\n        \\\"-ac\\\",\\n        \\\"1\\\",\\n        str(out),\\n    ]\\n\\n    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=int(seconds) + 20)\\n\\n    if proc.returncode != 0 or not out.exists() or out.stat().st_size < 2000:\\n        raise RuntimeError((proc.stderr or proc.stdout or \\\"recording failed\\\").strip())\\n\\n    return out\\n\\n\\ndef record_audio(seconds=6):\\n    settings = load_settings()\\n    preferred = settings.get(\\\"ffmpeg_avfoundation_audio_device\\\", \\\":0\\\")\\n    candidates = []\\n    for dev in [preferred, \\\":0\\\", \\\":1\\\", \\\":2\\\", \\\":3\\\"]:\\n        if dev not in candidates:\\n            candidates.append(dev)\\n\\n    errors = []\\n    for device in candidates:\\n        try:\\n            path = _record_with_device(seconds, device)\\n            settings[\\\"ffmpeg_avfoundation_audio_device\\\"] = device\\n            save_settings(settings)\\n            return path, device\\n        except Exception as error:\\n            errors.append(f\\\"{device}: {error}\\\")\\n\\n    raise RuntimeError(\\\"Could not record audio with any tried device:\\\\n\\\" + \\\"\\\\n\\\".join(errors[-5:]))\\n\\n\\ndef transcribe_audio(path):\\n    try:\\n        from faster_whisper import WhisperModel\\n    except Exception as error:\\n        raise RuntimeError(f\\\"faster_whisper import failed: {error}\\\")\\n\\n    settings = load_settings()\\n    model_name = settings.get(\\\"whisper_model\\\", \\\"tiny.en\\\")\\n\\n    model = WhisperModel(model_name, device=\\\"cpu\\\", compute_type=\\\"int8\\\")\\n    segments, info = model.transcribe(str(path), beam_size=1, vad_filter=True)\\n\\n    text = \\\" \\\".join(seg.text.strip() for seg in segments).strip()\\n\\n    return {\\n        \\\"text\\\": text,\\n        \\\"language\\\": getattr(info, \\\"language\\\", None),\\n        \\\"duration\\\": getattr(info, \\\"duration\\\", None),\\n        \\\"model\\\": model_name,\\n    }\\n\\n\\ndef ask_seed_text(message):\\n    try:\\n        from seed_local_chat_v701 import choose_role, model_fallbacks, call_ollama\\n    except Exception as error:\\n        raise RuntimeError(f\\\"Could not import Seed local chat router: {error}\\\")\\n\\n    role = choose_role(message)\\n\\n    for model in model_fallbacks(role):\\n        try:\\n            print(f\\\"Using {model} for {role}.\\\")\\n            reply = call_ollama(model, role, message)\\n            reply = (reply or \\\"\\\").strip()\\n\\n            if reply and reply.lower() not in {\\\"normal\\\", \\\"ok\\\", \\\"okay\\\"}:\\n                return {\\n                    \\\"ok\\\": True,\\n                    \\\"role\\\": role,\\n                    \\\"model\\\": model,\\n                    \\\"reply\\\": reply,\\n                }\\n        except Exception as error:\\n            last_error = str(error)\\n\\n    return {\\n        \\\"ok\\\": False,\\n        \\\"role\\\": role,\\n        \\\"model\\\": None,\\n        \\\"reply\\\": \\\"\\\",\\n        \\\"error\\\": locals().get(\\\"last_error\\\", \\\"no valid reply\\\"),\\n    }\\n\\n\\ndef say_text(text):\\n    say = tool_path(\\\"say\\\")\\n    if not say:\\n        return False\\n\\n    clean = str(text or \\\"\\\").strip()\\n    if not clean:\\n        return False\\n\\n    subprocess.run([say, clean[:900]], timeout=90)\\n    return True\\n\\n\\ndef append_journal(row):\\n    with JOURNAL_FILE.open(\\\"a\\\") as f:\\n        f.write(json.dumps(row, ensure_ascii=False) + \\\"\\\\n\\\")\\n\\n\\ndef run_voice_once(seconds=6, speak=True):\\n    print(f\\\"\\\\n=== SEED v73.1 VOICE ONCE ({seconds}s) ===\\\")\\n    print(\\\"Recording now. Speak after the microphone permission prompt if macOS shows one.\\\")\\n\\n    try:\\n        audio_path, device = record_audio(seconds)\\n        print(f\\\"Recorded: {audio_path} using device {device}\\\")\\n\\n        transcript = transcribe_audio(audio_path)\\n        text = transcript.get(\\\"text\\\", \\\"\\\").strip()\\n\\n        print(f\\\"Transcript: {text or '[empty]'}\\\")\\n\\n        if not text:\\n            row = {\\n                \\\"created_at\\\": now_timestamp(),\\n                \\\"ok\\\": False,\\n                \\\"audio\\\": str(audio_path),\\n                \\\"device\\\": device,\\n                \\\"error\\\": \\\"empty transcript\\\",\\n            }\\n            append_journal(row)\\n            print(\\\"I recorded, but transcription was empty. Try 'voice once 8' and speak closer to the mic.\\\")\\n            return \\\"handled\\\"\\n\\n        answer = ask_seed_text(text)\\n        reply = answer.get(\\\"reply\\\", \\\"\\\")\\n\\n        print(\\\"\\\\nSeed:\\\")\\n        print(reply or \\\"[no reply]\\\")\\n\\n        did_say = False\\n        if speak and reply:\\n            did_say = say_text(reply)\\n\\n        row = {\\n            \\\"created_at\\\": now_timestamp(),\\n            \\\"ok\\\": answer.get(\\\"ok\\\"),\\n            \\\"audio\\\": str(audio_path),\\n            \\\"device\\\": device,\\n            \\\"transcript\\\": text,\\n            \\\"transcript_meta\\\": transcript,\\n            \\\"role\\\": answer.get(\\\"role\\\"),\\n            \\\"model\\\": answer.get(\\\"model\\\"),\\n            \\\"reply\\\": reply,\\n            \\\"spoke\\\": did_say,\\n        }\\n        append_journal(row)\\n\\n        return \\\"handled\\\"\\n\\n    except Exception as error:\\n        row = {\\n            \\\"created_at\\\": now_timestamp(),\\n            \\\"ok\\\": False,\\n            \\\"error\\\": str(error),\\n            \\\"hint\\\": \\\"Run 'voice devices' if recording fails. macOS may need microphone permission for Terminal.\\\",\\n        }\\n        append_journal(row)\\n\\n        print(\\\"\\\\nVoice failed:\\\")\\n        print(error)\\n        print(\\\"\\\\nTry:\\\")\\n        print(\\\"- voice devices\\\")\\n        print(\\\"- give Terminal/iTerm microphone permission in macOS Settings > Privacy & Security > Microphone\\\")\\n        print(\\\"- voice once 8\\\")\\n        return \\\"handled\\\"\\n\\n\\ndef handle_voice_command_v731(user_message):\\n    text = str(user_message or \\\"\\\").strip().lower()\\n\\n    if text in {\\\"voice status\\\", \\\"voice live\\\", \\\"voice\\\"}:\\n        return show_voice_status()\\n\\n    if text in {\\\"voice devices\\\", \\\"list voice devices\\\", \\\"mic devices\\\", \\\"microphone devices\\\"}:\\n        return list_voice_devices()\\n\\n    if text in {\\\"voice test say\\\", \\\"test say\\\", \\\"say test\\\"}:\\n        say_text(\\\"Seed voice output is working.\\\")\\n        print(\\\"macOS say test sent.\\\")\\n        return \\\"handled\\\"\\n\\n    if text.startswith(\\\"voice once\\\") or text.startswith(\\\"record voice\\\") or text.startswith(\\\"test voice\\\"):\\n        match = re.search(r\\\"\\\\b(\\\\d{1,2})\\\\b\\\", text)\\n        seconds = int(match.group(1)) if match else 6\\n        seconds = max(2, min(seconds, 20))\\n        return run_voice_once(seconds=seconds, speak=True)\\n\\n    return None\\n\\n\\nif __name__ == \\\"__main__\\\":\\n    show_voice_status()\\n\", \"seed_v731_gate.py\": \"\\nimport json\\nimport subprocess\\nfrom datetime import datetime\\n\\nMODULES = [\\n    \\\"seed_live_voice_v731.py\\\",\\n    \\\"seed_v731_gate.py\\\",\\n]\\n\\ndef now_timestamp():\\n    return datetime.now().isoformat(timespec=\\\"seconds\\\")\\n\\ndef compile_module(module):\\n    proc = subprocess.run([\\\"python\\\", \\\"-m\\\", \\\"py_compile\\\", module], capture_output=True, text=True, timeout=30)\\n    return {\\\"module\\\": module, \\\"ok\\\": proc.returncode == 0, \\\"stderr\\\": proc.stderr[-1200:]}\\n\\ndef run_v731_gate():\\n    checks = [compile_module(m) for m in MODULES]\\n    modules_ok = all(c[\\\"ok\\\"] for c in checks)\\n    details = {}\\n\\n    try:\\n        from seed_live_voice_v731 import voice_status\\n        status = voice_status()\\n        voice_ok = bool(status.get(\\\"tools\\\", {}).get(\\\"ffmpeg\\\")) and bool(status.get(\\\"tools\\\", {}).get(\\\"macos_say\\\"))\\n        details[\\\"voice\\\"] = status\\n    except Exception as error:\\n        voice_ok = False\\n        details[\\\"voice_error\\\"] = str(error)\\n\\n    try:\\n        from seed_v73_gate import run_v73_gate\\n        v73 = run_v73_gate()\\n        v73_ok = v73.get(\\\"ready\\\") is True\\n        details[\\\"v73\\\"] = {\\\"ready\\\": v73.get(\\\"ready\\\")}\\n    except Exception as error:\\n        v73_ok = False\\n        details[\\\"v73_error\\\"] = str(error)\\n\\n    report = {\\n        \\\"created_at\\\": now_timestamp(),\\n        \\\"version\\\": \\\"v73.1.0\\\",\\n        \\\"ready\\\": modules_ok and voice_ok and v73_ok,\\n        \\\"modules_ok\\\": modules_ok,\\n        \\\"voice_ok\\\": voice_ok,\\n        \\\"v73_ok\\\": v73_ok,\\n        \\\"module_checks\\\": checks,\\n        \\\"details\\\": details,\\n    }\\n\\n    with open(\\\"seed_v731_gate_report.json\\\", \\\"w\\\") as f:\\n        json.dump(report, f, indent=4)\\n\\n    return report\\n\\ndef show_v731_gate():\\n    report = run_v731_gate()\\n    print(\\\"\\\\n=== SEED v73.1 VOICE ROUTER GATE ===\\\")\\n    print(f\\\"Ready: {report['ready']}\\\")\\n    print(f\\\"Modules OK: {report['modules_ok']}\\\")\\n    print(f\\\"Voice OK: {report['voice_ok']}\\\")\\n    print(f\\\"v73 OK: {report['v73_ok']}\\\")\\n    print(\\\"Details:\\\")\\n    print(json.dumps(report[\\\"details\\\"], indent=4, ensure_ascii=False))\\n\\nif __name__ == \\\"__main__\\\":\\n    show_v731_gate()\\n\"}")

def write(path, text):
    Path(path).write_text(text.strip() + "\n")
    print("Wrote", path)

for path, text in MODULES.items():
    write(path, text)

# Patch seed_commands.py so voice once is caught before old v73 voice-status route.
p = Path("seed_commands.py")
text = p.read_text(errors="ignore") if p.exists() else "def handle_chat_command(user_message,*args,**kwargs): return None\n"

if "_seed_v731_previous_handle_chat_command" not in text:
    text += """
# v73.1 Voice command router fix.
try:
    _seed_v731_previous_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_live_voice_v731 import handle_voice_command_v731
            handled = handle_voice_command_v731(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v73.1 voice router error: {error}")
            return "handled"

        return _seed_v731_previous_handle_chat_command(user_message, *args, **kwargs)

except Exception:
    pass
"""
    p.write_text(text)
    print("Patched seed_commands.py")

# Patch natural routers if they exist, so direct import tests also route correctly.
for router_file in ["seed_natural_intent_router_v73.py", "seed_natural_intent_router_v72.py"]:
    p = Path(router_file)
    if p.exists():
        text = p.read_text(errors="ignore")
        marker = "v73.1 voice once precedence"
        if marker not in text:
            text = text.replace(
                "def handle_natural_intent",
                f"# {marker}\ntry:\n    from seed_live_voice_v731 import handle_voice_command_v731\nexcept Exception:\n    handle_voice_command_v731 = None\n\ndef handle_natural_intent",
                1
            )
            text = text.replace(
                "raw=str(user_message or \"\").strip(); text=norm(raw)",
                "raw=str(user_message or \"\").strip(); text=norm(raw)\n    if handle_voice_command_v731:\n        handled_voice = handle_voice_command_v731(raw)\n        if handled_voice == \"handled\": return \"handled\"",
                1
            )
            p.write_text(text)
            print("Patched", router_file)

# Update config.
p = Path("seed_config.py")
text = p.read_text(errors="ignore") if p.exists() else 'SEED_VERSION = "v73.1.0"\n'
text = re.sub(r'^SEED_VERSION\s*=\s*".*?"', 'SEED_VERSION = "v73.1.0"', text, flags=re.M)
if "SEED_V731_VOICE_ROUTER_FIX" not in text:
    text += '\nSEED_V731_VOICE_ROUTER_FIX = True\n'
p.write_text(text)
print("Updated seed_config.py")

# Update docs.
p = Path("Seed_Core.md")
text = p.read_text(errors="ignore") if p.exists() else ""
if "Seed v73.1 — Voice Router Fix" not in text:
    text += """
## Seed v73.1 — Voice Router Fix

Fixes the issue where `voice once` showed voice status instead of recording.
Adds:
- voice once recording
- ffmpeg avfoundation auto-device fallback
- faster-whisper transcription
- routing transcript into Seed local chat
- macOS say reply
- voice journal
- voice devices helper
"""
p.write_text(text)
print("Updated Seed_Core.md")

# Update gitignore.
p = Path(".gitignore")
text = p.read_text(errors="ignore") if p.exists() else ""
block = """
# Seed v73.1 voice runtime
seed_voice_recordings_v731/
seed_voice_journal_v731.jsonl
seed_voice_settings_v731.json
seed_v731_gate_report.json
"""
if "Seed v73.1 voice runtime" not in text:
    text += "\n" + block
p.write_text(text)
print("Updated .gitignore")

print("\nSeed v73.1 Voice Router Fix installer complete.")
