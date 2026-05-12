import ollama
from rich.console import Console
from rich.panel import Panel
import random

console = Console()
MODEL = "llama3.2:1b"

BOTS = {
    "Arin": {
        "system": "You are Arin, a passionate ML Engineer in an informal group chat with fellow engineers. You love ML, neural networks, and data. You are enthusiastic and slightly nerdy. Keep responses to 2-3 sentences max. Be casual and fun.",
        "color": "cyan",
        "history": []
    },
    "Dev": {
        "system": "You are Dev, a pragmatic DevOps Engineer in an informal group chat with fellow engineers. You think about infra, deployment, and cost. Slightly sarcastic but friendly. Keep responses to 2-3 sentences max. Be casual and fun.",
        "color": "green",
        "history": []
    },
    "Rex": {
        "system": "You are Rex, a no-nonsense Backend Engineer in an informal group chat with fellow engineers. You are pragmatic, love clean code, hate over-engineering. Keep responses to 2-3 sentences max. Be casual and fun.",
        "color": "yellow",
        "history": []
    },
    "Chip": {
        "system": "You are Chip, the funny one in an informal group chat with fellow engineers. You crack jokes, use puns, keep things light — but you are also technically sound. Keep responses to 2-3 sentences max. Always sneak in a joke or witty remark.",
        "color": "magenta",
        "history": []
    },
}

# Shared chat log — everyone can see what everyone said
shared_log = []

def chat_with_bot(bot_name, message, speaker="You"):
    bot = BOTS[bot_name]

    # Build context from shared log so bot knows what others said
    context = "\n".join([f"{entry['speaker']}: {entry['message']}" for entry in shared_log[-10:]])

    full_message = f"Chat history:\n{context}\n\n{speaker} says: {message}\n\nRespond naturally as {bot_name}."

    bot["history"].append({"role": "user", "content": full_message})

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "system", "content": bot["system"]}] + bot["history"][-6:]
    )

    reply = response["message"]["content"]

    bot["history"].append({"role": "assistant", "content": reply})

    return reply

def display_message(speaker, message, color="white"):
    console.print(Panel(
        message,
        title=f"[bold {color}]{speaker}[/bold {color}]",
        border_style=color
    ))
    console.print()

def bot_to_bot_round(trigger_bot, trigger_message):
    """After trigger_bot speaks, one random other bot reacts to them."""
    other_bots = [name for name in BOTS if name != trigger_bot]
    reactor = random.choice(other_bots)

    reaction_prompt = f"React briefly to what {trigger_bot} just said: '{trigger_message}'"
    reaction = chat_with_bot(reactor, reaction_prompt, speaker=trigger_bot)

    shared_log.append({"speaker": reactor, "message": reaction})
    display_message(reactor, reaction, BOTS[reactor]["color"])

    return reactor, reaction

def main():
    console.print(Panel("🖥  Welcome to AI Chatroom!\nYour virtual software club is ready.", style="bold magenta"))
    console.print("[dim]Commands: 'quit' to exit | 'debate [topic]' to start a debate | just chat normally![/dim]\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "quit":
            console.print("\n[bold magenta]See you later comrade![/bold magenta]")
            break

        if not user_input:
            continue

        # Add your message to shared log
        shared_log.append({"speaker": "You", "message": user_input})
        console.print()

        # Handle debate mode
        if user_input.lower().startswith("debate "):
            topic = user_input[7:]
            console.print(f"[bold red]⚡ Debate started: {topic}[/bold red]\n")
            for bot_name, bot_data in BOTS.items():
                reply = chat_with_bot(bot_name, f"Give your strong opinion on: {topic}. Be opinionated and disagree with others if needed.", speaker="You")
                shared_log.append({"speaker": bot_name, "message": reply})
                display_message(bot_name, reply, bot_data["color"])

            # One extra round of reactions
            console.print("[dim]--- bots react to each other ---[/dim]\n")
            for bot_name in list(BOTS.keys())[:2]:
                last_message = shared_log[-1]["message"]
                last_speaker = shared_log[-1]["speaker"]
                reaction = chat_with_bot(bot_name, f"React to what {last_speaker} said.", speaker=last_speaker)
                shared_log.append({"speaker": bot_name, "message": reaction})
                display_message(bot_name, reaction, BOTS[bot_name]["color"])

        else:
            # Normal chat — all bots respond to you
            last_bot = None
            last_reply = None

            for bot_name, bot_data in BOTS.items():
                reply = chat_with_bot(bot_name, user_input)
                shared_log.append({"speaker": bot_name, "message": reply})
                display_message(bot_name, reply, bot_data["color"])

                # 40% chance a bot reacts to the previous bot
                if last_bot and random.random() < 0.4:
                    console.print("[dim]--- side conversation ---[/dim]\n")
                    bot_to_bot_round(last_bot, last_reply)

                last_bot = bot_name
                last_reply = reply

if __name__ == "__main__":
    main()