from pathlib import Path

from nukki.core import COREML_CACHE_DIR, output_path_for, resolve_providers


def test_output_path_for_same_directory():
    assert output_path_for(Path("/tmp/photo.jpg")) == Path("/tmp/photo_배경제거.png")


def test_output_path_for_preserves_multiple_dots():
    assert output_path_for(Path("a.b.jpg")) == Path("a.b_배경제거.png")


def test_resolve_providers_default_is_cpu_only():
    assert resolve_providers(use_coreml=False) == ["CPUExecutionProvider"]


def test_resolve_providers_coreml_opt_in():
    providers = resolve_providers(use_coreml=True)
    assert providers[0][0] == "CoreMLExecutionProvider"
    assert providers[0][1]["ModelCacheDirectory"] == str(COREML_CACHE_DIR)
    assert providers[1] == "CPUExecutionProvider"
