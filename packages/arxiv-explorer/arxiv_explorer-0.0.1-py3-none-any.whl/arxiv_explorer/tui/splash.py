from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static, DataTable
from textual.reactive import reactive
from textual.containers import Horizontal


class arXivExplorer(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        # ("s", "push_search_screen", "Search")
    ]

    # No need for SCREENS dictionary if instantiating manually when pushing
    # SCREENS = {
    #     "search": SearchScreen
    # }

    CSS = """
    Screen {
        layout: vertical;
    }

    #search-container {
        padding: 2;
        border: round $accent;
        margin: 1 2;
        height: auto;
    }

    #search-input {
        width: 100%;
        margin-bottom: 1;
    }

    #search-results-display {
        border: round $surface-darken-1;
        padding: 1;
        height: auto;
        min-height: 5;
        max-height: 20; /* Limit height for display */
        overflow: auto;
    }

    DataTable {
        height: 1fr; /* Use 1fr to make it flexible in vertical layout */
        width: 40%;
    }

    Static {
        padding: 1;
        border: round $accent;
        overflow: auto;
        height: 1fr; /* Use 1fr to make it flexible in vertical layout */
        width: 60%;
    }

    Horizontal {
        height: 1fr; /* Allow Horizontal container to take remaining space */
    }
    """

    def __init__(self, results: list, **kwargs):
        super().__init__(**kwargs)
        self.results = results
        self.table = DataTable()
        self.detail_panel = Static()
        self.current_row = reactive(0)

    def compose(self) -> ComposeResult:
        self.table.add_columns("Title")
        for i, row in enumerate(self.results):
            title = row[0][:50] + "..." if len(row[0]) > 50 else row[0]
            self.table.add_row(title, key=i)

        self.table.cursor_type = "row"

        yield Header()
        yield Horizontal(self.table, self.detail_panel)
        yield Footer()

    def on_mount(self):
        self.table.focus()
        self.show_details(0)
        self.query_one(Header).tall = False
        self.query_one(Header).app_title = "arXiv Explorer"

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self.show_details(event.cursor_row)

    def show_details(self, index: int):
        if 0 <= index < len(self.results):
            title, summary, published, short_id, category, pdf_url = self.results[index]
            self.detail_panel.update(
                f"[b]Title:[/b] {title}\n\n"
                f"[b]Summary:[/b]\n{summary}\n\n"
                f"[b]Published:[/b] {published}\n"
                f"[b]Category:[/b] {category}\n"
                f"[b]ABS:[/b] https://arxiv.org/abs/{short_id}\n"
                f"[b]PDF:[/b] {pdf_url}"
            )

    def action_quit(self) -> None:
        self.exit()

    # def action_push_search_screen(self):
    #     """Custom action to push the search screen, passing the app instance."""
    #     self.push_screen(SearchScreen(self))
