import flet as ft
import cst_ui as ui

app = ui.App(
    route_init="/page-1",
)


# ----------------- Custom class for multiple pages to use --------------------
class Custom:
    def __init__():
        pass

    def custom_appbar(self):
        return ft.AppBar(
            title=ft.Text("App"),
            actions=[
                ft.Row(
                    controls=[
                        ft.FilledButton(
                            "Page 1",
                            on_click=self.data.go("/page-1"),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.RED_600,
                            ),
                        ),
                        ft.FilledButton(
                            "Page 2",
                            on_click=self.data.go("/page-2/100"),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.AMBER_500,
                            ),
                        ),
                    ]
                )
            ],
        )


# -------------------------------- Add page 1 --------------------------------
@app.page(route="/page-1", title="Page 1")
class Page1(Custom):
    def __init__(self, data: ui.DataAdmin):
        self.data = data

    def build(self):
        return ft.View(
            controls=[ft.Text("Page 1", size=50)],
            appbar=self.custom_appbar(),
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )


# -------------------------------- Add page 2 --------------------------------
@app.page(route="/page-2/{id}", title="Page 2")
class Page2(Custom):
    def __init__(self, data: ui.DataAdmin, id: int):
        self.data = data
        self.id = id

    def build(self):
        return ft.View(
            controls=[ft.Text(f"Page 2: \nID-URL = {self.id}", size=50)],
            appbar=self.custom_appbar(),
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )


app.run()
