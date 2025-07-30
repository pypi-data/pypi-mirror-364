import cst_ui as ui
import flet as ft

app = ui.App()


@app.page(route='/')
def test(data: ui.DataAdmin):
    return ft.View(controls=[ft.Text('Hello World!')])


app.run()
