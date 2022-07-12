from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
import src.myanimelist as mal


class MyAnimeListExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        search_query = event.get_argument()
        api_key = extension.preferences["api_key"]

        if not search_query or not api_key:
            return

        if len(search_query) < 3:
            result = [
                ExtensionResultItem(
                    icon="images/icon.png",
                    name="Search query must be at least 3 characters long",
                    on_enter=HideWindowAction(),
                )
            ]

            return RenderResultListAction(result)

        search_results = []

        keyword = event.get_keyword()

        if keyword == extension.preferences["mal_kw_anime"]:
            search_results = mal.search(search_query, extension.preferences, "anime")
        elif keyword == extension.preferences["mal_kw_manga"]:
            search_results = mal.search(search_query, extension.preferences, "manga")
        elif keyword == extension.preferences["mal_kw"]:
            search_results = mal.search(search_query, extension.preferences, "all")

        return RenderResultListAction(search_results)


if __name__ == "__main__":
    MyAnimeListExtension().run()
