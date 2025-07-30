import os
from typing import Any, cast

from pagerduty.rest_api_v2_client import RestApiV2Client

from daydream.plugins.base import Plugin
from daydream.plugins.mixins import McpServerMixin, tool


class PagerDutyPlugin(Plugin, McpServerMixin):
    _client: RestApiV2Client

    def init_plugin(self) -> None:
        super().init_plugin()
        api_key = self._settings.get("api_key") or os.environ.get("PAGERDUTY_API_KEY", "")
        if api_key:
            self._client = RestApiV2Client(api_key)

    @tool()
    async def get_incident_details(self, incident_id: str) -> dict[str, Any]:
        """Get a PagerDuty incident by ID, including all alert details.

        Args:
            incident_id (str): The ID of the PagerDuty incident. Typically a
            string of uppercase letters and numbers. For example "PGR0VU2",
            "PF9KMXH", or "Q2K78SNJ5U1VE1".

        Returns:
            dict: The incident JSON payload, including all alert details.
        """
        incident = cast("dict[str, Any]", self._client.rget(f"/incidents/{incident_id}"))
        incident["alerts"] = await self.get_alert_details_for_incident(incident_id)
        return incident

    @tool()
    async def get_alert_details_for_incident(self, incident_id: str) -> list[dict[str, Any]]:
        """Get the details of the alert(s) for a PagerDuty incident.

        Args:
            incident_id (str): The ID of the PagerDuty incident. Typically a
            string of uppercase letters and numbers. For example "PGR0VU2",
            "PF9KMXH", or "Q2K78SNJ5U1VE1".

        Returns:
            list[dict]: The list of alert details.
        """
        return cast("list[dict[str, Any]]", self._client.rget(f"/incidents/{incident_id}/alerts"))

    @tool()
    async def post_status_update(self, incident_id: str, message: str) -> None:
        """Post a status update to a PagerDuty incident

        Args:
            incident_id (str): The PagerDuty ID of the incident
            message (str): The message to post
        """
        self._client.rpost(
            f"/incidents/{incident_id}/status_updates",
            json={
                "message": message,
            },
        )
