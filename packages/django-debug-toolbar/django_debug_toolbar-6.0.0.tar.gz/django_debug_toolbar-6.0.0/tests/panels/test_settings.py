from django.test import override_settings

from ..base import IntegrationTestCase


@override_settings(DEBUG=True)
class SettingsIntegrationTestCase(IntegrationTestCase):
    def test_panel_title(self):
        response = self.client.get("/regular/basic/")
        # The settings module is None due to using Django's UserSettingsHolder
        # in tests.
        self.assertContains(
            response,
            """
            <li id="djdt-SettingsPanel" class="djDebugPanelButton">
            <input type="checkbox" checked title="Disable for next and successive requests" data-cookie="djdtSettingsPanel">
            <a class="SettingsPanel" href="#" title="Settings from None">Settings</a>
            </li>
            """,
            html=True,
        )
        self.assertContains(
            response,
            """
            <div id="SettingsPanel" class="djdt-panelContent djdt-hidden">
            <div class="djDebugPanelTitle">
            <h3>Settings from None</h3>
            <button type="button" class="djDebugClose">×</button>
            </div>
            <div class="djDebugPanelContent">
            <div class="djdt-loader"></div>
            <div class="djdt-scroll"></div>
            </div>
            </div>
            """,
            html=True,
        )
