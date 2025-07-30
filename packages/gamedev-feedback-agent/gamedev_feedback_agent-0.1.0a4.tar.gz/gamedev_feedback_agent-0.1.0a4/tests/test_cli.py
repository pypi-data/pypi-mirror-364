from cli.shell import GDCFA_Shell
import pytest
from cli.command_router import route_command
from cli.commands import crawler_cmd, scheduler_cmd, view_cmd, search_cmd, database_cmd
import types
from datetime import datetime
from unittest.mock import MagicMock, patch
from pathlib import Path

# 1. test shell initialization and prompt
def test_shell_initialization_and_prompt():
    shell = GDCFA_Shell()
    assert shell is not None
    assert shell.prompt == "(gdcfa) "
    

# 2. test default command handling with valid input
def test_shell_default_command_handling(monkeypatch):
    shell = GDCFA_Shell()
    
    # Mock the route_command function to avoid actual command execution
    def mock_route_command(command, args):
        assert command == "test"
        assert args == ["arg1", "arg2"]
    
    monkeypatch.setattr("cli.command_router.route_command", mock_route_command)
    
    # test no input, should not raise an error
    shell.default("test")
    
    # Simulate input
    shell.default("test arg1 arg2")
    
    # No assertion needed, if it doesn't raise an error, it passed
    
    
# 3. test exit command
def test_shell_exit_command():
    shell = GDCFA_Shell()
    result = shell.do_exit("")
    assert result is True  # Should return True to exit the shell
    

# 4. test help command
def test_shell_help_command(monkeypatch):
    shell = GDCFA_Shell()
    
    # Mock the show_help function to avoid actual help display
    def mock_show_help(arg):
        assert arg == "test"
    
    monkeypatch.setattr("cli.commands.help_cmd.show_help", mock_show_help)
    
    # Simulate input
    shell.do_help("test")
    
    # No assertion needed, if it doesn't raise an error, it passed
    

# 5. test default command with empty input
def test_shell_default_command_empty_input(monkeypatch):
    shell = GDCFA_Shell()

    # Mock the route_command function to avoid actual command execution
    def mock_route_command(command, args):
        assert False, "route_command should not be called with empty input"

    monkeypatch.setattr("cli.command_router.route_command", mock_route_command)

    # Simulate input
    shell.default("")

    # No assertion needed, if it doesn't raise an error, it passed
    
    
# 6. test default command with invalid input
def test_shell_default_command_invalid_input(monkeypatch):
    shell = GDCFA_Shell()

    # Mock the route_command function to avoid actual command execution
    def mock_route_command(command, args):
        assert False, "route_command should not be called with invalid input"

    monkeypatch.setattr("cli.command_router.route_command", mock_route_command)

    # Simulate input
    shell.default("invalid command")

    # No assertion needed, if it doesn't raise an error, it passed
    
    
# 7. test command router
def test_route_command_calls_correct_handler(monkeypatch):
    called = {}

    def mock_handle(args):
        called['handler'] = 'crawler'
        called['args'] = args

    def mock_handle_scheduler(args):
        called['handler'] = 'scheduler'
        called['args'] = args

    def mock_handle_view(args):
        called['handler'] = 'view'
        called['args'] = args

    def mock_handle_search(args):
        called['handler'] = 'search'
        called['args'] = args

    def mock_handle_search_similar(args):
        called['handler'] = 'search_similar'
        called['args'] = args

    def mock_handle_database(args):
        called['handler'] = 'database'
        called['args'] = args

    monkeypatch.setattr("cli.commands.crawler_cmd.handle", mock_handle)
    monkeypatch.setattr("cli.commands.scheduler_cmd.handle", mock_handle_scheduler)
    monkeypatch.setattr("cli.commands.view_cmd.handle", mock_handle_view)
    monkeypatch.setattr("cli.commands.search_cmd.handle_search", mock_handle_search)
    monkeypatch.setattr("cli.commands.search_cmd.handle_search_similar", mock_handle_search_similar)
    monkeypatch.setattr("cli.commands.database_cmd.handle", mock_handle_database)


    route_command("crawler", ["arg1"])
    assert called['handler'] == "crawler"
    assert called['args'] == ["arg1"]

    route_command("scheduler", ["arg2"])
    assert called['handler'] == "scheduler"
    assert called['args'] == ["arg2"]

    route_command("view", ["arg3"])
    assert called['handler'] == "view"
    assert called['args'] == ["arg3"]

    route_command("search", ["arg4"])
    assert called['handler'] == "search"
    assert called['args'] == ["arg4"]

    route_command("search_similar", ["arg5"])
    assert called['handler'] == "search_similar"
    assert called['args'] == ["arg5"]

    route_command("database", ["arg6"])
    assert called['handler'] == "database"
    assert called['args'] == ["arg6"]


