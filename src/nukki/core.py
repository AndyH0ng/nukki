"""Pure helper functions with no heavy dependencies, kept separate so they can
be unit-tested without importing rembg/onnxruntime or downloading model weights.
"""

from pathlib import Path

OUTPUT_SUFFIX = "_배경제거"

# CoreML compiles BiRefNet's many subgraphs from scratch unless pointed at a
# persistent cache dir. In practice this still took 5+ minutes and several GB
# on first run regardless of MLComputeUnits, so CoreML is opt-in, not default.
COREML_CACHE_DIR = Path.home() / "Library" / "Caches" / "nukki" / "coreml"

ProviderList = list[str | tuple[str, dict[str, str]]]


def output_path_for(input_path: Path) -> Path:
    """Return the sibling output path for a given input image path.

    e.g. photo.jpg -> photo_배경제거.png
    """
    return input_path.with_name(f"{input_path.stem}{OUTPUT_SUFFIX}.png")


def resolve_providers(use_coreml: bool) -> ProviderList:
    """Return the onnxruntime execution provider priority list.

    Defaults to CPU: predictable ~10s/image, no compile step. CoreML is
    available via an explicit opt-in for whoever wants to experiment with it,
    but its first-run compile cost for BiRefNet was too large/unpredictable
    to make it the default (see README).
    """
    if not use_coreml:
        return ["CPUExecutionProvider"]
    return [
        (
            "CoreMLExecutionProvider",
            {
                "ModelFormat": "MLProgram",
                "MLComputeUnits": "CPUAndNeuralEngine",
                "ModelCacheDirectory": str(COREML_CACHE_DIR),
            },
        ),
        "CPUExecutionProvider",
    ]
