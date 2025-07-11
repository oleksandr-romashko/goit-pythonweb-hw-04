from pathlib import Path


def validate_form_data(data: dict) -> dict:
    """Validates form values"""
    username = data.get("username", "").strip()
    message = data.get("message", "").strip()

    # Empty values guard
    # At least one field must be filled; both empty makes no sense.
    # TODO: Add separate validations for username and message
    # ? Technical requirements for values validation were not specified
    if not username and not message:
        raise ValueError("Missing form fields values. Form can't be empty.")

    return {"username": username, "message": message}


def validate_is_safe_path(base_path: Path, target_path: Path) -> bool:
    """Validates if target path is safe to prevent Path Traversal attack"""
    return str(target_path).startswith(str(base_path))
