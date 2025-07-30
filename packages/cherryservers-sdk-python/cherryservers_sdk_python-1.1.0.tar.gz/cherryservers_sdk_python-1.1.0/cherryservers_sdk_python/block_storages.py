"""Cherry Servers EBS resource management module."""

from __future__ import annotations

from pydantic import Field

from cherryservers_sdk_python import _base, _resource_polling, ips, regions


class BlockStorageModel(_base.ResourceModel):
    """Cherry Servers Elastic Block Storage model.

    This model is frozen by default,
    since it represents an actual Cherry Servers EBS resource state.

    Attributes:
        id (int): EBS ID.
        name (str | None): EBS name.
        href (str | None): EBS href.
        size (int): EBS size.
        allow_edit_size (bool | None): Whether size can be edited.
        unit (str | None): Size measurement unit.
        attached_to (cherryservers_sdk_python.ips.AttachedServerModel | None):
         EBS attached server data.
        vlan_id (str | None): EBS VLAN ID.
        vlan_ip (str | None): EBS VLAN IP address.
        initiator (str | None): EBS initiator.
        discovery_ip (str | None): EBS discovery IP address.
        region (cherryservers_sdk_python.regions.RegionModel | None): Region data.

    """

    id: int = Field(description="EBS ID.")
    name: str | None = Field(description="EBS name.", default=None)
    href: str | None = Field(description="EBS href.", default=None)
    size: int = Field(description="EBS size.")
    allow_edit_size: bool | None = Field(
        description="Whether size can be edited.", default=None
    )
    unit: str | None = Field(description="Size measurement unit.", default=None)
    attached_to: ips.AttachedServerModel | None = Field(
        description="EBS attached server model.", default=None
    )
    vlan_id: str | None = Field(description="EBS VLAN ID.", default=None)
    vlan_ip: str | None = Field(description="EBS VLAN IP address.", default=None)
    initiator: str | None = Field(description="EBS initiator.", default=None)
    discovery_ip: str | None = Field(
        description="EBS discovery IP address.", default=None
    )
    region: regions.RegionModel | None = Field(description="Region data.", default=None)


class CreationRequest(_base.RequestSchema):
    """Cherry Servers block storage creation request schema.

    Attributes:
        region (str):  Region slug. Required.
        size (int):  Block storage size in GB. Required.
        description (str | None):  Block storage description.

    """

    region: str = Field(description="Region slug. Required.")
    size: int = Field(description="Block storage size in GB. Required.")
    description: str | None = Field(
        description="Block storage description.", default=None
    )


class UpdateRequest(_base.RequestSchema):
    """Cherry Servers block storage update request schema.

    Attributes:
        size (int | None): Block storage size in GB. Storage size cannot be reduced.
        description (str | None): Block storage description.

    """

    size: int | None = Field(
        description="Block storage size in GB. Storage size cannot be reduced",
        default=None,
    )
    description: str | None = Field(
        description="Block storage description.", default=None
    )


class AttachRequest(_base.RequestSchema):
    """Cherry Servers block storage server attachment request schema.

    Attributes:
        attach_to (int): ID of the server, to which the storage will be attached.

    """

    attach_to: int = Field(
        description="ID of the server, to which the storage will be attached."
    )


