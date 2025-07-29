from typing import Any


def pretty(
    obj: Any,
    max_str_length: int = 50,
    max_list_items: int = 10,
    max_dict_items: int = 20,
    indent: int = 2,
    current_indent: int = 0,
    visited: set[int] | None = None,
) -> str:
    """
    Convert any nested object to a pretty-printed string representation.

    Long strings and lists are truncated for better readability.
    Recursively processes all fields without modifying the original object.

    Args:
        obj: The object to pretty print
        max_str_length: Maximum length for string values before truncation
        max_list_items: Maximum number of list items to show
        max_dict_items: Maximum number of dict items to show
        indent: Number of spaces for each indentation level
        current_indent: Current indentation level (used internally)
        visited: Set of object ids to detect circular references (used internally)

    Returns:
        A pretty-printed string representation of the object
    """
    if visited is None:
        visited = set()

    # Handle None
    if obj is None:
        return "None"

    # Handle basic types
    if isinstance(obj, (int, float, bool)):
        return str(obj)

    # Handle strings with truncation
    if isinstance(obj, str):
        if len(obj) > max_str_length:
            truncated = obj[: max_str_length - 3] + "..."
            return repr(truncated)
        return repr(obj)

    # Handle bytes
    if isinstance(obj, bytes):
        if len(obj) > max_str_length:
            truncated_repr = repr(obj[: max_str_length // 2]) + "..."
            return truncated_repr[:-1] + "...'"
        return repr(obj)

    # Check for circular references
    obj_id = id(obj)
    if obj_id in visited:
        return f"<Circular reference to {type(obj).__name__}>"

    # Add to visited set
    visited = visited.copy()  # Create a new set for this branch
    visited.add(obj_id)

    # Handle lists and tuples
    if isinstance(obj, (list, tuple)):
        if not obj:
            return "[]" if isinstance(obj, list) else "()"

        # Create a copy to avoid modifying the original
        items = list(obj)
        truncated = False
        if len(items) > max_list_items:
            items = items[:max_list_items]
            truncated = True

        # Process each item
        processed_items = []
        for item in items:
            item_str = pretty(item, max_str_length, max_list_items, max_dict_items, indent, current_indent + indent, visited)
            processed_items.append(item_str)

        # Format the output
        if all(len(item) < 40 and "\n" not in item for item in processed_items):
            # Single line if all items are short
            result = ", ".join(processed_items)
            if truncated:
                result += f", ... ({len(obj) - max_list_items} more items)"
            if isinstance(obj, list):
                return f"[{result}]"
            else:
                return f"({result})"
        else:
            # Multi-line format
            indent_str = " " * (current_indent + indent)
            result_lines = []
            result_lines.append("[" if isinstance(obj, list) else "(")
            for item_str in processed_items:
                if "\n" in item_str:
                    # Multi-line item
                    lines = item_str.split("\n")
                    result_lines.append(indent_str + lines[0])
                    for line in lines[1:]:
                        result_lines.append(indent_str + line)
                    result_lines[-1] += ","
                else:
                    result_lines.append(indent_str + item_str + ",")

            if truncated:
                result_lines.append(indent_str + f"... ({len(obj) - max_list_items} more items)")

            result_lines.append(" " * current_indent + ("]" if isinstance(obj, list) else ")"))
            return "\n".join(result_lines)

    # Handle sets
    if isinstance(obj, set):
        if not obj:
            return "set()"
        items = list(obj)[:max_list_items]
        processed_items = []
        for item in items:
            item_str = pretty(item, max_str_length, max_list_items, max_dict_items, indent, current_indent + indent, visited)
            processed_items.append(item_str)

        result = "{" + ", ".join(processed_items)
        if len(obj) > max_list_items:
            result += f", ... ({len(obj) - max_list_items} more items)"
        result += "}"
        return result

    # Handle dictionaries
    if isinstance(obj, dict):
        if not obj:
            return "{}"

        items = list(obj.items())[:max_dict_items]
        truncated = len(obj) > max_dict_items

        # Process each key-value pair
        processed_items = []
        for key, value in items:
            key_str = pretty(key, max_str_length, max_list_items, max_dict_items, indent, current_indent + indent, visited)
            value_str = pretty(value, max_str_length, max_list_items, max_dict_items, indent, current_indent + indent, visited)
            processed_items.append((key_str, value_str))

        # Check if we can format on a single line
        if not truncated and all(len(k) + len(v) < 60 and "\n" not in k and "\n" not in v for k, v in processed_items):
            result = ", ".join(f"{k}: {v}" for k, v in processed_items)
            return f"{{{result}}}"

        # Multi-line format
        indent_str = " " * (current_indent + indent)
        result_lines = ["{"]
        for key_str, value_str in processed_items:
            if "\n" in value_str:
                # Multi-line value
                result_lines.append(f"{indent_str}{key_str}: {value_str.split(chr(10))[0]}")
                for line in value_str.split("\n")[1:]:
                    result_lines.append(indent_str + line)
                result_lines[-1] += ","
            else:
                result_lines.append(f"{indent_str}{key_str}: {value_str},")

        if truncated:
            result_lines.append(f"{indent_str}... ({len(obj) - max_dict_items} more items)")

        result_lines.append(" " * current_indent + "}")
        return "\n".join(result_lines)

    # Handle objects with __dict__
    if hasattr(obj, "__dict__"):
        class_name = type(obj).__name__
        obj_dict = vars(obj).copy()  # Create a copy to avoid modifying

        if not obj_dict:
            return f"<{class_name}()>"

        # Pretty print the object's attributes
        dict_str = pretty(obj_dict, max_str_length, max_list_items, max_dict_items, indent, current_indent, visited)

        if "\n" in dict_str:
            # Multi-line format
            return f"<{class_name}(\n{dict_str[1:-1]}\n{' ' * current_indent})>"
        else:
            # Single line format
            return f"<{class_name}({dict_str[1:-1]})>"

    # Handle objects with __slots__
    if hasattr(obj, "__slots__"):
        class_name = type(obj).__name__
        attrs = {}
        for slot in obj.__slots__:
            if hasattr(obj, slot):
                attrs[slot] = getattr(obj, slot)

        dict_str = pretty(attrs, max_str_length, max_list_items, max_dict_items, indent, current_indent, visited)

        if "\n" in dict_str:
            return f"<{class_name}(\n{dict_str[1:-1]}\n{' ' * current_indent})>"
        else:
            return f"<{class_name}({dict_str[1:-1]})>"

    # Fallback for other types
    try:
        return repr(obj)
    except:
        return f"<{type(obj).__name__} object>"


# Example usage and tests
if __name__ == "__main__":
    # Test with various data structures
    test_data = {
        "string": "This is a very long string that should be truncated for better readability in logs",
        "number": 42,
        "float": 3.14159,
        "boolean": True,
        "none": None,
        "short_list": [1, 2, 3],
        "long_list": list(range(100)),
        "nested": {"level1": {"level2": {"data": "nested value", "array": [1, 2, 3, 4, 5]}}},
        "mixed_list": ["string", 123, {"key": "value"}, [1, 2, 3], "another string that is quite long and should be truncated"],
    }

    print("Pretty printed output:")
    print(pretty(test_data))

    # Test with custom object
    class CustomObject:
        def __init__(self):
            self.name = "Test Object"
            self.data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            self.metadata = {"created": "2025-01-17", "author": "System", "tags": ["important", "test", "debug", "logging", "pretty-print"]}

    print("\nCustom object:")
    print(pretty(CustomObject()))

    # Test circular reference
    circular_dict: dict[str, Any] = {"a": 1}
    circular_dict["self"] = circular_dict

    print("\nCircular reference:")
    print(pretty(circular_dict))
