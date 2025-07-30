"""
FIXME: issue list:
    toga:
        - cannot maximize/mimimize window at startup.
    webui2:
        - too slow to detect window close event.
        - the launcher icon is in low resolution.
    wxpython:
        ...
    chrome_appmode:
        - when close the window, will popup a new window with blank page.
        - requires that user PC has chrome installed.
    pywebview:
        - cannot set launch icon and window icon.
        - may be crashed in older windows (caused by pythonnet, .NET etc.)
        - cannot show the window in macos when running in poetry venv.
    pyside6:
        - too heavy to use.
    kivy:
        ...
"""
import os
import sys
import typing as t


class T:
    Backend = t.Literal[
        'chrome_appmode',
        'pywebview',
        'terminal',
        'toga',
        'webbrowser',
        'webui2',
    ]
    Position = t.Tuple[int, int]
    Size = t.Tuple[int, int]


def select_backend(
    prefer: t.Optional[T.Backend] = os.getenv('PYAPP_WINDOW_BACKEND', None)
) -> t.Callable:
    if prefer:
        backend = prefer
    else:
        if sys.platform == 'linux':
            try:
                import webui
                backend = 'webui2'
            except ImportError:
                backend = 'webbrowser'
        elif sys.platform == 'win32':
            backend = 'toga'
        else:
            try:
                import toga
                backend = 'toga'
            except ImportError:
                backend = 'webui2'
    print(backend)
    del prefer
    
    return {
        'chrome_appmode': open_with_chrome_appmode,
        'pywebview'     : open_with_pywebview,
        'terminal'      : open_with_terminal,
        'toga'          : open_with_toga,
        'webbrowser'    : open_with_webbrowser,
        'webui2'        : open_with_webui2,
    }[backend]


# -----------------------------------------------------------------------------


def open_with_chrome_appmode(*_, **__):
    raise NotImplementedError


def open_with_pywebview(
    *,
    fullscreen: bool = False,
    pos: T.Position,
    size: T.Size,
    title: str,
    url: str,
    **_
) -> None:
    import webview  # pip install pywebview
    webview.create_window(
        title,
        url,
        x=pos[0],
        y=pos[1],
        width=size[0],
        height=size[1],
        fullscreen=fullscreen,
    )
    webview.start()


def open_with_terminal(
    *,
    fullscreen: bool = False,
    maximized: bool = False,
    pos: T.Position,
    size: T.Size,
    suppress_size_warning: bool = False,
    **_
) -> None:
    """
    open terminal app, the terminal app should be pre-installed.
    for windows, we prefer to open wt.exe (windows terminal).
    
    params:
        size: the `(width, height)` means `(cols, rows)`. suggested values are:
            - `(80, 24)`: for small terminal.
            - `(120, 40)`: for medium terminal.
            - `(160, 60)`: for large terminal.
    """
    assert fullscreen == maximized == False or fullscreen != maximized  # noqa
    if not suppress_size_warning:
        assert size[0] <= 500 and size[1] <= 100, (
            'the unit for terminal size is cols and rows, not pixels. '
            'it seems you are giving too large values for `size` param. '
            'if you are sure this is what you want, try again with setting '
            '`suppress_size_warning=True`.'
        )
    
    from lk_utils import run_cmd_args
    
    if sys.platform == 'win32':
        if os.path.exists(
            wt := '{}/Microsoft/WindowsApps/wt.exe'.format(
                os.environ['LocalAppData']
            )
        ):
            # https://learn.microsoft.com/en-us/windows/terminal/command-line
            # -arguments?tabs=windows#options-and-commands
            run_cmd_args(
                wt,
                '--pos', '{},{}'.format(*pos),
                '--size', '{},{}'.format(*size),
                (fullscreen and '--fullscreen' or ''),
                (maximized and '--maximized' or ''),
                verbose=True,  # TEST
            )
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError


