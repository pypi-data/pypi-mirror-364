VERSION = '0.0.2'

from .basic.app import (
    App,
    page,
    DataAdmin,
    AddPageAdmin,
    PageAdmin,
    Redirect,
    EncryptAlgorithm,
    PemKey,
    SecretKey,
    encode_HS256,
    encode_RS256,
    Job,
    KeyboardAdmin,
    ResizeAdmin,
    ResponsiveControl,
    AppKey,
    decode,
    decode_async,
    auto_routing,
)


def main() -> None:
    print("Hello from cst_ui!")


if __name__ == "__main__":
    main()