# 8. test command router with unknown command
def test_route_command_with_unknown_command(capsys):
    route_command("unknown", ["foo"])
    captured = capsys.readouterr()
    assert "Unknown command: unknown" in captured.out

# 9. test command router with no arguments
def test_route_command_with_no_args(monkeypatch):
    called = False

    def mock_handle(args):
        nonlocal called
        called = True

    monkeypatch.setattr("cli.commands.crawler_cmd.handle", mock_handle)
    route_command("crawler", [])
    assert not called


# 10. test crawler command
def test_crawler_command(monkeypatch):
    # Mock each crawler's run method to verify correct instantiation and call
    called = {}

    class MockRedditCrawler:
        def __init__(self, **kwargs):
            called['platform'] = 'reddit'
            called['kwargs'] = kwargs
        def run(self):
            called['ran'] = True

    class MockSteamCrawler:
        def __init__(self, **kwargs):
            called['platform'] = 'steam'
            called['kwargs'] = kwargs
        def run(self):
            called['ran'] = True

    class MockSteamDiscussionCrawler:
        def __init__(self, **kwargs):
            called['platform'] = 'steam_discussion'
            called['kwargs'] = kwargs
        def run(self):
            called['ran'] = True

    class MockDiscordCrawler:
        def __init__(self, **kwargs):
            called['platform'] = 'discord'
            called['kwargs'] = kwargs
        def run(self):
            called['ran'] = True
            
    def mock_run_reddit(args):
        called['platform'] = args.platform
        called['kwargs'] = vars(args)
        called['ran'] = True

    def mock_run_steam(args):
        called['platform'] = args.platform
        called['kwargs'] = vars(args)
        called['ran'] = True
        
    def mock_run_steam_discussion(args):
        called['platform'] = args.platform
        called['kwargs'] = vars(args)
        called['ran'] = True
        
    def mock_run_discord(args):
        called['platform'] = args.platform
        called['kwargs'] = vars(args)
        called['ran'] = True
        called['kwargs']['channel_ids'] = [str(x) for x in args.channels]  # Ensure IDs are strings


    monkeypatch.setattr("crawlers.reddit_crawler.RedditCrawler", MockRedditCrawler)
    monkeypatch.setattr("crawlers.steam_crawler.SteamCrawler", MockSteamCrawler)
    monkeypatch.setattr("crawlers.steam_discussion_crawler.SteamDiscussionCrawler", MockSteamDiscussionCrawler)
    monkeypatch.setattr("crawlers.discord_crawler.DiscordCrawler", MockDiscordCrawler)
    
    monkeypatch.setattr("cli.commands.crawler_cmd.run_reddit", mock_run_reddit)
    monkeypatch.setattr("cli.commands.crawler_cmd.run_steam", mock_run_steam)
    monkeypatch.setattr("cli.commands.crawler_cmd.run_steam_discussion", mock_run_steam_discussion)
    monkeypatch.setattr("cli.commands.crawler_cmd.run_discord", mock_run_discord)


    # Test reddit
    called.clear()
    crawler_cmd.handle(["reddit", "--subreddits", "testsub", "--max_posts", "1"])
    print("[DEBUG] called:", called)
    assert called['platform'] == "reddit"
    assert called['kwargs']['subreddits'] == ["testsub"]
    assert called['ran']

    # Test steam
    called.clear()
    crawler_cmd.handle(["steam", "--app_id", "123", "--fetch_review"])
    assert called['platform'] == "steam"
    assert called['kwargs']['app_id'] == "123"
    assert called['kwargs']['fetch_review'] is True
    assert called['ran']

    # Test steam_discussion
    called.clear()
    crawler_cmd.handle(["steam_discussion", "--app_id", "456"])
    assert called['platform'] == "steam_discussion"
    assert called['kwargs']['app_id'] == "456"
    assert called['ran']

    # Test discord
    called.clear()
    crawler_cmd.handle(["discord", "--channels", "789"])
    assert called['platform'] == "discord"
    assert called['kwargs']['channel_ids'] == [789] or called['kwargs']['channel_ids'] == ["789"]
    assert called['ran']
    
    