def open_with_toga(
    *,
    appid: str = 'dev.likianta.pyapp_window',
    fullscreen: bool = False,
    icon: str = None,
    # maximized: bool = False,  # TODO
    pos: T.Position,
    # size: t.Union[T.Size, t.Literal['fullscreen', 'maximized']],
    size: T.Size,
    splash_screen: str = None,
    title: str,
    url: str,
    **_
) -> None:
    import toga
    from lk_utils import new_thread
    from toga.style.pack import CENTER, COLUMN, Pack
    from .util import wait_webpage_ready
    
    class MyApp(toga.App):
        _progress_bar: t.Optional[toga.ProgressBar]
        
        def __init__(self) -> None:
            super().__init__(formal_name=title, app_id=appid, icon=icon)
        
        # noinspection PyTypeChecker
        def startup(self) -> None:
            if splash_screen:
                img_width = round(size[0] * 0.8)
                h_padding = (size[0] - img_width) // 2
                print(size[0], img_width, h_padding, ':v')
                # view = toga.ImageView(
                #     toga.Image(splash_screen),
                #     style=Pack(
                #         alignment=CENTER,
                #         flex=1,
                #         padding_left=h_padding,
                #         padding_right=h_padding,
                #     )
                # )
                view = toga.Box(
                    children=(
                        toga.ImageView(
                            toga.Image(splash_screen),
                            style=Pack(
                                alignment=CENTER,
                                flex=1,
                                padding_left=h_padding,
                                padding_right=h_padding,
                            )
                        ),
                        # toga.ImageView(
                        #     toga.Image(xpath('loading_motion_blur_2.png')),
                        #     style=Pack(
                        #         alignment=CENTER,
                        #         # flex=1,
                        #         width=img_width,
                        #         padding_left=h_padding,
                        #         padding_right=h_padding,
                        #     )
                        # ),
                        bar := toga.ProgressBar(
                            max=None,
                            style=Pack(
                                alignment=CENTER,
                                # color='#E31B25',
                                # background_color='#E31B25',
                                padding_left=h_padding,
                                padding_right=h_padding,
                                padding_bottom=20,
                                width=img_width,
                            )
                        ),
                    ),
                    style=Pack(
                        direction=COLUMN
                    )
                )
                self._progress_bar = bar
                self._progress_bar.start()
                # TEST: if you want to test only splash screen, comment below
                #   line.
                self._wait_webpage_ready(url)
            else:
                view = toga.WebView(url=url)
                self._progress_bar = None
            self.main_window = toga.MainWindow(
                id='main', title=title, position=pos, size=size, content=view,
            )
            # if maximized:
            #     self.main_window.maximized = True
            if fullscreen:
                self.main_window.full_screen = True
            self.main_window.show()
        
        @new_thread()
        def _wait_webpage_ready(self, url: str, timeout: float = 30) -> None:
            wait_webpage_ready(url, timeout)
            
            # don't update ui in non-main thread directly, instead, toga has
            # pre-set `self.loop` for this purpose.
            # https://stackoverflow.com/a/77350586/9695911
            def _replace_view() -> None:
                self._progress_bar.stop()
                self.main_window.content = toga.WebView(url=url)
            
            self.loop.call_soon_threadsafe(_replace_view)  # noqa
    
    app = MyApp()
    app.main_loop()


def open_with_webbrowser(
    *,
    url: str,
    **_
) -> None:
    import webbrowser
    webbrowser.open_new_tab(url)


def open_with_webui2(
    *,
    icon: str = None,
    pos: T.Position,
    size: T.Size,
    title: str,
    url: str,
    **_
) -> None:
    """
    pros: webui2 is small and lightning fast.
    https://github.com/webui-dev/python-webui
    """
    from lk_utils import xpath
    from textwrap import dedent
    from webui import webui
    
    if icon:
        assert icon.endswith('.svg')
    else:
        icon = xpath('./favicon.svg')
    
    win = webui.window()
    html = dedent(
        '''
        <html>
        <head>
            <title>{title}</title>
            <link
                rel="icon"
                type="image/svg+xml"
                href="data:image/svg+xml,{svg}" />
        </head>
        <body>
            <iframe
                src="{target_url}"
                width="100%"
                height="100%"
                frameBorder="0"
            ></iframe>
        </body>
        </html>
        '''.format(
            title=title,
            # https://stackoverflow.com/a/75832198
            svg=(
                open(icon, 'r').read()
                .replace('\n', ' ')
                .replace('"', "%22")
                .replace('#', '%23')
            ),
            target_url=url,
        )
    )
    # print(html, ':v')
    win.set_position(pos[0], pos[1])
    win.set_size(size[0], size[1])
    
    print(':tv', 'start opening')
    win.show(html)  # FIXME: very slow waiting for window close event.
    # run_new_thread(win.show, (html,))
    # sleep(3)
    # while win.is_shown():
    #     sleep(1)
    print(':tv', 'show over', win.is_shown())
    
    webui.wait()  # block until all opened windows are closed.
    print('webui window closed', ':v7t')


# def open_with_wxpython(
#     *,
#     pos: T.Position,
#     size: T.Size,
#     title: str,
#     url: str,
#     **_
# ):
#     raise NotImplementedError
