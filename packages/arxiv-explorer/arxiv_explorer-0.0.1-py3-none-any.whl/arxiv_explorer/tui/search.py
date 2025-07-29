from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Label, Button, Footer, Header, Static
from textual.containers import Vertical, Horizontal


class SearchScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("enter", "perform_search", "Search"),
    ]

    def __init__(self, app_ref: App, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.search_results = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="search-container"):
            yield Label("[b]Enter search query:[/b]")
            self.search_input = Input(
                placeholder="Type to search...", id="search-input"
            )
            yield self.search_input
            yield Horizontal(
                Button("Search", id="search-button", variant="primary"),
                Button("Clear", id="clear-button"),
            )
            yield Static("[b]Results:[/b]", id="search-results-label")
            self.results_display = Static(
                "No search performed yet.", id="search-results-display"
            )
            yield self.results_display
        yield Footer()

    def on_mount(self):
        self.query_one("#search-input", Input).focus()
        self.query_one(Header).tall = False
        self.query_one(Header).app_title = "Search Articles"

    def action_perform_search(self):
        query = self.search_input.value.lower()
        if not query:
            self.results_display.update("Please enter a query.")
            return

        matching_results = []
        # Access results via the app_ref
        for row in self.app_ref.results:
            # Simple case-insensitive search across title and summary
            if query in row[0].lower() or query[0] in row[1].lower():
                matching_results.append(row[0])

        if matching_results:
            self.results_display.update("\n".join(matching_results))
        else:
            self.results_display.update("No matching results found.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "search-button":
            self.action_perform_search()
        elif event.button.id == "clear-button":
            self.search_input.value = ""
            self.results_display.update("No search performed yet.")
            self.search_input.focus()
