import os
from pathlib import Path


def ensure_model_downloaded(model_name: str, model_dir: str) -> str:
    """
    Ensure the spaCy model is present in the specified directory and points to the model's root.
    If not found, raise a FileNotFoundError with instructions to download manually.

    Returns the full path to the model root directory.
    """
    model_root = Path(model_dir) / model_name

    # Check if the directory exists
    if not model_root.exists():
        raise FileNotFoundError(
            f"SpaCy model '{model_name}' was not found in the directory '{model_dir}'.\n"
            f"Please download and unpack the model manually in the directory: {model_root}\n"
            f"Visit https://github.com/explosion/spacy-models/releases to download."
        )

    # Validate existence of meta.json (model config file)
    meta_file = model_root / "meta.json"
    if not meta_file.exists():
        raise FileNotFoundError(
            f"The directory '{model_root}' is missing the required 'meta.json'.\n"
            f"Ensure the model is properly unpacked in: {model_dir}"
        )

    print(f"Model '{model_name}' is correctly set up at {model_root.resolve()}")
    return str(model_root)  # Return the root model path