# 11. test scheduler command
def test_scheduler_command(monkeypatch):
    # Mocks for scheduler engine_utils functions
    called = {}

    def mock_list_jobs(scheduler_inst):
        called['action'] = 'list'

    def mock_pause_job(scheduler_inst, job_id):
        called['action'] = 'pause'
        called['job_id'] = job_id

    def mock_resume_job(scheduler_inst, job_id):
        called['action'] = 'resume'
        called['job_id'] = job_id

    def mock_remove_job(scheduler_inst, job_id):
        called['action'] = 'delete'
        called['job_id'] = job_id

    def mock_run_job_now(scheduler_inst, job_id):
        called['action'] = 'run_now'
        called['job_id'] = job_id

    def mock_clear_all_jobs(scheduler_inst):
        called['action'] = 'clear'

    def mock_add_job_crawler(scheduler_inst, job_cfg):
        called['action'] = 'add'
        called['job_cfg'] = job_cfg

    def mock_get_job_by_name(scheduler_inst, job_name):
        return None

    # Patch all engine_utils functions
    monkeypatch.setattr("cli.commands.scheduler_cmd.list_jobs", mock_list_jobs)
    monkeypatch.setattr("cli.commands.scheduler_cmd.pause_job", mock_pause_job)
    monkeypatch.setattr("cli.commands.scheduler_cmd.resume_job", mock_resume_job)
    monkeypatch.setattr("cli.commands.scheduler_cmd.remove_job", mock_remove_job)
    monkeypatch.setattr("cli.commands.scheduler_cmd.run_job_now", mock_run_job_now)
    monkeypatch.setattr("cli.commands.scheduler_cmd.clear_all_jobs", mock_clear_all_jobs)
    monkeypatch.setattr("cli.commands.scheduler_cmd.add_job_crawler", mock_add_job_crawler)
    monkeypatch.setattr("cli.commands.scheduler_cmd.get_job_by_name", mock_get_job_by_name)

    # Patch input for clear confirmation
    monkeypatch.setattr("builtins.input", lambda _: "y")

    # Patch os.path.exists for add command
    monkeypatch.setattr("os.path.exists", lambda path: True)
    # Patch open for add command
    import builtins
    from io import StringIO  # optional, if you want easier json.load support

    real_open = builtins.open  # backup the real open

    def safe_open(path, mode="r", *args, **kwargs):
        if "dummy.json" in str(path):
            return StringIO('{"name": "job1"}')  # or your DummyFile if preferred
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", safe_open)


    import cli.commands.scheduler_cmd as scheduler_cmd

    # list
    called.clear()
    scheduler_cmd.handle(["list"])
    assert called['action'] == "list"

    # pause
    called.clear()
    scheduler_cmd.handle(["pause", "abc"])
    assert called['action'] == "pause"
    assert called['job_id'] == "abc"

    # resume
    called.clear()
    scheduler_cmd.handle(["resume", "abc"])
    assert called['action'] == "resume"
    assert called['job_id'] == "abc"

    # delete
    called.clear()
    scheduler_cmd.handle(["delete", "abc"])
    assert called['action'] == "delete"
    assert called['job_id'] == "abc"

    # run_now
    called.clear()
    scheduler_cmd.handle(["run_now", "abc"])
    assert called['action'] == "run_now"
    assert called['job_id'] == "abc"

    # clear
    called.clear()
    scheduler_cmd.handle(["clear"])
    assert called['action'] == "clear"

    # add
    called.clear()
    scheduler_cmd.handle(["add", "--path", "dummy.json"])
    assert called['action'] == "add"
    assert isinstance(called['job_cfg'], dict)

    # crawling (reddit, interval)
    called.clear()
    scheduler_cmd.handle([
        "crawling", "--platform", "reddit", "--subreddits", "testsub",
        "--interval", "6h"
    ])
    assert called['action'] == "add"
    assert called['job_cfg']['platform'] == "reddit"
    assert called['job_cfg']['params']['subreddits'] == ["testsub"]

    # crawling (steam, daily_at)
    called.clear()
    scheduler_cmd.handle([
        "crawling", "--platform", "steam", "--app_id", "123",
        "--daily_at", "12:00"
    ])
    assert called['action'] == "add"
    assert called['job_cfg']['platform'] == "steam"
    assert called['job_cfg']['params']['app_id'] == "123"

    # crawling (discord, weekly)
    called.clear()
    scheduler_cmd.handle([
        "crawling", "--platform", "discord", "--channels", "789",
        "--weekly", "--day", "fri"
    ])
    assert called['action'] == "add"
    assert called['job_cfg']['platform'] == "discord"
    assert called['job_cfg']['params']['channel_ids'] == ["789"]
    
    
