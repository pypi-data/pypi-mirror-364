from cli.commands import crawler_cmd, database_cmd, scheduler_cmd, search_cmd, view_cmd, init_cmd, analyze_cmd, config_cmd, intelligence_cmd, safety_cmd, alert_cmd, report_cmd

def route_command(cmd_name: str, args: list[str]) -> None:
    """Route the command to the appropriate handler.

    Args:
        cmd_name (str): The name of the command.
        args (list[str]): The arguments for the command.
    """
    if not args and cmd_name != "init":
        print(f"Usage: {cmd_name} <command> [options]")
        return

    if cmd_name == "crawler":
        crawler_cmd.handle(args)
    elif cmd_name == "scheduler":
        scheduler_cmd.handle(args)
    elif cmd_name == "view":
        view_cmd.handle(args)
    elif cmd_name == "search":
        search_cmd.handle_search(args)
    elif cmd_name == "search_similar":
        search_cmd.handle_search_similar(args)
    elif cmd_name == "search_hybrid":
        search_cmd.handle_search_hybrid(args)
    elif cmd_name == "database":
        database_cmd.handle(args)
    elif cmd_name == "analyze":
        analyze_cmd.handle(args)
    elif cmd_name == "config":
        config_cmd.handle(args)
    elif cmd_name == "intelligence":
        intelligence_cmd.handle(args)
    elif cmd_name == "safety":
        safety_cmd.handle(args)
    elif cmd_name == "alert":
        alert_cmd.handle(args)
    elif cmd_name == "report":
        report_cmd.handle(args)

    # elif cmd_name == "init":
    #     init_cmd.handle(args)
    else:
        print(f"Unknown command: {cmd_name}. Try 'help'.")
