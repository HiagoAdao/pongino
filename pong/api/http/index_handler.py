from pathlib import Path

from tornado.web import RequestHandler


class IndexHandler(RequestHandler):
    def initialize(self, web_path: Path) -> None:
        self._web_path = web_path

    def get(self) -> None:
        index_file = self._web_path / "index.html"
        if not index_file.exists():
            self.finish("<h1>Pong Retrô Distribuído</h1><p>Frontend em carregamento...</p>")
            return
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.finish(index_file.read_text(encoding="utf-8"))
