"""Cherry Servers API Python facade."""

from __future__ import annotations

from cherryservers_sdk_python import (
    _client,
    backup_storages,
    block_storages,
    images,
    ips,
    plans,
    projects,
    regions,
    servers,
    sshkeys,
    teams,
    users,
)


class CherryApiFacade:
    """Cherry Servers API Python facade.

    This is the preferred way of managing Cherry Servers resources with the SDK.
    For Cherry Servers API reference, see https://api.cherryservers.com/doc/.

    Attributes:
        users (users.UserClient): Manage user resources.
        sshkeys (sshkeys.SSHKeyClient): Manage SSH key resources.
        projects (projects.ProjectClient): Manage project resources.
        regions (regions.RegionClient): Manage region resources.
        ips (ips.IPClient): Manage IP resources.
        teams (teams.TeamClient): Manage team resources.
        plans (plans.PlanClient): Manage plan resources.
        images (images.ImageClient): Manage image resources.
        servers (servers.ServerClient): Manage server resources.
        block_storages (block_storages.BlockStorageClient): Manage EBS resources.
        backup_storages (backup_storages.BackupStorageClient):
         Manage backup storage resources.

    """

    def __init__(
        self, token: str, user_agent_prefix: str = "", request_timeout: int = 120
    ) -> None:
        """Create a new :class:`CherryApiFacade` instance.

        :param str token: Cherry Servers API token.
            Can be created at https://portal.cherryservers.com/settings/api-keys.
        :param str user_agent_prefix:
            User-Agent prefix that will be added to the header. Empty by default.
        :param int request_timeout: Default timeout for API requests, in seconds.

        Example:
            .. code-block:: python

                # Instantiate the facade.
                token = environ["CHERRY_AUTH_TOKEN"]
                facade = cherryservers_sdk_python.facade.CherryApiFacade(token)

                # Order a VPS.

                creation_req = (cherryservers_sdk_python.servers.
                CreationRequest(region="LT-Siauliai", plan="B1-1-1gb-20s-shared"))
                server = facade.servers.create(creation_req, project_id=217727)

        """
        self._api_client = _client.CherryApiClient(
            token=token, user_agent_prefix=user_agent_prefix
        )

        self.users = users.UserClient(self._api_client, request_timeout)

        self.sshkeys = sshkeys.SSHKeyClient(self._api_client, request_timeout)

        self.projects = projects.ProjectClient(self._api_client, request_timeout)

        self.regions = regions.RegionClient(self._api_client, request_timeout)

        self.ips = ips.IPClient(self._api_client, request_timeout)

        self.teams = teams.TeamClient(self._api_client, request_timeout)

        self.plans = plans.PlanClient(self._api_client, request_timeout)

        self.images = images.ImageClient(self._api_client, request_timeout)

        self.servers = servers.ServerClient(self._api_client, request_timeout)

        self.block_storages = block_storages.BlockStorageClient(
            self._api_client, request_timeout
        )

        self.backup_storages = backup_storages.BackupStorageClient(
            self._api_client, request_timeout
        )
