import re
from re import Pattern, compile, escape
from typing import Any, Callable, Dict, List, Optional, Tuple
from inspect import iscoroutinefunction

from flet import ControlEvent, KeyboardEvent, Page, RouteChangeEvent, View

# from parse import parse

from .data_admin import DataAdmin
from .my_types import TYPE_PATTERNS, Msg, Redirect
from .inheritance import KeyboardAdmin, ResizeAdmin
from .page_admin import Middleware, PageAdmin
from .view_404 import page_404_common


from importlib.util import module_from_spec, spec_from_file_location
from inspect import getmembers
from pathlib import Path
from .page_admin import AddPageAdmin


def auto_routing(file_dir: Path) -> List[AddPageAdmin]:
    """
    A function that automatically routes through a directory to find Python files, extract AddPageAdmin objects, and return a list of them.

    Parameters:
    - dir (str): The directory path to search for Python files.

    Returns:
    - List[AddPageAdmin]: A list of AddPageAdmin objects found in the specified directory.
    """

    pages = []
    # for file in file_dir.rglob('*.py[c]'):
    for file in file_dir.rglob('*.py'):
        if file.name != "__init__.py":
            spec = spec_from_file_location(file.stem, file)
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            for _, object_page in getmembers(module):
                if isinstance(object_page, AddPageAdmin):
                    pages.append(object_page)
    if len(pages) == 0:
        raise ValueError(
            "No instances of AddPageAdmin found. Check the assigned path of the 'path_views' parameter of the class (App)."
        )

    return pages


