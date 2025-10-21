import reflex as rx
from app.state import ChatState, Message


def header() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.icon("message-circle", class_name="h-8 w-8 text-purple-600"),
            rx.el.h1(
                "HTML Chat Renderer",
                class_name="text-2xl font-bold text-gray-800 tracking-tight",
            ),
            class_name="flex items-center gap-3",
        ),
        class_name="w-full p-4 border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10",
    )


def message_bubble(message: Message) -> rx.Component:
    is_user = message["sender"] == "user"
    return rx.el.div(
        rx.el.div(
            rx.el.p(message["text"], class_name="text-sm md:text-base"),
            rx.cond(
                message["html_content"] != None,
                rx.el.button(
                    rx.icon("file-code", class_name="h-4 w-4 mr-2"),
                    rx.el.span("Click to view HTML output"),
                    on_click=ChatState.show_html_in_panel(message["html_content"]),
                    class_name="mt-2 flex items-center text-left w-full bg-white border border-gray-200 rounded-lg p-3 hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm",
                ),
                None,
            ),
            class_name=rx.cond(
                is_user,
                "bg-purple-600 text-white p-3 rounded-t-2xl rounded-bl-2xl",
                "bg-gray-100 text-gray-800 p-3 rounded-t-2xl rounded-br-2xl",
            ),
        ),
        class_name=rx.cond(
            is_user, "flex justify-end w-full", "flex justify-start w-full"
        ),
    )


def chat_input() -> rx.Component:
    return rx.el.div(
        rx.el.form(
            rx.el.div(
                rx.upload.root(
                    rx.el.button(
                        rx.icon("paperclip", class_name="h-5 w-5"),
                        type="button",
                        class_name="text-gray-500 hover:text-purple-600 transition-colors",
                    ),
                    id="html_upload",
                    multiple=False,
                    accept={"text/html": [".html"]},
                    on_drop=ChatState.handle_html_upload(
                        rx.upload_files(upload_id="html_upload")
                    ),
                    class_name="p-2",
                ),
                rx.el.input(
                    placeholder="Type your message...",
                    name="message_text",
                    disabled=ChatState.is_processing,
                    class_name="flex-1 bg-transparent focus:outline-none placeholder-gray-500 disabled:opacity-50",
                ),
                rx.el.button(
                    rx.icon("send", class_name="h-5 w-5"),
                    type="submit",
                    disabled=ChatState.is_processing,
                    class_name="bg-purple-600 text-white p-2 rounded-full hover:bg-purple-700 transition-colors disabled:bg-purple-300 disabled:cursor-not-allowed",
                ),
                class_name="flex items-center w-full bg-white border border-gray-200 rounded-full p-2 shadow-sm",
            ),
            on_submit=ChatState.send_message,
            reset_on_submit=True,
            width="100%",
        ),
        rx.foreach(
            rx.selected_files("html_upload"),
            lambda file: rx.el.div(
                rx.el.p(file, class_name="text-sm text-gray-500"),
                rx.el.button(
                    "Upload",
                    on_click=ChatState.handle_html_upload(
                        rx.upload_files(upload_id="html_upload")
                    ),
                    class_name="text-sm bg-purple-100 text-purple-700 px-2 py-1 rounded-md hover:bg-purple-200",
                ),
                class_name="flex justify-between items-center bg-white border rounded-lg p-2 mt-2 shadow-sm",
            ),
        ),
        class_name="w-full",
    )


def chat_interface() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.foreach(ChatState.messages, message_bubble),
            rx.cond(
                ChatState.is_processing,
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            class_name="h-2 w-2 bg-purple-300 rounded-full animate-bounce [animation-delay:-0.3s]"
                        ),
                        rx.el.div(
                            class_name="h-2 w-2 bg-purple-300 rounded-full animate-bounce [animation-delay:-0.15s]"
                        ),
                        rx.el.div(
                            class_name="h-2 w-2 bg-purple-300 rounded-full animate-bounce"
                        ),
                        class_name="flex gap-1 items-center",
                    ),
                    class_name="bg-gray-100 text-gray-800 p-3 rounded-t-2xl rounded-br-2xl w-fit",
                ),
                None,
            ),
            class_name="flex-1 space-y-4 p-4 md:p-6 overflow-y-auto",
        ),
        rx.el.div(
            chat_input(),
            class_name="p-4 border-t border-gray-200 bg-white/80 backdrop-blur-sm",
        ),
        class_name="flex flex-col h-full",
    )


def html_side_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h2("Rendered HTML", class_name="font-bold text-lg"),
                rx.el.button(
                    rx.icon("x", class_name="h-5 w-5"),
                    on_click=ChatState.close_side_panel,
                    class_name="p-1 rounded-full hover:bg-gray-100",
                ),
                class_name="flex justify-between items-center p-4 border-b",
            ),
            rx.el.div(
                rx.el.iframe(
                    src_doc=ChatState.side_panel_html_content,
                    sandbox="allow-scripts allow-same-origin allow-modals allow-forms allow-popups",
                    class_name="w-full h-full border-0",
                ),
                class_name="flex-1 overflow-auto",
            ),
            class_name="flex flex-col h-full bg-white w-full md:w-[450px] border-l shadow-2xl",
        ),
        class_name=rx.cond(
            ChatState.show_side_panel,
            "fixed top-0 right-0 h-full z-20 transition-transform transform translate-x-0 duration-300 ease-in-out",
            "fixed top-0 right-0 h-full z-20 transition-transform transform translate-x-full duration-300 ease-in-out",
        ),
    )


def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            header(),
            chat_interface(),
            class_name="relative flex flex-col h-screen max-w-2xl mx-auto bg-white border-x border-gray-200",
        ),
        html_side_panel(),
        class_name="font-['Poppins'] bg-gray-50",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index)