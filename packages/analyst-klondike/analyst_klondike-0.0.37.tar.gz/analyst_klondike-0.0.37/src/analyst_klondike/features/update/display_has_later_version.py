from dataclasses import dataclass
import httpx
import analyst_klondike
from analyst_klondike.features.message_box.actions import DisplayMessageBoxAction
from analyst_klondike.state.app_dispatch import app_dispatch


async def _get_latest_app_version() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://pypi.org/pypi/analyst-klondike/json', timeout=5000)
        response.raise_for_status()
        data = response.json()
        latest_version = data['info']['version']
        return latest_version


@dataclass
class IsOutdatedResult:
    current_version: str
    latest_version: str
    is_outdated: bool


async def _is_outdated() -> IsOutdatedResult:
    current_version = analyst_klondike.__version__
    latest_version = await _get_latest_app_version()
    is_outdated = _more(latest_version, current_version)
    return IsOutdatedResult(
        current_version=current_version,
        latest_version=latest_version,
        is_outdated=is_outdated
    )


def _more(first_v: str, next_v: str) -> bool:
    av_tuple = first_v.split(".")
    msp_tuple = next_v.split(".")
    return av_tuple > msp_tuple


def close_app() -> None:
    # pylint: disable=import-outside-toplevel
    from analyst_klondike.ui.runner_app import get_app
    app = get_app()
    app.exit(0)


async def display_message_if_outdated():
    res = await _is_outdated()
    if res.is_outdated:
        # update_package()
        app_dispatch(
            DisplayMessageBoxAction(
                message=f"Доступна новая версия {res.latest_version} " +
                "(сейчас установлена {res.current_version}). \n"
                "Обновите приложение. \n" +
                "Для этого закройте приложение и запустите команду: \n" +
                "[@click=app.copy_update_str_to_clipboard]uv tool upgrade analyst-klondike[/]",
                ok_button_callback=close_app)
        )
