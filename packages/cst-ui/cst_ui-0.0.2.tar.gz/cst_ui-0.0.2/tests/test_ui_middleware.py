import flet as ft
import cst_ui as ui

app = ui.App(route_init="/login", route_login="/login")

db = []  # Database

# -------------------------------------------------------------------------------


# Customized middleware
def login_middleware(data: ui.DataAdmin):
    """If the path is '/login', it will return the None function,
    which will not prevent access to the page."""
    if data.route == "/login":
        return

    username = data.page.client_storage.get_async("login")
    if username is None or username not in db:
        return data.redirect("/login")


# Middleware that runs in general, i.e. every time you load a page.
app.add_middleware([login_middleware])
# -------------------------------------------------------------------------------


@app.page(route="/dashboard", title="Dashboard")
def dashboard_page(data: ui.DataAdmin):
    return ft.View(
        controls=[
            ft.Text("Dash", size=30),
            # We delete the key that we have previously registered
            ft.ElevatedButton("Logaut", on_click=data.logout("login")),
            ft.ElevatedButton("go Home", on_click=data.go("/login")),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


# -------------------------------------------------------------------------------


@app.page(route="/login", title="Login", middleware=[login_middleware])
def login_page(data: ui.DataAdmin):
    # create login stored user
    username = ft.TextField(label="Username")

    def store_login(e):
        db.append(username.value)  # We add to the simulated databas

        """First the values must be stored in the browser, then in the
        login decorator the value must be retrieved through the key used
        and then validations must be used."""
        data.login(key="login", value=username.value, next_route="/dashboard")

    return ft.View(
        controls=[
            ft.Text("login", size=30),
            username,
            ft.ElevatedButton("store login in browser", on_click=store_login),
            ft.ElevatedButton("go Dashboard", on_click=data.go("/dashboard")),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


app.run(view=ft.AppView.WEB_BROWSER)
# app.run()
