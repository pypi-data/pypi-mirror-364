from abc import ABC
from pydantic import BaseModel, ConfigDict
from threecxapi.connection import ThreeCXApiConnection


class APIResource(BaseModel, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    endpoint: str
    api: ThreeCXApiConnection

    def get_endpoint(self, resource_id: int | None = None, action: str | None = None) -> str:
        """
        Returns the appropriate endpoint for resource or a specific resource.

        Args:
            resource_id (Optional[int]): The ID of the resource, if provided.
            If None, returns the endpoint without id specified.
            uri
        Returns:
            str: The formatted endpoint string.
        """
        if resource_id:
            endpoint = f"{self.endpoint}({resource_id})"
        else:
            endpoint = self.endpoint

        if action:
            endpoint += f"/{action}"

        return endpoint