# 12. test view command
def test_view_command(monkeypatch, capsys):
    # Dummy row object with .name
    class DummyRow:
        def __init__(self, name): 
            self.name = name
            self.studio = "Studio A"
            self.title = name
            self.post_type = "reddit_post"

    # Dummy Post object
    class DummyPost:
        post_id = 1
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        platform_id = 1
        post_type = "reddit_post"
        content = "This is a test search post content."
        language = "en"
        
    class DummyPostTypeQuery:
        def all(self):
            return [("reddit_post", 1)]

    # Dummy query that mimics SQLAlchemy behavior
    class DummyQuery:
        def __init__(self, model=None):
            self.model = model
            self._all = []
        def all(self):
            if getattr(self.model, "__name__", "") == "Platform":
                return [DummyRow("reddit")]
            if getattr(self.model, "__name__", "") == "Tag":
                return [DummyRow("testtag")]
            if getattr(self.model, "__name__", "") == "Game":
                return [DummyRow("Game 1")]
            
            return self._all or [DummyPost()]
        def distinct(self):
            return DummyPostTypeQuery()
        def count(self):
            model_name = getattr(self.model, "__name__", "")
            return {
                "Post": 1,
                "Platform": 2,
                "Author": 3,
                "Game": 4,
                "Tag": 5,
                "Alert": 6
            }.get(model_name, 0)
        def filter(self, *args, **kwargs): _ = args, kwargs; return self
        def join(self, *args, **kwargs): return self
        def outerjoin(self, *args, **kwargs): return self
        def order_by(self, *args, **kwargs): return self
        def limit(self, *args, **kwargs): return self
        def first(self):
            if self.model == "Platform.name":
                return ("reddit",)
            return (datetime(2024, 1, 1, 12, 0, 0),)

    # Dummy session
    class DummySession:
        def __init__(self, bind=None): _ = bind
        def query(self, model): return DummyQuery(model)
        def close(self): pass

    # Patch CLI command dependencies
    monkeypatch.setattr("cli.commands.view_cmd.get_session", lambda bind=None: DummySession())
    monkeypatch.setattr("cli.commands.view_cmd.or_", lambda *args: args)
    monkeypatch.setattr("cli.commands.view_cmd.and_", lambda *args: args)

    import cli.commands.view_cmd as view_cmd
    
    # Patch the engine to simulate a successful connection
    with patch("cli.commands.view_cmd.get_session") as mock_connect:
        # Simulate successful connection context manager
        mock_connect.connect.return_value.__enter__.return_value = None

        # Run the CLI command
        view_cmd.handle(["platforms"])

        # Confirm it connected
        mock_connect.assert_called()
        
    # # patch the engine to simulate a failed connection
    # with patch("cli.commands.view_cmd.get_session") as mock_connect:
    #     # Simulate a connection error
    #     mock_connect.return_value.connect.side_effect = Exception("Connection failed")

    #     # Run the CLI command
    #     view_cmd.handle(["platforms"])

    #     # Confirm it raised an error
    #     out = capsys.readouterr().out
    #     assert "[Database Error] Could not connect to the database: Connection failed" in out

        
    # Test platforms
    view_cmd.handle(["platforms"])
    out = capsys.readouterr().out
    assert "- reddit" in out
    
    # Test tags
    view_cmd.handle(["tags"])
    out = capsys.readouterr().out
    assert "- testtag" in out
    
    # Test games
    view_cmd.handle(["games"])
    out = capsys.readouterr().out
    assert "- Game 1 (studio: Studio A)" in out
    
    # Test sources
    view_cmd.handle(["sources"])
    out = capsys.readouterr().out
    assert "- reddit_post" in out

    # Test stats
    view_cmd.handle(["stats"])
    out = capsys.readouterr().out
    assert "Total Posts: 1" in out
    assert "Total Platforms: 2" in out
    assert "Total Authors: 3" in out
    assert "Total Games: 4" in out
    assert "Total Tags: 5" in out
    assert "Total Alerts: 6" in out
    assert "Last Update: 2024-01-01" in out

    # Test posts with filters
    view_cmd.handle(["posts", "--platform", "reddit", "--type", "reddit_post", "--keywords", "search"])
    out = capsys.readouterr().out
    assert "Found 1 posts" in out
    assert "[1] 2024-01-01" in out
    assert "reddit_post" in out
    # language flag
    view_cmd.handle(["posts", "--platform", "reddit", "--type", "reddit_post", "--keywords", "search", "--language", "en"])
    out = capsys.readouterr().out
    assert "Found 1 posts" in out
    assert "[1] 2024-01-01" in out
    assert "reddit_post" in out
    assert "en" in out

    # Test tables
    tables = [
        "Platform",
        "Author",
        "Post",
        "Game",
        "Tag",
        "Alert",
        "Analysis",
        "Embedding",
        "GamePost",
        "PostTag",
    ]

    for table in tables:
        view_cmd.handle(["tables", table])
        out = capsys.readouterr().out
        assert f"Rows in table {table}:" in out
        
    view_cmd.handle(["tables", "NonExistentTable"])
    out = capsys.readouterr().out
    assert f"Unknown table: NonExistentTable" in out
    
    
    # test analysisdef test_view_analysis_command(monkeypatch, capsys):
    # Dummy Analysis object
    class DummyAnalysis:
        def __init__(self, post_id=1, sentiment_label="positive", sentiment_score=0.9, priority_score=0.8):
            self.post_id = post_id
            self.sentiment_label = sentiment_label
            self.sentiment_score = sentiment_score
            self.priority_score = priority_score

    # Dummy SQLAlchemy-like query
    class DummyAnalysisQuery:
        def __init__(self):
            self._all = [DummyAnalysis()]
        def filter(self, *args, **kwargs): return self
        def join(self, *args, **kwargs): return self
        def order_by(self, *args, **kwargs): return self
        def limit(self, *args, **kwargs): return self
        def all(self): return self._all

    class DummyPlatformQuery:
        def filter(self, *args, **kwargs): return self
        def first(self): return (1,)

    class DummyCountQuery:
        def scalar(self): return 1
        def join(self, *args, **kwargs): return self
        def filter(self, *args, **kwargs): return self
        def order_by(self, *args, **kwargs): return self
        def limit(self, *args, **kwargs): return self
        def all(self): return [DummyAnalysis()]

    # Dummy Session that responds with proper mock objects
    from database.db_models import Platform, Analysis
    from sqlalchemy.sql.functions import Function
    class DummySessionAnalysis:
        def __init__(self, bind=None):
            pass

        def query(self, model):
            # func.count(Analysis.post_id)
            if isinstance(model, Function) or callable(model):
                return DummyCountQuery()

            # SELECT Platform.platform_id
            if model is Platform.platform_id:
                return DummyPlatformQuery()

            # SELECT * FROM Analysis
            if model is Analysis:
                return DummyAnalysisQuery()

            return DummyAnalysisQuery()  # default fallback

        def close(self):
            pass

    # Patch dependencies
    monkeypatch.setattr("cli.commands.view_cmd.Session", lambda bind=None: DummySessionAnalysis())
    # Patch get_session to return a dummy session object with .connect()
    class DummyConnection:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
    class DummySessionWithConnect(DummySessionAnalysis):
        def connect(self):
            return DummyConnection()
    monkeypatch.setattr("cli.commands.view_cmd.get_session", lambda: DummySessionWithConnect())

    # Run CLI command
    view_cmd.handle(["analysis", "--platform", "reddit"])
    out = capsys.readouterr().out

    # Assertions
    assert "Found 1 analyses:" in out
    assert "[Post ID: 1" in out
    assert "Platform: reddit" in out
    assert "Sentiment: positive" in out
    assert "Total Analyses: 1" in out
    
    
