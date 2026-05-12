import ollama
from rich.console import Console
from rich.panel import Panel

console = Console()

MODEL = "llama3.2"

# Each bot has a name and a personality (system prompt)
BOTS = {
    "Arin": {
        "system": "You are Arin, a passionate ML Engineer. You love discussing machine learning, neural networks, and data. You speak with enthusiasm about models and training. Keep responses SHORT — 3 to 4 sentences max. You are in an informal group chat with engineers.",
        "color": "cyan",
        "history": []
    },
    "Dev": {
        "system": "You are Dev, a pragmatic DevOps Engineer. You always think about infrastructure, deployment, scalability, and cost. You are slightly sarcastic but friendly. Keep responses SHORT — 3 to 4 sentences max. You are in an informal group chat with engineers.",
        "color": "green",
        "history": []
    },
}

def chat_with_bot(bot_name, user_message):
    bot = BOTS[bot_name]

    # Add user message to this bot's history
    bot["history"].append({
        "role": "user",
        "content": user_message
    })

    # Call Ollama with the bot's personality and conversation history
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "system", "content": bot["system"]}] + bot["history"]
    )

    reply = response["message"]["content"]

    # Add bot's reply to history so it remembers later
    bot["history"].append({
        "role": "assistant",
        "content": reply
    })

    return reply

def main():
    console.print(Panel("Welcome to AI Chatroom!", style="bold magenta"))
    console.print("[dim]Type your message and press Enter. Type 'quit' to exit.[/dim]\n")

    while True:
        # Get your message
        user_input = input("You: ").strip()

        if user_input.lower() == "quit":
            console.print("\n[bold magenta]Goodbye comrade![/bold magenta]")
            break

        if not user_input:
            continue

        console.print()

        # Each bot responds one by one
        for bot_name, bot_data in BOTS.items():
            reply = chat_with_bot(bot_name, user_input)
            console.print(Panel(
                reply,
                title=f"[bold {bot_data['color']}]{bot_name}[/bold {bot_data['color']}]",
                border_style=bot_data["color"]
            ))
            console.print()

if __name__ == "__main__":
    main()