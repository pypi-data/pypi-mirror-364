import requests
from typing import List

from pydantic import TypeAdapter

from threecxapi.components.parameters import (
    ExpandParameters,
    ListParameters,
    OrderbyParameters,
    SelectParameters,
)
from threecxapi.resources.api_resource import APIResource
from threecxapi.components.schemas.pbx import Peer
from threecxapi.components.responses.pbx import PeerCollectionResponse
from threecxapi.resources.exceptions.peers_exceptions import PeerListError, PeerGetError


class ListPeerParameters(ListParameters, OrderbyParameters, SelectParameters[Peer.to_enum()], ExpandParameters): ...


class PeersResource(APIResource):
    """Provides operations to manage the collection of Peer entities."""

    def get_endpoint(self) -> str:
        return "/Peers"

    def list_peer(self, params: ListPeerParameters) -> PeerCollectionResponse:
        try:
            response = self.api.get(self.get_endpoint(), params)
            return TypeAdapter(PeerCollectionResponse).validate_python(response.json())
        except requests.HTTPError as e:
            raise PeerListError(e)

    def get_peer_by_number(self, user_number: str) -> Peer | None:
        try:
            response = self.api.get(f"{self.get_endpoint()}/Pbx.GetPeerByNumber(number='{user_number}')")
            return TypeAdapter(Peer).validate_python(response.json())
        except requests.HTTPError as e:
            raise PeerGetError(e, user_number)
