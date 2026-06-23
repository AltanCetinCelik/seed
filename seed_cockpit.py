import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from seed_config import (
    COCKPIT_HOST,
    COCKPIT_PORT,
    COCKPIT_TITLE,
    SEED_VERSION
)
from seed_status import show_seed_status
from seed_memory import memories
from seed_memory_tools import show_memory_stats
from seed_project_inspector import get_project_report
from seed_llm import check_ollama_health
from seed_skill_kernel import load_all_skills, get_all_capabilities
from seed_open_source_dna import load_dna_data
from seed_world import (
    load_world,
    load_timeline,
    load_quests,
    load_rituals,
    get_world_summary
)
from seed_brain import ask_seed


app = FastAPI(title=COCKPIT_TITLE)


def safe_call(function, fallback):
    try:
        return function()
    except Exception as error:
        return {
            "error": str(error),
            "fallback": fallback
        }


def get_cockpit_state():
    health = check_ollama_health()
    skills = load_all_skills()
    capabilities = get_all_capabilities()
    dna = load_dna_data()
    world_summary = get_world_summary()

    return {
        "version": SEED_VERSION,
        "ollama": health,
        "memory_count": len(memories),
        "skills": len(skills),
        "capabilities": len(capabilities),
        "dna_repos_found": dna.get("found_count"),
        "dna_repo_count": dna.get("repo_count"),
        "dna_audits": len(dna.get("audits", {})),
        "world": world_summary["world"],
        "active_quests": world_summary["active_quests"],
        "timeline_count": world_summary["timeline_count"],
        "quest_count": world_summary["quest_count"]
    }


@app.get("/")
def home():
    return HTMLResponse(get_cockpit_html())


@app.get("/api/state")
def api_state():
    return JSONResponse(get_cockpit_state())


@app.get("/api/world")
def api_world():
    return JSONResponse(load_world())


@app.get("/api/timeline")
def api_timeline():
    return JSONResponse(load_timeline())


@app.get("/api/quests")
def api_quests():
    return JSONResponse(load_quests())


@app.get("/api/rituals")
def api_rituals():
    return JSONResponse(load_rituals())


@app.get("/api/skills")
def api_skills():
    return JSONResponse({
        "skills": load_all_skills(),
        "capabilities": get_all_capabilities()
    })


@app.get("/api/dna")
def api_dna():
    return JSONResponse(load_dna_data())


@app.get("/api/project")
def api_project():
    return JSONResponse({
        "report": get_project_report()
    })


@app.post("/api/chat")
async def api_chat(payload: dict):
    message = payload.get("message", "")

    if message.strip() == "":
        return JSONResponse({
            "answer": "Message cannot be empty."
        })

    answer = ask_seed(
        message,
        session_history=[],
        runtime_context={
            "source": "cockpit"
        }
    )

    return JSONResponse({
        "answer": answer
    })


