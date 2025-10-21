import reflex as rx
import asyncio
from typing import TypedDict, Literal


class Message(TypedDict):
    id: int
    text: str
    sender: Literal["user", "bot"]
    html_content: str | None
    show_html: bool


class ChatState(rx.State):
    messages: list[Message] = []
    message_counter: int = 0
    is_processing: bool = False
    show_side_panel: bool = False
    side_panel_html_content: str = ""

    @rx.event
    async def handle_html_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        file = files[0]
        upload_data = await file.read()
        html_content = upload_data.decode("utf-8")
        user_message = Message(
            id=self.message_counter,
            text=f"Uploaded: {file.name}",
            sender="user",
            html_content=None,
            show_html=False,
        )
        self.messages.append(user_message)
        self.message_counter += 1
        self.is_processing = True
        yield
        await asyncio.sleep(1)
        bot_message = Message(
            id=self.message_counter,
            text="I've received your HTML file. Click the preview to see it.",
            sender="bot",
            html_content=html_content,
            show_html=False,
        )
        self.messages.append(bot_message)
        self.message_counter += 1
        self.is_processing = False

    @rx.event
    def send_message(self, form_data: dict):
        message_text = form_data.get("message_text", "").strip()
        if not message_text:
            return
        user_message = Message(
            id=self.message_counter,
            text=message_text,
            sender="user",
            html_content=None,
            show_html=False,
        )
        self.messages.append(user_message)
        self.message_counter += 1
        return ChatState.process_bot_response

    def _generate_html_from_text(self, text: str) -> tuple[str, str | None]:
        text_lower = text.lower()
        if "blue button" in text_lower:
            return (
                "I've created a blue button for you.",
                '<button class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">Click me</button>',
            )
        if "card" in text_lower:
            return (
                "Here is a card component.",
                '<div class="bg-white border border-gray-200 rounded-lg shadow-md p-6 w-64"><h3 class="text-lg font-bold mb-2">Card Title</h3><p class="text-gray-600">This is some card content.</p></div>',
            )
        if "form" in text_lower:
            return (
                "Here is a simple form structure.",
                """<form class="bg-white p-6 border rounded-lg w-full max-w-sm">
  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2" for="username">
      Username
    </label>
    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="username" type="text" placeholder="Username">
  </div>
  <div class="flex items-center justify-between">
    <button class="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="button">
      Sign In
    </button>
  </div>
</form>""",
            )
        return (
            "Sorry, I didn't understand that. Try 'create a blue button' or 'show a form'.",
            None,
        )

    @rx.event(background=True)
    async def process_bot_response(self):
        async with self:
            self.is_processing = True
            last_message = self.messages[-1] if self.messages else None
        if not last_message or last_message["sender"] != "user":
            async with self:
                self.is_processing = False
            return
        await asyncio.sleep(1.5)
        async with self:
            bot_text, html_payload = self._generate_html_from_text(last_message["text"])
            bot_message = Message(
                id=self.message_counter,
                text=bot_text,
                sender="bot",
                html_content=html_payload,
                show_html=False,
            )
            self.messages.append(bot_message)
            self.message_counter += 1
            self.is_processing = False

    @rx.event
    def show_html_in_panel(self, html_content: str):
        self.side_panel_html_content = html_content
        self.show_side_panel = True

    @rx.event
    def close_side_panel(self):
        self.show_side_panel = False
        self.side_panel_html_content = ""