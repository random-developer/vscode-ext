import uuid
import json
from vscode.enums import ViewColumn
from vscode.utils import log

__all__ = (
    "WebviewPanel",
)

class WebviewPanel:
    def __init__(self, title: str, colomn: ViewColumn) -> None:
        self.title = title
        self.colomn = colomn
        self._html = ""
        self.id = str(uuid.uuid4())
        self.ws = None
        self.running = False

    @property
    def html(self) -> str:
        return self._html
    
    async def _setup(self, ws) -> None:
        self.ws = ws
        self.ws.webviews[self.id] = self
        await self.ws.run_code(
            f"""
            let p = vscode.window.createWebviewPanel('{self.id}', '{self.title}', {self.colomn}, {{ enableScripts: true }}); 
            webviews['{self.id}'] = p;

            p.webview.onDidReceiveMessage((message) => ws.send(JSON.stringify({{ type: 4, id: '{self.id}', data: message }})));
            """
            , wait_for_response=False
        )
        self.running = True

    async def set_html(self, html: str) -> None:
        if not self.running:
            raise ValueError(f"Webview is not running")
        
        self._html = html
        await self.ws.run_code(f"webviews['{self.id}'].webview.html = `{html}`", wait_for_response=False)

    async def update_title(self, title: str) -> None:
        if not self.running:
            raise ValueError(f"Webview is not running")
        
        self.title = title
        await self.ws.run_code(f"webviews['{self.id}'].title = '{title}'", wait_for_response=False)

    async def post_message(self, data: dict) -> None:
        if not self.running:
            raise ValueError(f"Webview is not running")
        
        message = json.dumps(data)
        await self.ws.run_code(f"webviews['{self.id}'].webview.postMessage({message})", wait_for_response=False)

    async def on_message(self, data: dict):
        log(f"Webview {self.id} received message: {data}")