def get_cockpit_html():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>SEED Companion Cockpit</title>
    <meta charset="utf-8">
    <style>
        :root {
            --bg: #0d0f10;
            --panel: #171a1d;
            --panel2: #202428;
            --text: #f1efe7;
            --muted: #a6a29a;
            --accent: #ff9f1c;
            --accent2: #ffd166;
            --danger: #ef476f;
            --green: #06d6a0;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background:
                radial-gradient(circle at top left, rgba(255, 159, 28, 0.18), transparent 30%),
                radial-gradient(circle at bottom right, rgba(6, 214, 160, 0.08), transparent 25%),
                var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        header {
            padding: 24px 32px;
            border-bottom: 1px solid #2b3035;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        h1 {
            margin: 0;
            font-size: 28px;
            letter-spacing: 0.5px;
        }

        .version {
            color: var(--accent);
            font-weight: 700;
        }

        .grid {
            padding: 28px 32px;
            display: grid;
            grid-template-columns: 1.2fr 1fr 1fr;
            gap: 18px;
        }

        .panel {
            background: linear-gradient(180deg, var(--panel), #111315);
            border: 1px solid #2a2f33;
            border-radius: 18px;
            padding: 18px;
            box-shadow: 0 12px 35px rgba(0,0,0,0.25);
        }

        .wide {
            grid-column: span 2;
        }

        .full {
            grid-column: span 3;
        }

        .panel h2 {
            margin: 0 0 12px 0;
            font-size: 17px;
            color: var(--accent2);
        }

        .metric {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #252a2e;
            padding: 8px 0;
            color: var(--muted);
        }

        .metric strong {
            color: var(--text);
        }

        .world {
            min-height: 260px;
            background:
                radial-gradient(circle at 50% 35%, rgba(255, 209, 102, 0.25), transparent 16%),
                linear-gradient(180deg, #1b1f24, #0f1113);
            border-radius: 18px;
            border: 1px solid #30363d;
            position: relative;
            overflow: hidden;
        }

        .seed-orb {
            position: absolute;
            width: 76px;
            height: 76px;
            left: calc(50% - 38px);
            top: 82px;
            background: radial-gradient(circle, #ffd166, #ff9f1c 55%, #7a3f00);
            border-radius: 50%;
            box-shadow: 0 0 45px rgba(255,159,28,0.75);
            animation: breathe 3s ease-in-out infinite;
        }

        @keyframes breathe {
            0%, 100% { transform: scale(1); opacity: 0.9; }
            50% { transform: scale(1.08); opacity: 1; }
        }

        .world-label {
            position: absolute;
            bottom: 18px;
            left: 18px;
            right: 18px;
            color: var(--muted);
            line-height: 1.5;
        }

        .button {
            border: 1px solid #3b4249;
            background: var(--panel2);
            color: var(--text);
            padding: 10px 12px;
            border-radius: 12px;
            cursor: pointer;
        }

        .button:hover {
            border-color: var(--accent);
        }

        textarea {
            width: 100%;
            height: 90px;
            background: #0b0d0e;
            color: var(--text);
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 12px;
            resize: vertical;
        }

        .answer {
            margin-top: 12px;
            white-space: pre-wrap;
            color: var(--text);
            background: #0b0d0e;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 12px;
            min-height: 80px;
        }

        .tag {
            display: inline-block;
            padding: 5px 8px;
            border-radius: 999px;
            background: #252a2e;
            color: var(--accent2);
            margin: 4px 5px 4px 0;
            font-size: 12px;
        }

        @media (max-width: 980px) {
            .grid {
                grid-template-columns: 1fr;
            }

            .wide, .full {
                grid-column: span 1;
            }
        }
    </style>
</head>
<body>
    <header>
        <div>
            <h1>SEED Companion Cockpit</h1>
            <div class="version" id="version">loading...</div>
        </div>
        <button class="button" onclick="refreshState()">Refresh</button>
    </header>

    <main class="grid">
        <section class="panel wide">
            <h2>SEED World</h2>
            <div class="world">
                <div class="seed-orb"></div>
                <div class="world-label" id="worldLabel">Loading Seed World...</div>
            </div>
        </section>

        <section class="panel">
            <h2>System</h2>
            <div id="systemMetrics"></div>
        </section>

        <section class="panel">
            <h2>Memory Garden</h2>
            <div id="gardenMetrics"></div>
        </section>

        <section class="panel">
            <h2>Active Quests</h2>
            <div id="quests"></div>
        </section>

        <section class="panel">
            <h2>Skill OS</h2>
            <div id="skillMetrics"></div>
        </section>

        <section class="panel">
            <h2>Open-Source DNA</h2>
            <div id="dnaMetrics"></div>
        </section>

        <section class="panel full">
            <h2>Talk to SEED</h2>
            <textarea id="message" placeholder="Ask Seed something from the cockpit..."></textarea>
            <br><br>
            <button class="button" onclick="sendMessage()">Send</button>
            <div class="answer" id="answer">Seed cockpit chat ready.</div>
        </section>
    </main>

    <script>
        function row(label, value) {
            return `<div class="metric"><span>${label}</span><strong>${value}</strong></div>`;
        }

        async function refreshState() {
            const res = await fetch('/api/state');
            const data = await res.json();

            document.getElementById('version').innerText = data.version;

            const world = data.world;
            const garden = world.memory_garden || {};

            document.getElementById('worldLabel').innerHTML =
                `<strong>${world.location}</strong><br>` +
                `Mood: ${world.mood}<br>` +
                `Weather: ${world.weather}<br>` +
                `Trust phase: ${world.trust_phase}<br>` +
                `Symbol: ${world.current_symbol}`;

            document.getElementById('systemMetrics').innerHTML =
                row('Ollama', data.ollama.ok ? 'online' : 'offline') +
                row('Memories', data.memory_count) +
                row('Timeline events', data.timeline_count) +
                row('Quests', data.quest_count);

            document.getElementById('gardenMetrics').innerHTML =
                row('Seeds', garden.seeds || 0) +
                row('Trees', garden.trees || 0) +
                row('Stones', garden.stones || 0) +
                row('Lights', garden.lights || 0) +
                row('Growth', world.growth) +
                row('Energy', world.energy);

            document.getElementById('skillMetrics').innerHTML =
                row('Skills', data.skills) +
                row('Capabilities', data.capabilities);

            document.getElementById('dnaMetrics').innerHTML =
                row('Repos found', `${data.dna_repos_found} / ${data.dna_repo_count}`) +
                row('Audits', data.dna_audits);

            const quests = data.active_quests || [];
            if (quests.length === 0) {
                document.getElementById('quests').innerHTML = 'No active quests.';
            } else {
                document.getElementById('quests').innerHTML = quests.map(q =>
                    `<div class="tag">${q.id}</div><br><strong>${q.title}</strong><br><span style="color:#a6a29a">${q.reason}</span><br><br>`
                ).join('');
            }
        }

        async function sendMessage() {
            const message = document.getElementById('message').value;
            const answerBox = document.getElementById('answer');

            answerBox.innerText = 'Seed is thinking...';

            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message})
            });

            const data = await res.json();
            answerBox.innerText = data.answer;
        }

        refreshState();
    </script>
</body>
</html>
"""


def run_cockpit():
    print("\n=== SEED COMPANION COCKPIT ===")
    print(f"Open: http://{COCKPIT_HOST}:{COCKPIT_PORT}")
    print("Press CTRL+C to stop.")
    uvicorn.run(
        "seed_cockpit:app",
        host=COCKPIT_HOST,
        port=COCKPIT_PORT,
        reload=False
    )