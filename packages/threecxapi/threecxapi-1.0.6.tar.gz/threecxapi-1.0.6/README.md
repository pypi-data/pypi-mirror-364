# 3CX API Python Module
## Description
This is a python wrapper for the 3CX API. It is designed to make it easier to interact with the 3CX API. It is a work in progress and is not yet feature complete. It is designed to be used with the official 3CX v20 API.

> :warning: Notice
> This package is not affiliated with 3CX. It is an unofficial package that is designed to make it easier to interact with the 3CX API.

## 3CX API Compatibility
The 3CX API can change at any time. They do provide a swagger file. The following table works to show compatibility between this package and the 3CX and swagger reported versions.
| Package Version | 3CX Version| OpenAPI Version |
|-----------------|------------|-----------------|
| 1.0.6           | Version 20.0 Update 6 + | 3.0.4 |
| < 1.0.6         | < Version 20.0 Update 6 | 3.0.0 |

## Supported Endpoints
Objects are created for almost every endpoint, response, exception, etc from the swagger provided by 3CX. The following endpoints are fully implemented into a resource that makes it easier to perform actions on them. Other endpoints can be accessed but must be done so manually with the `ThreeCXApiConnection` object.

__Supported Endpoints:__
- Users
- Groups
- Trunks
- Peers

Feel free to read the provided swagger.yaml or pull your own swagger from your own 3CX installation to see what is available.

## Installation
```bash
python3 -m pip install threecxapi
```

## Example Usage
### Connection
```python
from threecxapi.connection import ThreeCXApiConnection

# Build Connection
api_connection = ThreeCXApiConnection(server_url=app_config.server_url)
api_connection.authenticate(
    username="username",
    password="password",
)
```
### Users
```python
from threecxapi.resources.users import UsersResource, ListUserParameters
from threecxapi.resources.exceptions.users_exceptions import UserListError

# Get Users
users_resource = UsersResource(api=api_connection)

try:
    user_collection_response = self.users_resource.list_user(
        params=ListUserParameters(
            expand="Groups($expand=Rights,GroupRights),ForwardingProfiles,ForwardingExceptions,Phones,Greetings"
        )
    )
    users = user_collection_response.users
except UserListError as e:
    print(e)
```

### Direct calls to API
```python

# Import an object from here:
# from threecxapi.components.schemas.pbx import MyObject

response = api_connection.get(
    endpoint="SomeEndpoint/123",
)

api_connection.patch(
    endpoint="SomeEndpoint/123",
    data=MyObject.to_dict(),
)

api_connection.delete(
    endpoint="SomeEndpoint/123",
)
```
### Type Conversions
```python
# All objects use pydantic BaseModel so you can use TypeAdapter to convert responses to the appropriate objects like so:

from pydantic import TypeAdapter
from threecxapi.components.schemas.pbx import MyObject

response = api_connection.get(
    endpoint="SomeEndpoint/123",
)
TypeAdapter(MyObject).validate_python(response.json())

# Note that List endpoints will return a CollectionResponse found in from threecxapi.components.responses.pbx

```