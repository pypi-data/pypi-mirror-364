import flet as ft
import cst_ui as ui

app = ui.App(route_init="/keyboard", on_Keyboard=True)


@app.page(route="/keyboard", title="Use Keyboard")
def keyboard_page(data: ui.DataAdmin):
    page = data.page
    on_keyboard: ui.KeyboardAdmin
    on_keyboard = data.on_keyboard_event

    use_keyboard = ft.Column()

    def show_event():
        use_keyboard.controls.append(ft.Text(on_keyboard.test()))
        page.update()

    # Add function to be executed by pressing the keyboard.
    on_keyboard.add_control(show_event)

    return ft.View(
        controls=[ft.Text("Use Keyboard", size=30), use_keyboard],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


app.run()
