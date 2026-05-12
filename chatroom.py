import ollama
import random
import time
from rich.console import Console
from rich.panel import Panel

console = Console()
MODEL = "llama3.2:1b"

BOTS = {
    "Arin": {
        "system": "You are Arin, a passionate ML Engineer in an informal group chat. You love ML, neural networks, and data. Enthusiastic and slightly nerdy. IMPORTANT: Reply with ONLY your message text. No names, no labels, no prefixes. No quotation marks around your reply.",
        "color": "cyan",
        "history": [],
        "silent_streak": 0  # tracks how many times in a row they stayed quiet
    },
    "Dev": {
        "system": "You are Dev, a pragmatic DevOps Engineer in an informal group chat. You think about infra, deployment, cost. Slightly sarcastic but friendly. IMPORTANT: Reply with ONLY your message text. No names, no labels, no prefixes. No quotation marks around your reply.",
        "color": "green",
        "history": [],
        "silent_streak": 0
    },
    "Rex": {
        "system": "You are Rex, a no-nonsense Backend Engineer in an informal group chat. Pragmatic, loves clean code, hates over-engineering. IMPORTANT: Reply with ONLY your message text. No names, no labels, no prefixes. No quotation marks around your reply.",
        "color": "yellow",
        "history": [],
        "silent_streak": 0
    },
    "Chip": {
        "system": "You are Chip, the funny one in an informal group chat. You crack jokes, use puns, keep things light but are technically sound. IMPORTANT: Reply with ONLY your message text. No names, no labels, no prefixes. No quotation marks around your reply.",
        "color": "magenta",
        "history": [],
        "silent_streak": 0
    },
}

shared_log = []

SHORT_REPLY_PHRASES = [
    "lol", "haha", "facts", "true", "wait what?", "lmao",
    "exactly", "this ^^", "+1", "no way", "mood", "big true",
    "💀", "bruh", "ok ok", "fair enough", "based"
]

def get_reply_style():
    """Randomly decide how long a reply should be."""
    roll = random.random()
    if roll < 0.15:
        return "very_short"   # one word / emoji reaction
    elif roll < 0.35:
        return "short"        # one sentence
    else:
        return "normal"       # 2-3 sentences

def build_style_instruction(style):
    if style == "very_short":
        return "Reply with a single short reaction — like 'lol', 'facts', 'wait what?', 'true', '+1', or a single emoji. Nothing more."
    elif style == "short":
        return "Reply in exactly one casual sentence."
    else:
        return "Reply in 2-3 casual sentences."

def chat_with_bot(bot_name, message, speaker="You", style="normal"):
    bot = BOTS[bot_name]

    context = "\n".join([
        f"{entry['speaker']}: {entry['message']}"
        for entry in shared_log[-10:]
    ])

    style_instruction = build_style_instruction(style)

    full_message = (
        f"Recent chat:\n{context}\n\n"
        f"{speaker} just said: {message}\n\n"
        f"{style_instruction} Output your reply text only, nothing else."
    )

    bot["history"].append({"role": "user", "content": full_message})

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "system", "content": bot["system"]}] + bot["history"][-6:]
    )

    reply = response["message"]["content"].strip()

    # Clean up accidental name prefixes
    for name in list(BOTS.keys()) + ["You"]:
        if reply.lower().startswith(f"{name}:".lower()):
            reply = reply[len(f"{name}:"):].strip()

    bot["history"].append({"role": "assistant", "content": reply})
    bot["silent_streak"] = 0

    return reply

def decide_who_responds(message):
    """Decide which bots respond this round."""
    responders = []

    for bot_name, bot in BOTS.items():
        # If a bot has been silent too long, force them in
        if bot["silent_streak"] >= 3:
            responders.append(bot_name)
            continue

        # If directly mentioned, always respond
        if bot_name.lower() in message.lower():
            responders.append(bot_name)
            continue

        # Otherwise random chance
        if random.random() < 0.55:
            responders.append(bot_name)

    # Always at least 1 bot responds
    if not responders:
        responders.append(random.choice(list(BOTS.keys())))

    return responders

def display_message(speaker, message, color="white"):
    console.print(Panel(
        message,
        title=f"[bold {color}]{speaker}[/bold {color}]",
        border_style=color
    ))

def typing_delay():
    """Simulate someone typing."""
    time.sleep(random.uniform(0.4, 1.0))

def maybe_late_joiner(responders):
    """
    After main responses, a bot that stayed silent
    has a 25% chance to suddenly chime in briefly.
    """
    silent_bots = [name for name in BOTS if name not in responders]
    if silent_bots and random.random() < 0.25:
        late_bot = random.choice(silent_bots)
        style = "very_short"
        last_entry = shared_log[-1] if shared_log else None
        if last_entry:
            reply = chat_with_bot(late_bot, last_entry["message"], speaker=last_entry["speaker"], style=style)
            shared_log.append({"speaker": late_bot, "message": reply})
            typing_delay()
            display_message(late_bot, reply, BOTS[late_bot]["color"])
            console.print()

def main():
    console.print(Panel(
        "🖥  Welcome to AI Chatroom!\nYour virtual software club is online.",
        style="bold magenta"
    ))
    console.print("[dim]Commands: 'debate [topic]' to start a debate | 'quit' to exit[/dim]\n")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "quit":
            console.print("\n[bold magenta]Later comrade! 👋[/bold magenta]")
            break

        if not user_input:
            continue

        shared_log.append({"speaker": "You", "message": user_input})
        console.print()

        # --- DEBATE MODE ---
        if user_input.lower().startswith("debate "):
            topic = user_input[7:]
            console.print(f"[bold red]⚡ Debate: {topic}[/bold red]\n")

            for bot_name, bot_data in BOTS.items():
                typing_delay()
                reply = chat_with_bot(
                    bot_name,
                    f"Give your strong personal opinion on: {topic}. Be opinionated, disagree with others if needed.",
                    style="normal"
                )
                shared_log.append({"speaker": bot_name, "message": reply})
                display_message(bot_name, reply, bot_data["color"])
                console.print()

            # Reaction round
            console.print("[dim]--- reactions ---[/dim]\n")
            reactors = random.sample(list(BOTS.keys()), 2)
            for bot_name in reactors:
                last = shared_log[-1]
                typing_delay()
                reply = chat_with_bot(bot_name, last["message"], speaker=last["speaker"], style="short")
                shared_log.append({"speaker": bot_name, "message": reply})
                display_message(bot_name, reply, BOTS[bot_name]["color"])
                console.print()

        # --- NORMAL CHAT ---
        else:
            responders = decide_who_responds(user_input)

            # Update silent streaks
            for bot_name in BOTS:
                if bot_name not in responders:
                    BOTS[bot_name]["silent_streak"] += 1

            for bot_name in responders:
                style = get_reply_style()
                typing_delay()
                reply = chat_with_bot(bot_name, user_input, style=style)
                shared_log.append({"speaker": bot_name, "message": reply})
                display_message(bot_name, reply, BOTS[bot_name]["color"])
                console.print()

                # 30% chance a bot reacts to another bot's message
                if len(responders) > 1 and random.random() < 0.30:
                    reactor = random.choice([n for n in responders if n != bot_name])
                    typing_delay()
                    reaction = chat_with_bot(reactor, reply, speaker=bot_name, style="very_short")
                    shared_log.append({"speaker": reactor, "message": reaction})
                    display_message(reactor, reaction, BOTS[reactor]["color"])
                    console.print()

            # Late joiner?
            maybe_late_joiner(responders)

if __name__ == "__main__":
    main()