import json
import random
import streamlit as st
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Prisoner's Dilemma Tournament",
    page_icon="",
    layout="wide"
)

PLAYERS = [
    "GUNGUN","MAHIMA","NGIPLO","GODIVA","LUHAMDI",
    "ZELLA","ARSEY","ROJITA","BHARGAB","RIJU"
]
MAX_ROUNDS = 10

PAYOFFS = {
    ("C", "C"): (3, 3),
    ("C", "D"): (0, 5),
    ("D", "C"): (5, 0),
    ("D", "D"): (1, 1),
}

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
.hero {
    padding: 1.4rem 1.6rem;
    border-radius: 18px;
    background: linear-gradient(135deg,#3949ab,#6a1b9a);
    color: white;
    margin-bottom: 1rem;
}
.hero h1 {margin:0; font-size:2rem;}
.hero p {margin:.25rem 0 0 0; opacity:.92;}
.smallmuted {color:#667085; font-size:.9rem;}
.turnbox {
    border:1px solid #dfe5ee;
    border-radius:16px;
    padding:1.2rem;
    background:#ffffff;
}
.payoff {
    text-align:center;
    border-radius:12px;
    padding:.75rem;
    border:1px solid #e5e7eb;
}
.waiting {
    padding:1rem;
    border-radius:12px;
    background:#f8fafc;
    border:1px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

def default_state():
    return {
        "id": 1,
        "round_no": 1,
        "match_index": 0,
        "player_in_pair": 0,
        "current_pairs": [],
        "choices": {},
        "scores": {p: 0 for p in PLAYERS},
        "history": [],
        "game_started": False,
        "game_finished": False,
    }

def fetch_state():
    data = supabase.table("game_state").select("*").eq("id", 1).execute().data
    if not data:
        state = default_state()
        supabase.table("game_state").insert(state).execute()
        return state
    row = data[0]
    # Supabase may return json/jsonb already parsed, but keep this safe.
    for k in ["current_pairs", "choices", "scores", "history"]:
        if isinstance(row.get(k), str):
            row[k] = json.loads(row[k])
    return row

def save_state(state):
    payload = {
        "round_no": state["round_no"],
        "match_index": state["match_index"],
        "player_in_pair": state["player_in_pair"],
        "current_pairs": state["current_pairs"],
        "choices": state["choices"],
        "scores": state["scores"],
        "history": state["history"],
        "game_started": state["game_started"],
        "game_finished": state["game_finished"],
    }
    supabase.table("game_state").update(payload).eq("id", 1).execute()

def shuffled_pairs(history):
    previous = set()
    if history:
        for r in history[-1]["results"]:
            previous.add(tuple(sorted([r["a"], r["b"]])))

    best = None
    best_repeats = 999
    for _ in range(300):
        names = PLAYERS[:]
        random.shuffle(names)
        pairs = [[names[i], names[i+1]] for i in range(0, len(names), 2)]
        repeats = sum(tuple(sorted(pair)) in previous for pair in pairs)
        if repeats < best_repeats:
            best = pairs
            best_repeats = repeats
        if repeats == 0:
            break
    return best

def start_round(state):
    state["match_index"] = 0
    state["player_in_pair"] = 0
    state["choices"] = {}
    state["current_pairs"] = shuffled_pairs(state["history"])
    state["game_started"] = True
    state["game_finished"] = False
    save_state(state)

def current_player(state):
    if not state["current_pairs"] or state["match_index"] >= 5:
        return None
    pair = state["current_pairs"][state["match_index"]]
    return pair[state["player_in_pair"]]

def current_pair(state):
    if not state["current_pairs"] or state["match_index"] >= 5:
        return None
    return state["current_pairs"][state["match_index"]]

def record_vote(state, player, choice):
    expected = current_player(state)
    if expected != player:
        return False, "It is no longer your turn. The game has already moved on."

    state["choices"][player] = choice

    if state["player_in_pair"] == 0:
        state["player_in_pair"] = 1
    else:
        state["player_in_pair"] = 0
        state["match_index"] += 1

    if state["match_index"] >= 5:
        resolve_round(state)
    else:
        save_state(state)

    return True, "Vote saved."

def resolve_round(state):
    results = []
    for a, b in state["current_pairs"]:
        ca = state["choices"][a]
        cb = state["choices"][b]
        pa, pb = PAYOFFS[(ca, cb)]
        state["scores"][a] += pa
        state["scores"][b] += pb
        results.append({
            "a": a, "b": b, "ca": ca, "cb": cb,
            "pa": pa, "pb": pb
        })

    state["history"].append({
        "round": state["round_no"],
        "results": results
    })

    if state["round_no"] >= MAX_ROUNDS:
        state["game_finished"] = True
        state["game_started"] = False
    else:
        state["game_started"] = False

    save_state(state)

def reset_game():
    state = default_state()
    supabase.table("game_state").upsert(state).execute()

def advance_next_round(state):
    if state["round_no"] < MAX_ROUNDS:
        state["round_no"] += 1
        start_round(state)

# auto-refresh every 2 seconds so every laptop follows the shared state
st_autorefresh(interval=2000, key="game_refresh")

st.markdown("""
<div class="hero">
  <h1>Prisoner's Dilemma Tournament</h1>
  <p>Game Theory & Nash Equilibrium • The Assam Royal Global University • Designed by Amit Kumar</p>
</div>
""", unsafe_allow_html=True)

with st.expander("Payoff Matrix & Game Theory", expanded=False):
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown('<div class="payoff"><b>C / C</b><br>3 – 3</div>', unsafe_allow_html=True)
    c2.markdown('<div class="payoff"><b>C / D</b><br>0 – 5</div>', unsafe_allow_html=True)
    c3.markdown('<div class="payoff"><b>D / C</b><br>5 – 0</div>', unsafe_allow_html=True)
    c4.markdown('<div class="payoff"><b>D / D</b><br>1 – 1</div>', unsafe_allow_html=True)
    st.markdown("""
    **Game Theory:** studies strategic decisions where your outcome depends on what others do.

    **Nash Equilibrium:** a situation where no player can improve their payoff by changing their decision alone.
    In the standard one-shot Prisoner's Dilemma, **Defect–Defect (D,D)** is the Nash equilibrium.
    """)

state = fetch_state()

top1, top2, top3 = st.columns([1,1,1])
top1.metric("Round", f'{state["round_no"]} / {MAX_ROUNDS}')
top2.metric("Match", f'{min(state["match_index"] + 1, 5)} / 5')
top3.metric("Players", len(PLAYERS))

st.subheader("Student Login")
selected_name = st.selectbox(
    "Select your name",
    ["Select your name"] + PLAYERS,
    index=0
)

teacher_mode = st.toggle("Teacher controls", value=False)

if teacher_mode:
    st.markdown("#### Teacher Controls")
    tc1, tc2 = st.columns(2)

    if not state["game_started"] and not state["game_finished"]:
        if state["history"]:
            if tc1.button("Start Next Round", use_container_width=True):
                advance_next_round(state)
                st.rerun()
        else:
            if tc1.button("Start Game", use_container_width=True):
                start_round(state)
                st.rerun()

    if tc2.button("Reset Entire Game", use_container_width=True):
        reset_game()
        st.rerun()

st.divider()

if state["game_finished"]:
    st.success("Tournament complete.")
    sorted_scores = sorted(state["scores"].items(), key=lambda x: (-x[1], x[0]))
    high = sorted_scores[0][1]
    winners = [p for p, s in sorted_scores if s == high]
    st.subheader("Winner")
    st.write(f'**{", ".join(winners)}** — {high} points')

elif not state["game_started"]:
    if state["history"]:
        st.info("This round is complete. Waiting for the teacher to start the next round.")
    else:
        st.info("Waiting for the teacher to start the game.")

else:
    pair = current_pair(state)
    turn = current_player(state)

    if pair:
        st.subheader(f'Match {state["match_index"] + 1}: {pair[0]} vs {pair[1]}')

    if selected_name == "Select your name":
        st.markdown('<div class="waiting">Select your name above. The page will automatically update every few seconds.</div>', unsafe_allow_html=True)

    elif selected_name == turn:
        opponent = pair[1] if pair[0] == selected_name else pair[0]
        st.markdown(f"""
        <div class="turnbox">
          <div class="smallmuted">It is your turn</div>
          <h2>{selected_name}</h2>
          <p>Your opponent is <b>{opponent}</b>.</p>
          <p>Your choice remains hidden until the entire round ends.</p>
        </div>
        """, unsafe_allow_html=True)

        col_c, col_d = st.columns(2)
        if col_c.button("Cooperate (C)", use_container_width=True, type="primary"):
            ok, msg = record_vote(fetch_state(), selected_name, "C")
            if ok:
                st.success(msg)
            else:
                st.warning(msg)
            st.rerun()

        if col_d.button("Defect (D)", use_container_width=True):
            ok, msg = record_vote(fetch_state(), selected_name, "D")
            if ok:
                st.success(msg)
            else:
                st.warning(msg)
            st.rerun()

    else:
        st.markdown(f"""
        <div class="waiting">
          <b>Waiting for {turn}</b><br>
          Your screen will update automatically when it becomes your turn.
        </div>
        """, unsafe_allow_html=True)

st.divider()

left, right = st.columns([1,1])

with left:
    st.subheader("Current Pairings")
    for i, pair in enumerate(state.get("current_pairs") or []):
        if i < state["match_index"]:
            status = "Complete"
        elif state["game_started"] and i == state["match_index"]:
            status = "Voting now"
        else:
            status = "Waiting"
        st.write(f'**Match {i+1}:** {pair[0]} vs {pair[1]} — {status}')

with right:
    st.subheader("Leaderboard")
    sorted_scores = sorted(state["scores"].items(), key=lambda x: (-x[1], x[0]))
    for i, (name, points) in enumerate(sorted_scores, 1):
        st.write(f'**{i}. {name}** — {points} points')

if state["history"]:
    st.divider()
    st.subheader("Round History")
    for item in reversed(state["history"]):
        with st.expander(f'Round {item["round"]}'):
            for r in item["results"]:
                st.write(
                    f'{r["a"]} ({r["ca"]}) vs {r["b"]} ({r["cb"]}) '
                    f'→ {r["pa"]}–{r["pb"]}'
                )

st.caption("The Assam Royal Global University • Designed by Amit Kumar")
