import flet as ft
from .data_admin import DataAdmin


def page_404_common(data: DataAdmin) -> ft.View:
    return ft.View(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("404", size=90),
                        ft.Text("url not found!"),
                        ft.FilledButton(
                            "go to Home",
                            width=200,
                            height=40,
                            on_click=data.go(data.route_init),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.RED_900,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=ft.Colors.BLACK12,
                padding=20,
                border_radius=10,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
