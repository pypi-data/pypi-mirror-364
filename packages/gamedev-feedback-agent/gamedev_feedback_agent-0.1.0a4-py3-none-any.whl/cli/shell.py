import cmd
from cli.command_router import route_command
import shlex

class GDCFA_Shell(cmd.Cmd):
    intro = "Welcome to the GameDevCommunity Feedback Agent Shell. Type help or ? to list commands.\n"
    prompt = "(gdcfa) "

    def default(self, line: str) -> None:
        try:
            args = shlex.split(line, posix=False) # Use shlex to handle quoted strings correctly
            if not args:
                return
            command = args[0]
            command_args = args[1:]
            route_command(command, command_args)
        except Exception as e:
            print(f"[Shell Error] {e}")

    def do_exit(self, arg: str) -> bool:
        "Exit the shell"
        print("Exiting GameDev shell.")
        return True

    def do_help(self, arg: str) -> None:
        from cli.commands.help_cmd import show_help
        show_help(arg)

    def complete(self, text: str, state: int) -> str | None:
        # Only suggest completions if user typed something
        if not text.strip():
            return None  # Don't show anything on empty input

        top_commands = ["crawler", "scheduler", "view", "database", "search", "search_similar", "search_hybrid",
                        "exit", "help", "analyze", "config", "intelligence", "safety", "alert", "report"]
        matches = [cmd for cmd in top_commands if cmd.startswith(text)]
        try:
            return matches[state]
        except IndexError:
            return None


    def completenames(self, text: str, *ignored) -> list[str]:
        if not text:
            return []  # No suggestions if nothing is typed

        top_commands = [
            "crawler", "scheduler", "view", "database",
            "search", "search_similar", "search_hybrid", "exit", "help", "analyze", "config",
            "intelligence", "safety", "alert", "report"
        ]
        return [cmd for cmd in top_commands if cmd.startswith(text)]


def main():
    shell = GDCFA_Shell()
    shell.cmdloop()