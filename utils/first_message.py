import inquirer

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from art import text2art


def first_message():
    console = Console()
    color = "#3985bf"

    console.print(Panel.fit(text2art("MONAD\n  COMBINE", font="small"), title="", border_style=color), style=color, end="")

    text_link = Text("@next_softs", style=color)
    text_link.stylize("link https://t.me/next_softs")
    console.print("Обновления и другие софты: ", style=color, end="")
    console.print(text_link, style=color, end="\n\n")

def get_action(actions):
    actions.append("Выход")
    questions = [
        inquirer.List(
            "action",
            message='Выберите ваше действие',
            choices=actions
        )
    ]

    action = inquirer.prompt(questions)["action"]
    if action == "Выход": exit(0)

    return action