# test alert command
def test_view_alert_command(monkeypatch, capsys):
    # --- Mock Labelable Column Wrapper ---
    class DummyLabelColumn:
        def __init__(self, value):
            self.value = value
        def label(self, name):
            return self
        def __str__(self):
            return self.value
        def __repr__(self):
            return self.value

    # --- Dummy Models ---
    class DummyColumn:
        def __init__(self, value=None):
            self.value = value
        def desc(self):
            return f"{self.value or 'column'}.desc()"
        def __eq__(self, other): return True
        def __ge__(self, other): return True
        def __le__(self, other): return True

    class DummyAlert:
        post_id = 1
        triggered_at = DummyColumn("2024-01-01")
        alert_type = "sentiment"
        alert_id = 1
        def __init__(self, alert_id=1, triggered_at="2024-01-01", alert_type="sentiment"):
            self.alert_id = alert_id
            self.triggered_at = triggered_at
            self.alert_type = alert_type
            self.post_id = 1

    class DummyGame:
        title = DummyLabelColumn("Game 1")
        game_id = 1

    class DummyPlatform:
        name = DummyLabelColumn("reddit")
        platform_id = 1

    class DummyPost:
        post_id = 1
        platform_id = 1

    class DummyGamePost:
        post_id = 1
        game_id = 1

    # --- Dummy Query Logic ---
    class DummyAlertQuery:
        def __init__(self):
            self._filters = []
            self._order = None
            self._limit = None
        def join(self, *args, **kwargs): return self
        def filter(self, *args, **kwargs): self._filters.append((args, kwargs)); return self
        def order_by(self, *args, **kwargs): self._order = args; return self
        def limit(self, val): self._limit = val; return self
        def all(self):
            return [(DummyAlert(), DummyGame.title, DummyPlatform.name)]

    # --- Dummy Session ---
    class DummySession:
        def __init__(self, bind=None): pass
        def query(self, *args, **kwargs):
            return DummyAlertQuery()
        def close(self): pass

    # --- Monkeypatch dependencies ---
    monkeypatch.setattr("cli.commands.view_cmd.Session", lambda bind=None: DummySession())
    monkeypatch.setattr("cli.commands.view_cmd.Alert", DummyAlert)
    monkeypatch.setattr("cli.commands.view_cmd.Game", DummyGame)
    monkeypatch.setattr("cli.commands.view_cmd.Platform", DummyPlatform)
    monkeypatch.setattr("cli.commands.view_cmd.Post", DummyPost)
    monkeypatch.setattr("cli.commands.view_cmd.GamePost", DummyGamePost)
    # Patch get_session to return a dummy session object with .connect()
    class DummyConnection:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
    class DummySessionWithConnect(DummySession):
        def connect(self):
            return DummyConnection()
    monkeypatch.setattr("cli.commands.view_cmd.get_session", lambda: DummySessionWithConnect())

    # --- Run command ---
    view_cmd.handle(["alerts"])
    out = capsys.readouterr().out

    # --- Assert output ---
    assert "Found 1 alerts:" in out
    assert "[1] 2024-01-01 | reddit | Game 1 | sentiment" in out

    
