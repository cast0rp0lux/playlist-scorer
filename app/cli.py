from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.core.engine import analyze_playlist
from app.core.ingestion.parser import parse_input
from app.core.output.card import render_curatorial_card


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a deterministic playlist audit.")
    parser.add_argument("--file", type=Path, help="Text or JSON playlist input.")
    parser.add_argument("--text", help="Inline playlist text.")
    parser.add_argument("--name", default="Untitled Playlist")
    parser.add_argument("--pipeline", default="scene")
    parser.add_argument("--scene", default=None)
    parser.add_argument("--genre", default=None)
    parser.add_argument("--era", default=None)
    parser.add_argument("--json", action="store_true", help="Print JSON instead of the curatorial card.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.file:
        raw = args.file.read_text(encoding="utf-8")
    elif args.text:
        raw = args.text
    else:
        raise SystemExit("Provide --file or --text.")

    request = parse_input(
        raw,
        playlist_name=args.name,
        pipeline=args.pipeline,
        target_scene=args.scene,
        target_genre=args.genre,
        target_era=args.era,
    )
    result = analyze_playlist(request)
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_curatorial_card(result))


if __name__ == "__main__":
    main()
