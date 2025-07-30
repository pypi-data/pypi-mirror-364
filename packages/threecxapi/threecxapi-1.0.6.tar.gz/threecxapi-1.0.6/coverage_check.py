import re
import yaml
from enum import Enum, auto
from collections import defaultdict
from pathlib import Path

# This is meant to check what endpoint actions are currently implemented in resources


class status(Enum):
    implemented = auto()
    not_implemented = auto()


# Helper function to convert camelCase or PascalCase to snake_case
def to_snake_case(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


# Function to parse the swagger file and extract operationIds
def parse_swagger(swagger_path: str) -> dict:
    with open(swagger_path, "r") as file:
        swagger_data = yaml.safe_load(file)

    paths = swagger_data.get("paths", {})
    operations = {}

    for endpoint, actions in paths.items():
        for method, details in actions.items():
            if method not in ["get", "post", "put", "delete", "patch"]:
                continue
            operation_id = details.get("operationId")
            if operation_id:
                operations[operation_id] = {
                    "method": method,
                    "endpoint": endpoint,
                }

    return operations


# Function to search for methods in APIResource classes
def check_implementation(operations: dict, resources_path: str):
    results = defaultdict(lambda: defaultdict(list))

    # Helper to extract the group key from the path
    def get_endpoint_key(path):
        return re.split(r"[/(]", path.lstrip("/"), maxsplit=1)[0]

    # Iterate through all resource files
    all_content = ""
    content = []

    for resource_file in Path(resources_path).glob("*.py"):
        with open(resource_file, "r") as file:
            content.append(file.read())
    all_content = str.join(" ", content)

    for operation_id in list(operations.keys()):
        snake_case_method = to_snake_case(operation_id)
        endpoint_key = get_endpoint_key(operations[operation_id]["endpoint"])
        implementation_status = status.not_implemented
        if re.search(rf"def {re.escape(snake_case_method)}\(.*?\).*?:", all_content):
            implementation_status = status.implemented
        results[endpoint_key][implementation_status].append(operation_id)

    return results


# Main execution
if __name__ == "__main__":
    swagger_file_path = "swagger.yaml"  # Update with the correct path to your swagger file
    api_resources_path = "threecxapi/resources"  # Update with the correct path to your APIResource classes

    operations = parse_swagger(swagger_file_path)
    results = check_implementation(operations, api_resources_path)

    for endpoint, methods in results.items():
        print(f"\nEndpoint: {endpoint}")
        print("Implemented Methods:")
        for implemented in methods[status.implemented]:
            print(f"- {implemented}")
        print("\nNot Implemented Methods:")
        for not_implemented in methods[status.not_implemented]:
            print(f"- {not_implemented}")