# 13. test search command
def test_search_command(monkeypatch, capsys):
    # Dummy field object to simulate .ilike() behavior
    class DummyField:
        def ilike(self, value):
            return f"ILIKE({value})"
    
    class DummyTimestamp:
        def __init__(self, value):
            self.value = value
        def desc(self):
            return f"DESC({self.value})"

    # Dummy Post model
    class DummyPostModel:
        content = DummyField()
        platform_id = 1
        timestamp = DummyTimestamp("2024-01-01")
        __name__ = "Post"

    # Dummy Post query result
    class DummyPostRow:
        post_id = 1
        timestamp = "2024-01-01"
        platform_id = 1
        content = "This is a test search post content."

    # Dummy query logic
    class DummyQuery:
        def __init__(self, model=None):
            self.model = model
        def filter(self, *args, **kwargs): return self
        def order_by(self, *args): return self
        def limit(self, *args): return self
        def all(self): return [DummyPostRow()]
        def first(self): return ("reddit",)

    # Dummy session for database calls
    class DummySession:
        def __init__(self, bind=None): pass
        def query(self, model):
            return DummyQuery(model)
        def close(self): pass

    # Patch CLI dependencies
    monkeypatch.setattr("cli.commands.search_cmd.get_session", lambda bind=None: DummySession())
    monkeypatch.setattr("cli.commands.search_cmd.Post", DummyPostModel)
    monkeypatch.setattr("cli.commands.search_cmd.Platform", type("Platform", (), {"__name__": "Platform", "name": DummyField(), "platform_id": 1}))

    import cli.commands.search_cmd as search_cmd

    # Run basic search
    search_cmd.handle_search(["test"])
    out = capsys.readouterr().out
    assert "search posts by keyword string" in out
    assert "[1] 2024-01-01 | reddit | This is a test search post content." in out
    assert "Found 1 posts matching 'test'" in out

    # Run quoted string search
    search_cmd.handle_search(['"switch 2"'])
    out = capsys.readouterr().out
    assert '"switch 2"' in out

    # Run search with platform filter
    search_cmd.handle_search(["switch", "--platform", "steam"])
    out = capsys.readouterr().out
    assert "Found 1 posts matching 'switch'" in out
    
    