class BlockStorageClient(_base.ResourceClient):
    """Cherry Servers block storage client.

    Manage Cherry Servers block storage resources.
    This class should typically be initialized by
    :class:`cherryservers_sdk_python.facade.CherryApiFacade`.

    Example:
        .. code-block:: python

            # Get storage by ID.
            storage = facade.block_storages.get_by_id(123456)

            # List all project storages.
            print("List of all project storages:")
            for storage in facade.block_storages.list_by_project(123456):
                print(storage.get_model())

            # Create a storage.
            creation_req = cherryservers_sdk_python.block_storages.CreationRequest(
                region="LT-Siauliai", size=1
            )
            storage = facade.block_storages.create(creation_req, project_id=123456)

            # Update storage.
            update_req = cherryservers_sdk_python.block_storages.UpdateRequest(
                description="updated", size=2
            )
            storage.update(update_req)

            # Attach storage.
            attach_req = cherryservers_sdk_python.block_storages.AttachRequest(
                attach_to=123456
            )
            storage.attach(attach_req)

            # Detach storage.
            storage.detach()

            # Delete storage.
            storage.delete()

    """

    def get_by_id(self, storage_id: int) -> BlockStorage:
        """Retrieve a block storage by ID."""
        response = self._api_client.get(
            f"storages/{storage_id}",
            None,
            self.request_timeout,
        )
        storage_model = BlockStorageModel.model_validate(response.json())
        return BlockStorage(self, storage_model)

    def list_by_project(self, project_id: int) -> list[BlockStorage]:
        """Retrieve all block storages that belong to a specified project."""
        response = self._api_client.get(
            f"projects/{project_id}/storages",
            None,
            self.request_timeout,
        )
        storages: list[BlockStorage] = []
        for value in response.json():
            storage_model = BlockStorageModel.model_validate(value)
            storages.append(BlockStorage(self, storage_model))

        return storages

    def create(
        self,
        creation_schema: CreationRequest,
        project_id: int,
    ) -> BlockStorage:
        """Create a new block storage."""
        response = self._api_client.post(
            f"projects/{project_id}/storages",
            creation_schema,
            None,
            self.request_timeout,
        )
        return self.get_by_id(response.json()["id"])

    def delete(self, storage_id: int) -> None:
        """Delete block storage."""
        self._api_client.delete(f"storages/{storage_id}", None, self.request_timeout)

    def update(
        self,
        storage_id: int,
        update_schema: UpdateRequest,
    ) -> BlockStorage:
        """Update block storage.

        WARNING: increasing storage size will change its ID!
        """
        response = self._api_client.put(
            f"storages/{storage_id}", update_schema, None, self.request_timeout
        )
        storage = BlockStorage(self, BlockStorageModel.model_validate(response.json()))
        # We need to wait for backend.
        _resource_polling.wait_for_resource_condition(
            storage, 120, lambda: storage.get_size() == update_schema.size
        )
        return self.get_by_id(response.json()["id"])

    def attach(
        self,
        storage_id: int,
        attach_schema: AttachRequest,
    ) -> BlockStorage:
        """Attach block storage to server."""
        response = self._api_client.post(
            f"storages/{storage_id}/attachments",
            attach_schema,
            None,
            self.request_timeout,
        )

        return self.get_by_id(response.json()["id"])

    def detach(self, storage_id: int) -> BlockStorage:
        """Detach block storage from server."""
        self._api_client.delete(
            f"storages/{storage_id}/attachments", None, self.request_timeout
        )

        return self.get_by_id(storage_id)


class BlockStorage(
    _base.Resource[BlockStorageClient, BlockStorageModel],
    _resource_polling.RefreshableResource,
):
    """Cherry Servers block storage resource.

    This class represents an existing Cherry Servers resource
    and should only be initialized by :class:`BlockStorageClient`.
    Additional configuration is required. Refer to
    https://docs.cherryservers.com/knowledge/elastic-block-storage-linux.
    """

    def delete(self) -> None:
        """Delete Cherry Servers block storage resource."""
        self._client.delete(self._model.id)

    def update(self, update_schema: UpdateRequest) -> None:
        """Update Cherry Servers block storage resource.

        WARNING: increasing storage size will change its ID!
        """
        updated = self._client.update(self._model.id, update_schema)
        self._model = updated.get_model()

    def attach(self, attach_schema: AttachRequest) -> None:
        """Attach Cherry Servers block storage resource to server.

        Block storage volumes can only be attached to baremetal servers.
        """
        attached = self._client.attach(self._model.id, attach_schema)
        self._model = attached.get_model()

    def detach(self) -> None:
        """Detach Cherry Servers block storage resource from server."""
        detached = self._client.detach(self._model.id)
        self._model = detached.get_model()

    def get_id(self) -> int:
        """Get resource ID."""
        return self._model.id

    def get_size(self) -> int:
        """Get block storage size."""
        return self._model.size

    def refresh(self) -> None:
        """Refresh Cherry Servers block storage resource."""
        self._model = self._client.get_by_id(self._model.id).get_model()
