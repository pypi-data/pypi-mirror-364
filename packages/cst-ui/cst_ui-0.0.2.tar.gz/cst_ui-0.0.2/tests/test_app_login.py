import flet as ft
import cst_ui as ui

app = ui.App(route_init="/login", route_login="/login")

db = []  # Database


@app.login
def login_x(data: ui.DataAdmin):
    username = data.page.client_storage.get("login")

    """ We check if a value exists with the key login """
    if username is not None and username in db:
        """We verify if the username that is stored in the browser
        is in the simulated database."""
        return True

    return False


@app.page(route="/dashboard", title="Dashboard", protected_route=True)
def dashboard_page(data: ui.DataAdmin):
    return ft.View(
        controls=[
            ft.Text("Dash", size=30),
            # We delete the key that we have previously registered
            ft.ElevatedButton("Logaut", on_click=data.logout("login")),
            ft.ElevatedButton("Home", on_click=data.go("/login")),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


@app.page(route="/login", title="Login")
def login_page(data: ui.DataAdmin):
    # create login stored user
    username = ft.TextField(label="Username")

    def store_login(e):
        db.append(username.value)  # We add to the simulated database

        """First the values must be stored in the browser, then in the login
        decorator the value must be retrieved through the key used and then
        validations must be used."""
        data.login(key="login", value=username.value, next_route="/dashboard")

    return ft.View(
        controls=[
            ft.Text("login", size=30),
            username,
            ft.ElevatedButton("store login in browser", on_click=store_login),
            ft.ElevatedButton("go Dasboard", on_click=data.go("/dashboard")),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


app.run()
