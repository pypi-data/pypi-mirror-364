import yaml
import inspect
import enum
import threecxapi.components.schemas.pbx.enums as enums_module


def extract_enum_definitions(yaml_file_path: str) -> dict[str, list[str]]:
    with open(yaml_file_path, "r") as f:
        data = yaml.safe_load(f)

    schemas = data.get("components", {}).get("schemas", {})
    enum_definitions = {}

    for name, definition in schemas.items():
        enum_values = definition.get("enum")
        if enum_values:
            clean_name = name.removeprefix("Pbx.")
            enum_definitions[clean_name] = enum_values

    return enum_definitions


def get_enum_classes(module) -> dict[str, list[str]]:
    enum_classes = {}

    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, enum.Enum):
            if obj.__module__ == module.__name__:
                members = [member.value for member in obj]
                enum_classes[name] = members

    return enum_classes


if __name__ == "__main__":
    swagger_enums = extract_enum_definitions("./openapi/openapi_3.0.4.yml")
    python_enums = get_enum_classes(enums_module)

    swagger_enum_names = set(swagger_enums.keys())
    python_enum_names = set(python_enums.keys())

    missing_in_python = swagger_enum_names - python_enum_names
    extra_in_python = python_enum_names - swagger_enum_names

    print("=== Missing in Python (Code Output) ===")
    for name in sorted(missing_in_python):
        properties = swagger_enums[name]
        print(f"\nclass {name}(TcxStrEnum):")
        for property in properties:
            value = "auto()"
            # Replace special strings
            if property == "None":
                property = "NONE"
            elif property == "-INF":
                property = "NEGATIVE_INF"

            # Replace dots with double underscores
            if "." in property:
                value = repr(property)
                property = property.replace(".", "__")

            # Ensure it's a valid identifier
            if not property.isidentifier():
                property = f"_{property}"

            print(f"    {property} = {value}")
    print("\n=== Extra in Python ===")
    for name in sorted(extra_in_python):
        print(name)

print("\n=== Differences between Swagger enums and Python enums ===")
for enum_name in sorted(swagger_enum_names & python_enum_names):
    swagger_properties_raw = swagger_enums[enum_name]
    python_properties = python_enums[enum_name]  # list of enum values (strings)

    # Map Swagger enum values to property names the same way you generate them
    def map_property_name(val):
        # Handle special strings first
        if val == "None":
            val = "NONE"
        elif val == "-INF":
            val = "NEGATIVE_INF"
        elif val is False:
            val = "FALSE"
        elif val is True:
            val = "TRUE"

        # Replace dots with double underscores
        if isinstance(val, str) and "." in val:
            val = val.replace(".", "__")

        # Make valid identifier
        if isinstance(val, str) and not val.isidentifier():
            val = f"_{val}"
        return val

    swagger_properties = set(map_property_name(val) for val in swagger_properties_raw)

    enum_cls = getattr(enums_module, enum_name, None)
    if enum_cls is None:
        continue
    python_property_names = {member.name for member in enum_cls}

    # Compare
    missing_properties = swagger_properties - python_property_names
    extra_properties = python_property_names - swagger_properties

    if missing_properties or extra_properties:
        print(f"\nIn enum '{enum_name}':")
        if missing_properties:
            print("  Missing properties:")
            for prop in sorted(missing_properties):
                print(f"    {prop}")
        if extra_properties:
            print("  Extra properties:")
            for prop in sorted(extra_properties):
                print(f"    {prop}")