class FletAppX:
    __compiled_patterns_cache: Dict[str, re.Pattern[str]] = {}

    def __init__(
        self,
        page: Page,
        route_prefix: str,
        route_init: str,
        route_login: str,
        config_login: Callable[[DataAdmin], bool],
        pages: List[PageAdmin],
        page_404: PageAdmin,
        view_data: Callable[[DataAdmin], View],
        view_config: Callable[[DataAdmin], None],
        config_event_handler: Callable[[DataAdmin], None],
        on_resize: bool,
        on_Keyboard: bool,
        secret_key: str,
        auto_logout: bool,
        middleware: Middleware,
    ):
        self.__page = page
        self.__page_on_keyboard = KeyboardAdmin()
        self.__page_on_resize = ResizeAdmin(self.__page)

        self.__route_init = route_init
        self.__route_login = route_login
        self.__config_login = config_login
        self.__on_resize = on_resize
        self.__on_Keyboard = on_Keyboard
        self.__middlewares = middleware
        # ----
        self.__pages = pages
        self.__view_404 = page_404_common
        self.__page_404 = page_404
        self.__view_data = view_data
        self.__view_config = view_config
        self.__config_event = config_event_handler
        self.__page_admin: PageAdmin | None = None

        self.__data = DataAdmin(
            page=self.__page,
            route_prefix="" if route_prefix is None else route_prefix,
            route_init=self.__route_init,
            route_login=self.__route_login,
            secret_key=secret_key,
            auto_logout=auto_logout,
            page_on_keyboard=self.__page_on_keyboard,
            page_on_resize=self.__page_on_resize,
            login_async=iscoroutinefunction(self.__config_login),
            go=self._go,
        )
        self.__data.view = self.__view_data_config() if self.__view_data is not None else None
        if self.__route_login is not None:
            self.__data._create_login()

    # ----------- Supports async
    def __route_change(self, e: RouteChangeEvent):
        if self.__page_admin is None:
            if e.route == "/" and self.__route_init != "/":
                return self.__page.go(self.__route_init)

            self._go(e.route, True)
        else:
            self._view_append(e.route, self.__page_admin)
            self.__page_admin = None

    def __view_pop(self, e):
        if len(self.__data.history_routes) > 1:
            self.__data.history_routes.pop()
            self._go(self.__data.history_routes.pop())

    async def __on_keyboard(self, e: KeyboardEvent):
        self.__page_on_keyboard.call = e
        if self.__page_on_keyboard._controls():
            await self.__page_on_keyboard._run_controls()

    def __page_resize(self, e: ControlEvent):
        self.__page_on_resize.e = e

    def __add_configuration_start(self):
        """Add general settings to the pages."""
        if self.__view_config:
            if iscoroutinefunction(self.__view_config):
                self.__page.run_task(self.__view_config, self.__page).result()
            else:
                self.__view_config(self.__page)

        if self.__config_event:
            if iscoroutinefunction(self.__config_event):
                self.__page.run_task(self.__config_event, self.__data).result()
            else:
                self.__config_event(self.__data)

    def __disconnect(self, e):
        if self.__data._login_done and self.__page.web:
            self.__page.pubsub.send_others_on_topic(
                self.__page.client_ip,
                Msg("updateLoginSessions", value=self.__data._login_done),
            )

    # -- initialization

    def run(self):
        if self.__route_init != "/" and self.__page.route == "/":
            self.__page.route = self.__route_init

        """ Add custom events """
        self.__add_configuration_start()

        """ Executing charter events """
        self.__page.on_route_change = self.__route_change
        self.__page.on_view_pop = self.__view_pop
        self.__page.on_error = lambda e: print("FletAppX: Page error:", e, dir(e), e.page, e.data)
        self.__page.on_disconnect = self.__disconnect

        """ activation of charter events """
        if self.__on_resize:
            self.__page.on_resize = self.__page_resize
        if self.__on_Keyboard:
            self.__page.on_keyboard_event = self.__on_keyboard

        self._go(self.__page.route, use_reload=True)

    # ---------------------------[Route controller]-------------------------------------
    def __view_data_config(self):
        """Add the `View` configuration, to reuse on every page."""
        if iscoroutinefunction(self.__view_data):
            return self.__page.run_task(self.__view_data, self.__data).result()
        else:
            return self.__view_data(self.__data)

    def _view_append(self, route: str, page_admin: PageAdmin):
        """Add a new page and update it."""
        # 更新至 flet 0.28.2 后，无论去什么route，都会重定向到routee_init
        # self.__page.views.clear()

        if not page_admin.clear and len(self.__data.history_routes) > 0:
            self.__page.views.append(View())

        if callable(page_admin.view) and not isinstance(page_admin.view, type):
            view = (
                self.__page.run_task(page_admin.view, self.__data, **self.__data.url_params).result()
                if iscoroutinefunction(page_admin.view)
                else page_admin.view(self.__data, **self.__data.url_params)
            )
        elif isinstance(page_admin.view, type):
            view_class = page_admin.view(self.__data, **self.__data.url_params)
            view = (
                self.__page.run_task(view_class.build).result()
                if iscoroutinefunction(view_class.build)
                else view_class.build()
            )
        view.route = route
        self.__page.views.append(view)
        self.__data.history_routes.append(route)
        self.__page.update()

        # 为 class 形式的添加 did_mount
        if isinstance(page_admin.view, type):
            if hasattr(view_class, 'did_mount'):
                view_class.did_mount()

    def __reload_data_admin(
        self,
        page_admin: PageAdmin,
        url_params: Dict[str, Any] = dict(),
    ):
        """Update `data_admin` values when switching between pages."""
        self.__page.title = page_admin.title

        if not page_admin.share_data:
            self.__data.share.clear()
        if self.__on_Keyboard:
            self.__data.on_keyboard_event.clear()

        self.__data.url_params = url_params
        self.__data.route = page_admin.route

    def __execute_middleware(self, page_admin: PageAdmin, url_params: Dict[str, Any], middleware_list: Middleware):
        if middleware_list is None:
            return False

        for middleware in middleware_list:
            self.__reload_data_admin(page_admin, url_params)
            res_middleware = (
                self.__page.run_task(middleware, self.__data).result()
                if iscoroutinefunction(middleware)
                else middleware(self.__data)
            )
            if res_middleware is None:
                continue

            if isinstance(res_middleware, Redirect):
                self._go(res_middleware.route)
                return True

            if not res_middleware:
                raise Exception(
                    "Ocurrió un error en una función middleware. Usa los métodos para redirigir (data.redirect) o devolver False."
                )

    def __run_middlewares(
        self,
        route: str,
        middleware: Middleware,
        url_params: Dict[str, Any],
        page_admin: PageAdmin,
        use_route_change: bool,
        use_reload: bool,
    ):
        """Controla los middleware de la aplicación en general y en cada una de las páginas."""

        if self.__execute_middleware(page_admin, url_params, middleware):
            return True

        if self.__execute_middleware(page_admin, url_params, page_admin.middleware):
            return True

        self.__reload_data_admin(page_admin, url_params)
        if use_route_change:
            self._view_append(route, page_admin)
        else:
            if self.__page.route != route or use_reload:
                self.__page_admin = page_admin
            self.__page.go(route)

        return True

    # def __process_route(self, custom_params: Dict[str, Callable[[], bool]], path: str, route: str):
    #     if custom_params is None:
    #         route_math = parse(route, path)
    #         return [route_math, route_math]

    #     else:
    #         try:
    #             route_math = parse(route, path, custom_params)
    #             route_check = (
    #                 all(valor is not False and valor is not None for valor in dict(route_math.named).values())
    #                 if route_math
    #                 else route_math
    #             )
    #             return [route_math, route_check]

    #         except Exception as e:
    #             raise Exception(
    #                 f"The url parse has failed, check the url -> ({route}) parameters for correctness. Error-> {e}"
    #             )

    def _go(self, route: str, use_route_change: bool = False, use_reload: bool = False):
        pg_404 = True

        for page in self.__pages:
            route_math = self._verify_url(page.route, route, page.custom_params)
            if route_math is not None:
                pg_404 = False
                try:
                    if page.protected_route:
                        assert (
                            self.__route_login is not None
                        ), "Configure the route of the login page, in the Flet-Easy class in the parameter (route_login)"

                        if iscoroutinefunction(self.__config_login):
                            try:
                                auth = self.__page.run_task(self.__config_login, self.__data).result()
                            except Exception as e:
                                raise Exception(
                                    "Use async methods in the function decorated by 'login', to avoid conflicts.",
                                    e,
                                )
                        else:
                            auth = self.__config_login(self.__data)

                        if auth:
                            self.__reload_data_admin(page, route_math)

                            if use_route_change:
                                self._view_append(route, page)

                            else:
                                if self.__page.route != route or use_reload:
                                    self.__page_admin = page
                                self.__page.go(route)

                        else:
                            self._go(self.__route_login)

                        break
                    else:
                        if self.__run_middlewares(
                            route=route,
                            middleware=self.__middlewares,
                            url_params=route_math,
                            page_admin=page,
                            use_route_change=use_route_change,
                            use_reload=use_reload,
                        ):
                            break
                except Exception as e:
                    raise Exception(e)
        if pg_404:
            page = self.__page_404 or PageAdmin(route, self.__view_404, "Flet-Easy 404")

            if page.route is None:
                page.route = route

            self.__reload_data_admin(page)

            if use_route_change:
                self._view_append(page.route, page)
            else:
                if self.__page.route != route or use_reload:
                    self.__page_admin = page
                self.__page.go(page.route)

    @classmethod
    def __compile_pattern(cls, pattern_parts: list[str]) -> Pattern[str]:
        pattern_key = "/".join(pattern_parts)
        if pattern_key not in cls.__compiled_patterns_cache:
            cls.__compiled_patterns_cache[pattern_key] = compile(f"^/{pattern_key}/?$")
        return cls.__compiled_patterns_cache[pattern_key]

    @classmethod
    def _verify_url(
        cls,
        url_pattern: str,
        url: str,
        custom_types: Optional[Dict[str, Callable[[str], Optional[bool]]]] = None,
    ) -> Optional[Dict[str, Optional[bool]]]:
        combined_patterns = {
            **TYPE_PATTERNS,
            **{k: (compile(r"[^/]+"), v) for k, v in (custom_types or {}).items()},
        }

        segments: list[Tuple[str, Callable[[str], Optional[bool]]]] = []
        pattern_parts: list[str] = []
        type_patterns: list[str] = []

        for segment in url_pattern.strip("/").split("/"):
            try:
                if segment == "":
                    continue

                if segment[0] in "<{" and segment[-1] in ">}":
                    name, type_ = segment[1:-1].split(":", 1) if ":" in segment else (segment[1:-1], "str")
                    type_patterns.append(type_)
                    regex_part, parser = combined_patterns[type_]
                    pattern_parts.append(f"({regex_part.pattern})")
                    segments.append((name, parser))
                else:
                    pattern_parts.append(escape(segment))
            except KeyError as e:
                raise ValueError(f"Unrecognized data type: {e}")
        if custom_types and type_ not in custom_types:
            raise ValueError(f"A custom data type is not being used: {custom_types.keys()}")

        pattern = cls.__compile_pattern(pattern_parts)
        match = pattern.fullmatch(url)
        if not match:
            return None

        result = {name: parser(match.group(i + 1)) for i, (name, parser) in enumerate(segments)}

        return None if None in result.values() else result
