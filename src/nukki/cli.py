from __future__ import annotations

import argparse
import sys
from pathlib import Path

from nukki import __version__
from nukki.core import output_path_for, resolve_providers
from nukki.remover import BackgroundRemover

DEFAULT_MODEL = "birefnet-general"
MODEL_CHOICES = ["birefnet-general", "birefnet-portrait", "isnet-general-use", "u2net"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nukki",
        description="이미지에서 배경을 제거해 투명 PNG로 저장합니다.",
    )
    parser.add_argument("files", nargs="+", type=Path, help="배경을 제거할 이미지 파일들")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        choices=MODEL_CHOICES,
        help=f"사용할 모델 (기본값: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--coreml",
        action="store_true",
        help=(
            "CoreML 가속 사용 (실험적: 모델마다 최초 1회 컴파일에 수 분, "
            "캐시에 수 GB가 들 수 있음). 기본값은 CPU."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="실제로 사용된 onnxruntime provider 등 진행 상황을 stderr에 출력",
    )
    parser.add_argument("--version", action="version", version=f"nukki {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    providers = resolve_providers(args.coreml)
    remover = BackgroundRemover(args.model, providers, verbose=args.verbose)

    failures = 0
    for input_path in args.files:
        if not input_path.is_file():
            print(f"[nukki] 파일을 찾을 수 없음: {input_path}", file=sys.stderr)
            failures += 1
            continue
        try:
            result = remover.remove(input_path.read_bytes())
        except Exception as exc:  # noqa: BLE001 - keep processing remaining files
            print(f"[nukki] 실패: {input_path} ({exc})", file=sys.stderr)
            failures += 1
            continue

        out_path = output_path_for(input_path)
        out_path.write_bytes(result)
        print(out_path)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
