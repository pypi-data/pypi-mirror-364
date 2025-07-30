from typing import Any, Dict


def flatten_dict_by_keys(
    dict_: Dict[str, Any], cat_key: str = "/", level: int = 1
) -> Dict[str, Any]:
    """
    Flattens a nested dictionary using a specified key separator and maximum depth.

    Args:
        dict_ (Dict[str, Any]): The dictionary to be flattened.
        cat_key (str, optional): The key separator used to concatenate nested dictionary keys.
            Defaults to "/".
        level (int, optional): The maximum depth to which the dictionary should be flattened.
            Defaults to 1.

    Returns:
        Dict[str, Any]: The flattened dictionary.
    """
    flat_dict: Dict[str, Any] = {}
    for key, value in dict_.items():
        if isinstance(value, dict) and level > 0:
            flat_dict.update(
                {
                    f"{key}{cat_key}{k}": v
                    for k, v in flatten_dict_by_keys(value, cat_key, level - 1).items()
                }
            )
        else:
            flat_dict[key] = value
    return flat_dict
