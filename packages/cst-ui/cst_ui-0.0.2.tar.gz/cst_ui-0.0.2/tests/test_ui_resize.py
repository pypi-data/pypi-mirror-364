import flet as ft
import cst_ui as ui


from flet.canvas import CanvasResizeEvent

app = ui.App(route_init="/response")


class ResponseTest(ft.Row):
    def __init__(self):
        super().__init__()
        self.controls = [
            ui.ResponsiveControl(
                ft.Container(
                    content=ft.Text("W x H"),
                    bgcolor=ft.Colors.GREEN_400,
                    alignment=ft.Alignment.CENTER,
                ),
                expand=1,
                show_resize=True,
            ),
            ui.ResponsiveControl(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ui.ResponsiveControl(
                                content=ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Container(
                                                bgcolor=ft.Colors.DEEP_ORANGE_50,
                                                height=170,
                                                margin=5,
                                            ),
                                            ft.Container(bgcolor=ft.Colors.BLACK87, height=170, margin=5),
                                        ],
                                        scroll=ft.ScrollMode.HIDDEN,
                                        spacing=0,
                                    ),
                                    bgcolor=ft.Colors.BROWN_500,
                                    expand=True,
                                    margin=ft.Margin(5, 5, 0, 5),
                                ),
                                expand=1,
                                show_resize=True,
                            ),
                            ui.ResponsiveControl(
                                content=ft.Container(
                                    content=ft.Text(
                                        "ok",
                                    ),
                                    bgcolor=ft.Colors.CYAN_500,
                                    alignment=ft.Alignment.CENTER,
                                    margin=ft.Margin(0, 5, 5, 5),
                                ),
                                expand=1,
                                show_resize=True,
                            ),
                        ],
                        expand=1,
                        spacing=0,
                    ),
                    bgcolor=ft.Colors.AMBER_600,
                    alignment=ft.Alignment.CENTER,
                ),
                show_resize=True,
                expand=3,
            ),
        ]
        self.expand = 2


@app.page(route="/response")
def response_page(data: ui.DataAdmin):
    page = data.page
    page.title = "Response"

    def handle_resize(e: CanvasResizeEvent):
        c = e.control.content
        t = c.content
        t.value = f"{e.width} x {e.height}"
        page.update()

    return ft.View(
        controls=[
            ui.ResponsiveControl(
                content=ft.Container(
                    content=ft.Text("W x H"),
                    bgcolor=ft.Colors.RED,
                    alignment=ft.Alignment.CENTER,
                    height=100,
                ),
                expand=1,
                show_resize=True,
            ),
            ui.ResponsiveControl(
                ft.Container(content=ft.Text("W x H"), bgcolor=ft.Colors.BLUE, alignment=ft.Alignment.CENTER),
                on_resize=handle_resize,
                expand=1,
            ),
            ui.ResponsiveControl(content=ResponseTest(), expand=2),
        ],
    )


app.run()
