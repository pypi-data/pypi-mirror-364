import flet as ft
import cst_ui as ui

app = ui.App(route_init="/resize")


@app.page(route="/resize", title="Use resize")
def resize_page(data: ui.DataAdmin):

    # obtaining the values of the event.
    on_resize = data.on_resize

    # Modifying the customized margin.
    # on_resize.margin_y = 10

    return ft.View(
        controls=[
            ft.Container(bgcolor=ft.Colors.GREEN_600, height=on_resize.height_x(50)),
            ft.Container(bgcolor=ft.Colors.BLUE_600, height=on_resize.height_x(50), width=on_resize.width_x(50)),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        spacing=0,
        padding=0,  # Customized padding
    )


app.run()
