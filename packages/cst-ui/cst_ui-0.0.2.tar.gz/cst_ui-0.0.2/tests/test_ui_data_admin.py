import flet as ft
import cst_ui as ui

app = ui.App(route_init="/flet-app")


@app.page(route="/flet-app", title="flet-app")
def index_page(data: ui.DataAdmin):
    return ft.View(
        controls=[
            ft.Text("Home page"),
            ft.FilledButton("Go to Counter", on_click=data.go("/counter")),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


@app.page(route="/counter", title="Counter")
def counter_page(data: ui.DataAdmin):
    page = data.page

    txt_number = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    def minus_click(e):
        txt_number.value = str(int(txt_number.value) - 1)
        page.update()

    def plus_click(e):
        txt_number.value = str(int(txt_number.value) + 1)
        page.update()

    return ft.View(
        controls=[
            ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
                        txt_number,
                        ft.IconButton(ft.Icons.ADD, on_click=plus_click),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ),
            ft.FilledButton("Go to Home", on_click=data.go("/flet-app")),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


app.run(view=ft.AppView.WEB_BROWSER)
