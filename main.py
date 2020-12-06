import logging
import subprocess

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

logger = logging.getLogger(__name__)


class APTy(Extension):

    def __init__(self):
        super(APTy, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def search_package(self, query_package):
        results = []
        terminal_app = self.preferences.get("apty_terminal_app")
        n_results = self.preferences.get("apty_n_results")

        data = subprocess.Popen(["apt-cache", "search", str(query_package)], stdout=subprocess.PIPE)
        query_results = str(data.communicate()).replace("(b\"", "").replace("(b'", "").replace("\\n', None)", "")

        packages = query_results.split("\\n")
        for i in range(int(n_results)):
            package = packages[i]
            package_name = package.split(" - ")[0]
            package_description = package.split(" - ")[1]
            results.append(
                ExtensionResultItem(
                    icon="images/icon.png",
                    name=package_name,
                    description=package_description,
                    on_enter=RunScriptAction('%s sudo apt install %s' % (terminal_app, package_name), []),
                    on_alt_enter=CopyToClipboardAction(package_name)
                )
            )

        return results


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []
        text = event.get_argument() or "Start typing..."
        return RenderResultListAction(extension.search_package(text))


if __name__ == '__main__':
    APTy().run()