def test_search_invalid_command(capsys):
    search_cmd.handle_search(["nonexistent", "--platform", "nonexistent"])
    out = capsys.readouterr().out
    assert "[Search Error] Platform 'nonexistent' not found." in out
    

# 14. test database command
def test_database_command(monkeypatch, capsys):
    import cli.commands.database_cmd as database_cmd
    
    # --- list_json ---
    called = {}

    class DummyPath:
        def __init__(self, name):
            self.name = name
        def glob(self, pattern):
            if pattern == "*.jsonl":
                return [DummyPath("file1.jsonl")]
            if pattern == "*.json":
                return [DummyPath("file2.json")]
            return []

    def mock_get_context():
        return {"data_dir": DummyPath("dummy_dir")}

    monkeypatch.setattr("cli.commands.database_cmd.get_context", mock_get_context)

    # check context
    with patch("cli.commands.database_cmd.get_context") as mock_get_context:
        mock_get_context.return_value = {"data_dir": DummyPath("dummy_dir")}
        database_cmd.handle(["list_json"])
        mock_get_context.assert_called_once()

    database_cmd.handle(["list_json"])
    out = capsys.readouterr().out
    assert "[DB] Local JSON files:" in out
    assert "file1.jsonl" in out
    assert "file2.json" in out

    # --- insert_json ---
    called = {}

    def mock_bulk_insert_from_file(path):
        called['inserted'] = 3
        called['path'] = path
        return [1,2,3]

    monkeypatch.setattr("cli.commands.database_cmd.bulk_insert_from_file", mock_bulk_insert_from_file)

    database_cmd.handle(["insert_json", "--path", "dummy.json"])
    out = capsys.readouterr().out
    assert "[DB] Inserted 3 records from dummy.json" in out
    assert called['inserted'] == 3
    assert called['path'] == "dummy.json"

    # --- add row ---
    class DummyModel:
        __table__ = type("Table", (), {"columns": []})()
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    # Simulate a table with two columns: id (PK, int), name (str, not null)
    class DummyColumn:
        def __init__(self, name, type_, primary_key=False, nullable=True, default=None):
            self.name = name
            self.type = type_
            self.primary_key = primary_key
            self.nullable = nullable
            self.default = default

    class DummyInt:
        __name__ = "Integer"
    class DummyStr:
        __name__ = "String"

    DummyModel.__table__.columns = [
        DummyColumn("id", DummyInt(), primary_key=True, nullable=False),
        DummyColumn("name", DummyStr(), primary_key=False, nullable=False),
        DummyColumn("desc", DummyStr(), primary_key=False, nullable=True),
    ]

    # Patch TABLE_REGISTRY and engine/session
    monkeypatch.setitem(database_cmd.TABLE_REGISTRY, "dummy", DummyModel)
    class DummySession:
        def __init__(self, bind=None): self.committed = False; self.closed = False; self.added = None
        def add(self, row): self.added = row
        def commit(self): self.committed = True
        def close(self): self.closed = True
    monkeypatch.setattr("cli.commands.database_cmd.Session", lambda bind=None: DummySession())
    monkeypatch.setattr("cli.commands.database_cmd.get_session", lambda: DummySession())

    # Patch get_values_dict to simulate CLI parsing
    def mock_get_values_dict(prompt):
        # Simulate parsing a string like "name=bar"
        result = {}
        for pair in prompt.split(","):
            if "=" in pair:
                k, val = pair.split("=", 1)
                result[k.strip()] = val.strip()
        return result


    monkeypatch.setattr("cli.commands.database_cmd.get_values_dict", mock_get_values_dict)

    # Test add row success
    database_cmd.handle(["add", "--table", "dummy", "--values", "name=bar"])
    out = capsys.readouterr().out
    assert "[DB] Added new row to 'dummy': {'name': 'bar'}" in out

    # Test add row missing required column
    database_cmd.handle(["add", "--table", "dummy", "--values", "id=3"])
    out = capsys.readouterr().out
    assert "Missing value for column 'name'" in out

    # Test add row with unknown table
    database_cmd.handle(["add", "--table", "notfound", "--values", "id=4,name=foo"])
    out = capsys.readouterr().out
    assert "Table 'notfound' not found in the database schema" in out

    # Test add row with no values
    database_cmd.handle(["add", "--table", "dummy"])
    out = capsys.readouterr().out
    assert "Invalid command or arguments" in out

    # --- show table ---
    class DummyRow:
        def __init__(self, id, name, desc):
            self.id = id
            self.name = name
            self.desc = desc
        __table__ = DummyModel.__table__

    def mock_get_table_rows(session, table, limit):
        return [DummyRow(1, "foo", "bar")]

    monkeypatch.setattr("cli.commands.database_cmd.get_table_rows", mock_get_table_rows)

    database_cmd.handle(["show", "--table", "dummy", "--limit", "1"])
    out = capsys.readouterr().out
    assert "{'id': 1, 'name': 'foo', 'desc': 'bar'}" in out
    
    # --- export json ---
    called = {}
    # Simulate export_to_json and get_context
    def mock_export_to_json(table_names, output_path):
        called['exported'] = True
        called['tables'] = table_names
        called['output_path'] = output_path
        return True

    monkeypatch.setattr("cli.commands.database_cmd.export_to_json", mock_export_to_json)

    def mock_get_context_export():
        return {"workspace": Path("dummy_workspace")}

    monkeypatch.setattr("cli.commands.database_cmd.get_context", mock_get_context_export)

    # Test export_json with tables and path
    called.clear()
    database_cmd.handle(["export_json", "--tables", "dummy", "--path", "out.json"])
    out = capsys.readouterr().out
    assert called['exported'] is True
    assert "Exported tables to JSON files" in out

    # Test export_json with missing path
    called.clear()
    database_cmd.handle(["export_json", "--tables", "dummy"])
    out = capsys.readouterr().out
    assert "Invalid command or arguments" in out

    # Test export_json with invalid path
    called.clear()
    database_cmd.handle(["export_json", "--tables", "dummy", "--path", "out.txt"])
    out = capsys.readouterr().out
    assert "--path must be a valid JSON file path ending with .json or .jsonl" in out

    # Test export_json with no tables
    monkeypatch.setattr("cli.commands.database_cmd.TABLE_REGISTRY", {"dummy": object()})

    # Test export_json with no tables (should fallback to TABLE_REGISTRY.keys())
    assert list(database_cmd.TABLE_REGISTRY.keys())[0] == "dummy"
    
    called.clear()
    database_cmd.handle(["export_json", "--path", "out.json"])
    out = capsys.readouterr().out
    assert called['exported'] is True
    assert "Exported tables to JSON files" in out
    
# 15. test help command
def test_help_command(monkeypatch, capsys):
    import cli.commands.help_cmd as help_cmd

    # Test general help (no arg)
    help_cmd.show_help("")
    out = capsys.readouterr().out
    assert "Available commands:" in out
    assert "crawler <platform> <options>" in out

    # Test crawler help
    help_cmd.show_help("crawler")
    out = capsys.readouterr().out
    assert "Available platforms: reddit, steam, discord" in out
    assert "available options for reddit" in out

    # Test scheduler help
    help_cmd.show_help("scheduler")
    out = capsys.readouterr().out
    assert "scheduler list" in out
    assert "Available platforms: reddit, steam, discord" in out

    # Test unknown command
    help_cmd.show_help("unknowncmd")
    out = capsys.readouterr().out
    assert "No help found for 'unknowncmd'" in out