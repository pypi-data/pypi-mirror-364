
try:
    from flet import AppView, Page, WebRenderer, app
except ImportError:
    raise Exception('Install "flet" the latest version available -> pip install flet --upgrade.')

from collections import deque
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from flet import View

from .data_admin import DataAdmin
from .my_types import Redirect
from .my_types import SecretKey
from .page_admin import AddPageAdmin, Middleware, PageAdmin
from .route import auto_routing, FletAppX


def page(
    route: str,
    title: str = None,
    page_clear: bool = False,
    share_data: bool = False,
    protected_route: bool = False,
    custom_params: Dict[str, Any] = None,
    middleware: Middleware = None,
):
    return App.page(route, title, page_clear, share_data, protected_route, custom_params, middleware)


class App:
    """
    we create the app object, in it you can configure:

    * `route_prefix` : The route that is different from ` /`.
    * `route_init` : The initial route to initialize the app, by default is `/`.
    * `route_login` : The route that will be redirected when the app has route protectionconfigured.
    * `on_Keyboard` : Enables the on_Keyboard event, by default it is disabled (False).
    * `on_resize` : Triggers the on_resize event, by default it is disabled (False).
    * `secret_key` : Used with `SecretKey` class of Flet easy, to configure JWT or client storage.
    * `auto_logout` : If you use JWT, you can configure it.
    * `path_views` : Configuration of the folder where are the .py files of the pages, you use the `Path` class to configure it.

    Example:
    ```python
    import flet as ft
    import flet_app as fs

    app = FletApp(
        route_prefix="/FletApp",
        route_init="/FletApp/home",
    )


    @app.view
    async def view(data: fs.DataAdmin):
        return ft.View(
            appbar=ft.AppBar(
                title=ft.Text("AppBar Example"),
                center_title=False,
                bgcolor=ft.Colors.SURFACE_VARIANT,
                actions=[
                    ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem(
                                text="🔥 Home", on_click=data.go(data.route_init)
                            ),
                        ]
                    )
                ],
            ),
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )


    @app.page("/home", title="Index - Home", page_clear=True)
    async def index_page(data: fs.DataAdmin):
        view = data.view
        view.appbar.title = ft.Text("Index - Home")
        return ft.View(
            data.route_init,
            controls=[
                ft.Text("Menú", size=40),
                ft.ElevatedButton(
                    "Go to Test",
                    on_click=data.go(f"{data.route_prefix}/test/10/user/dxs"),
                ),
            ],
            appbar=view.appbar,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )


    @app.page("/test/{id:d}/user/{name:l}", title="Test")
    def test_page(data: fs.DataAdmin, id: int, name: str):
        view = data.view
        view.appbar.title = ft.Text("test")
        return ft.View(
            "/index/test",
            controls=[
                ft.Text(f"Test {id} | {name}"),
                ft.Text(f"Test Id is: {id}"),
                ft.ElevatedButton("Go to Home", on_click=data.go(data.route_init)),
            ],
            appbar=view.appbar,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )


    # Execute the app (synchronous / asynchronous)
    app.run()
    ```
    """

    __self = None

    def __init__(
        self,
        route_prefix: str = None,
        route_init: str = "/",
        route_login: str = None,
        on_resize: bool = False,
        on_Keyboard: bool = False,
        secret_key: SecretKey = None,
        auto_logout: bool = False,
        path_views: Path = None,
    ):
        self.__route_prefix = route_prefix
        self.__route_init = route_init
        self.__route_login = route_login
        self.__on_resize = on_resize
        self.__on_Keyboard = on_Keyboard
        self.__secret_key = secret_key
        self.__auto_logout = auto_logout
        self.__config_login: Callable[[DataAdmin], View] = None
        # ----
        self.__pages = deque()
        self.__page_404: PageAdmin = None
        self.__view_data: View = None
        self.__view_config: Callable[[DataAdmin], None] = None
        self.__config_event: Callable[[DataAdmin], None] = None
        self.__middlewares: Middleware = None
        App.__self = self

        if path_views is not None:
            self.add_pages(auto_routing(path_views))

    # -------------------------------------------------------------------
    # -- initialize / Supports async

    def run(
        self,
        name="",
        host=None,
        port=0,
        view: Optional[AppView] = AppView.FLET_APP,
        assets_dir="assets",
        upload_dir=None,
        web_renderer: WebRenderer = WebRenderer.CANVAS_KIT,
        route_url_strategy="path",
        export_asgi_app: bool = False,
        fastapi: bool = False,
    ) -> Page:
        """* Execute the app. | Soporta async, fastapi y export_asgi_app."""

        def main(page: Page):
            app = FletAppX(
                page=page,
                route_prefix=self.__route_prefix,
                route_init=self.__route_init,
                route_login=self.__route_login,
                config_login=self.__config_login,
                pages=self.__pages,
                page_404=self.__page_404,
                view_data=self.__view_data,
                view_config=self.__view_config,
                config_event_handler=self.__config_event,
                on_resize=self.__on_resize,
                on_Keyboard=self.__on_Keyboard,
                secret_key=self.__secret_key,
                auto_logout=self.__auto_logout,
                middleware=self.__middlewares,
            )

            app.run()

        if fastapi:
            return main
        try:
            return app(
                target=main,
                name=name,
                host=host,
                port=port,
                view=view,
                assets_dir=assets_dir,
                upload_dir=upload_dir,
                web_renderer=web_renderer,
                route_url_strategy=route_url_strategy,
                export_asgi_app=export_asgi_app,
            )
        except RuntimeError:
            raise Exception(
                "Ifs you are using fastapi from flet, set the 'fastapi = True' parameter of the run() method."
            )

    # -- decorators --------------------------------

    def __decorator(self, value: str, data: Dict[str, Any] = None):
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(data, *args, **kwargs):
                return func(data, *args, **kwargs)

            if data:
                route = (
                    (self.__route_prefix if data.get("route") == "/" else self.__route_prefix + data.get("route"))
                    if self.__route_prefix and data.get("route")
                    else data.get("route")
                )

            if value == "page_404":
                self.__page_404 = PageAdmin(route, func, data.get("title"), data.get("page_clear"))
            elif value == "page":
                self.__pages.append(
                    PageAdmin(
                        route=route,
                        view=func,
                        title=data.get("title"),
                        clear=data.get("page_clear"),
                        share_data=data.get("share_data"),
                        protected_route=data.get("protected_route"),
                        custom_params=data.get("custom_params"),
                        middleware=data.get("middleware"),
                    )
                )
            return wrapper

        return decorator

    def add_pages(self, group_pages: List[AddPageAdmin]):
        """Add pages from other archives
        * In the list you enter objects of class `AddPageAdmin` from other .py files.

        Example:
        ```python
        app.add_pages([index, test, contador, login, task])
        ```
        """
        try:
            for page in group_pages:
                if self.__route_prefix:
                    self.__pages.extend(page._add_pages(self.__route_prefix))
                else:
                    self.__pages.extend(page._add_pages())
        except Exception as e:
            raise e

    @classmethod
    def page(
        cls,
        route: str,
        title: str = None,
        page_clear: bool = False,
        share_data: bool = False,
        protected_route: bool = False,
        custom_params: Dict[str, Any] = None,
        middleware: Middleware = None,
    ):
        """Decorator to add a new page to the app, you need the following parameters:
        * route: text string of the url, for example(`'/FletApp'`).
        * `title` : Define the title of the page. (optional).
        * clear: Removes the pages from the `page.views` list of flet. (optional)
        * `share_data` : It is a boolean value, which is useful if you want to share data between pages, in a more restricted way. (optional)
        * protected_route: Protects the route of the page, according to the configuration of the `login` decorator of the `FletApp` class. (optional)
        * custom_params: To add validation of parameters in the custom url using a list, where the key is the name of the parameter validation and the value is the custom function that must report a boolean value.
        * `middleware` : It acts as an intermediary between different software components, intercepting and processing requests and responses. They allow adding functionalities to an application in a flexible and modular way. (optional)

        -> The decorated function must receive a parameter, for example `data:fs.DataAdmin`.

        Example:
        ```python
        import flet as ft
        import flet_app as fs

        app = FletApp(
            route_prefix="/FletApp",
            route_init="/FletApp",
        )


        @app.page("/", title="FletApp")
        async def index_page(data: fs.DataAdmin):
            return ft.View(
                route="/FletApp",
                controls=[ft.Text("FletApp")],
                vertical_alignment=view.vertical_alignment,
                horizontal_alignment=view.horizontal_alignment,
            )
        ```
        """

        data = {
            "route": route,
            "title": title,
            "page_clear": page_clear,
            "share_data": share_data,
            "protected_route": protected_route,
            "custom_params": custom_params,
            "middleware": middleware,
        }
        return cls.__decorator(cls.__self, "page", data)

    def page_404(
        self,
        route: str = None,
        title: str = None,
        page_clear: bool = False,
    ):
        """Decorator to add a new custom page when not finding a route in the app, you need the following parameters :
        * route: text string of the url, for example (`'/FletApp-404'`). (optional).
        * `title` : Define the title of the page. (optional).
        * clear: remove the pages from the `page.views` list of flet. (optional)

        -> The decorated function must receive a mandatory parameter, for example: `data:fs.DataAdmin`.

        Example:
        ```python
        import flet as ft
        import flet_app as fs

        app = FletApp(
            route_prefix="/FletApp",
            route_init="/FletApp",
        )


        @app.page_404("/FletApp-404", title="Error 404", page_clear=True)
        async def page404(data: fs.DataAdmin):
            return ft.View(
                route="/error404",
                controls=[
                    ft.Text(f"Error 404", size=30),
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ```
        """
        data = {
            "route": route,
            "title": "Flet-Easy 404" if title is None else title,
            "page_clear": page_clear,
        }
        return self.__decorator("page_404", data)

    def view(self, func: Callable[[DataAdmin], View]):
        """
        Decorator to add custom controls to the application, the decorator function will return the `View` class of `FletApp`. Which will be obtained in functions with `data:fs.DataAdmin` parameter and can be added to the page view decorated with `data.view` of `FletApp` class.

        * The decorator function must receive a mandatory parameter, for example: `data:ft.DataAdmin`.
        * Add universal controls to use on more than one page in an easy way.

        Example:
        ```python
        import flet as ft
        import flet_app as fs

        app = FletApp(
            route_prefix="/FletApp",
            route_init="/FletApp",
        )


        @app.view
        async def view(data: fs.DataAdmin):
            page = data.page

            def modify_theme():
                if page.theme_mode == ft.ThemeMode.DARK:
                    page.theme_mode = ft.ThemeMode.LIGHT
                else:
                    page.theme_mode = ft.ThemeMode.DARK

            async def theme(e):
                if page.theme_mode == ft.ThemeMode.SYSTEM:
                    modify_theme()

                modify_theme()
                await page.update_async()

            async def go_home(e):
                await page.go_async("/FletApp")

            return ft.View(
                appbar=ft.AppBar(
                    title=ft.Text("AppBar Example"),
                    center_title=False,
                    bgcolor=ft.Colors.SURFACE_VARIANT,
                    actions=[
                        ft.IconButton(ft.Icons.WB_SUNNY_OUTLINED, on_click=theme),
                        ft.PopupMenuButton(
                            items=[
                                ft.PopupMenuItem(text="🔥 Home", on_click=go_home),
                            ]
                        ),
                    ],
                ),
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ```
        """
        self.__view_data = func

    def config(self, func: Callable[[DataAdmin], None]):
        """Decorator to add a custom configuration to the app:

        * The decorator function must receive a mandatory parameter, for example: `page:ft.Page`. Which can be used to make universal app configurations.
        * The decorator function does not return anything.

        Example:
        ```python
        import flet as ft
        import flet_app as fs

        app = FletApp()


        @app.config
        async def config(page: ft.Page):
            theme = ft.Theme()
            platforms = ["android", "ios", "macos", "linux", "windows"]
            for platform in platforms:  # Removing animation on route change.
                setattr(theme.page_transitions, platform, ft.PageTransitionTheme.NONE)

            theme.text_theme = ft.TextTheme()
            page.theme = theme
        ```
        """
        self.__view_config = func

    def login(self, func: Callable[[DataAdmin], bool]):
        """Decorator to add a login configuration to the app (protected_route):

        * The decorator function must receive a mandatory parameter, for example: `page:ft.Page`. Which can be used to get information and perform universal settings of the app.
        * The decorator function must `return a boolean`.

        Example:
        ```python
        import flet as ft
        import flet_app as fs

        app = FletApp()


        # Basic demo example for login test
        @app.login
        async def login_x(page: ft.Page):
            v = [False, True, False, False, True]
            value = v[random.randint(0, 4)]
            return value
        ```
        """
        self.__config_login = func

    def config_event_handler(self, func: Callable[[DataAdmin], None]):
        """Decorator to add charter event settings -> https://flet.dev/docs/controls/page#events

        Example:
        ```python
        @app.config_event_handler
        async def event_handler(page: ft.Page):
            async def on_disconnect_async(e):
                print("Disconnect test application")

            page.on_disconnect = on_disconnect_async
        ```
        """

        self.__config_event = func

    def add_routes(self, add_views: List[PageAdmin]):
        """-> Add routes without the use of decorators.

        Example:
        ```python
        app.add_routes(
            add_views=[
                fs.PageAdmin("/hi", index_page, True),
                fs.PageAdmin(
                    "/test/{id:d}/user/{name:l}", test_page, protected_route=True
                ),
                fs.PageAdmin("/counter", counter_page),
                fs.PageAdmin("/task", task_page),
                fs.PageAdmin("/login/user", login_page),
            ]
        )
        ```
        """

        assert len(add_views) != 0, "add view (add_view) in 'add_routes'."
        for page in add_views:
            if self.__route_prefix:
                page.route = self.__route_prefix + page.route

            self.__pages.append(page)

    def add_middleware(self, middleware: List[Callable[[DataAdmin], Optional[Redirect]]]):
        """The function that will act as middleware will receive as a single mandatory parameter `data : DataAdmin` and its structure or content may vary depending on the context and the specific requirements of the middleware."""
        self.__middlewares = middleware
