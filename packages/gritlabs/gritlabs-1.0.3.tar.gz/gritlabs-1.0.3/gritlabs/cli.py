from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import importlib.resources as pkg_resources
except ImportError:  # Python < 3.9
    import importlib_resources as pkg_resources

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9
    from backports.zoneinfo import ZoneInfo


DEFAULT_TZ = "America/New_York"

# Configuration file names
NCC_FILE = "non-conforming-commits.xml"
INACTIVE_FILE = "inactive-prompts.xml"


def generate_trace_id(tz_name: str) -> str:
    """Return a Trace ID formatted as YYYYMMDDTHHMMSS±HHMM."""
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)
    return now.strftime("%Y%m%dT%H%M%S%z")


def _load_template_types() -> set[str]:
    """Return the allowed template type IDs from ``template-types.xml``."""
    with pkg_resources.files("gritlabs").joinpath("data/template-types.xml").open(
        "rb"
    ) as f:
        tree = ET.parse(f)
    return {elem.attrib["id"] for elem in tree.iterfind(".//type")}


def generate_template(template_type: str, output: str | None = None) -> Path:
    """Generate a prompt file from ``templates/<type>-template.md``."""
    allowed = _load_template_types()
    if template_type not in allowed:
        raise ValueError(f"Unknown template type: {template_type}")

    template_path = pkg_resources.files("gritlabs").joinpath(
        "templates",
        f"{template_type}-template.md",
    )
    if not template_path.is_file():
        raise FileNotFoundError(str(template_path))

    trace_id = generate_trace_id(DEFAULT_TZ)
    content = template_path.read_text()
    content = content.replace("YYYYMMDDTHHMMSS±HHMM", trace_id)
    content = re.sub(
        r"<gsl-template-guide>.*?</gsl-template-guide>\n?", "", content, flags=re.S
    )

    if output:
        dest = Path(output)
    else:
        dest = (
            Path("prompts")
            / trace_id[:4]
            / trace_id[4:6]
            / trace_id[6:8]
            / f"{trace_id}.md"
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content)
    return dest


def _ensure_user_xml(name: str) -> Path:
    """Return path to user XML file, creating from packaged template if missing."""
    path = Path(name)
    if not path.is_file():
        data_path = pkg_resources.files("gritlabs").joinpath(f"data/{name}")
        path.write_text(data_path.read_text())
    return path


def _load_xml(path: Path) -> ET.ElementTree:
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    return ET.parse(path, parser=parser)


def _cmd_ncc_add(args: argparse.Namespace) -> None:
    file_path = _ensure_user_xml(NCC_FILE)
    tree = _load_xml(file_path)
    root = tree.getroot()
    elem = ET.Element(
        "commit",
        {
            "hash": args.hash,
            **({"author": args.author} if args.author else {}),
            **({"date": args.date} if args.date else {}),
            "reason": args.reason,
        },
    )
    root.append(elem)
    tree.write(file_path, encoding="unicode")


def _cmd_ncc_list(args: argparse.Namespace) -> None:
    file_path = _ensure_user_xml(NCC_FILE)
    tree = _load_xml(file_path)
    for elem in tree.getroot().iterfind("commit"):
        author = f" {elem.get('author')}" if elem.get("author") else ""
        date = f" {elem.get('date')}" if elem.get("date") else ""
        print(f"{elem.get('hash')}{author}{date} {elem.get('reason')}")


def _cmd_ncc_remove(args: argparse.Namespace) -> None:
    file_path = _ensure_user_xml(NCC_FILE)
    tree = _load_xml(file_path)
    root = tree.getroot()
    removed = False
    for elem in list(root.iterfind("commit")):
        if elem.get("hash") == args.hash:
            root.remove(elem)
            removed = True
    if not removed:
        raise ValueError(f"Hash not found: {args.hash}")
    tree.write(file_path, encoding="unicode")


def _cmd_inactive_add(args: argparse.Namespace) -> None:
    file_path = _ensure_user_xml(INACTIVE_FILE)
    tree = _load_xml(file_path)
    root = tree.getroot()
    elem = ET.Element("prompt", {"trace_id": args.trace_id, "reason": args.reason})
    root.append(elem)
    tree.write(file_path, encoding="unicode")


def _cmd_inactive_list(args: argparse.Namespace) -> None:
    file_path = _ensure_user_xml(INACTIVE_FILE)
    tree = _load_xml(file_path)
    for elem in tree.getroot().iterfind("prompt"):
        print(f"{elem.get('trace_id')} {elem.get('reason')}")


def _cmd_inactive_remove(args: argparse.Namespace) -> None:
    file_path = _ensure_user_xml(INACTIVE_FILE)
    tree = _load_xml(file_path)
    root = tree.getroot()
    removed = False
    for elem in list(root.iterfind("prompt")):
        if elem.get("trace_id") == args.trace_id:
            root.remove(elem)
            removed = True
    if not removed:
        raise ValueError(f"Trace ID not found: {args.trace_id}")
    tree.write(file_path, encoding="unicode")


def _cmd_template_generate(args: argparse.Namespace) -> None:
    path = generate_template(args.type, args.output)
    print(str(path))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gritlabs")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("generate")
    gen_sub = gen_parser.add_subparsers(dest="generate_command", required=True)

    trace_parser = gen_sub.add_parser("trace_id", help="Generate a Trace ID")
    trace_parser.add_argument(
        "-t",
        "--timezone",
        default=DEFAULT_TZ,
        help=f"IANA timezone name (default: {DEFAULT_TZ})",
    )
    trace_parser.set_defaults(func=lambda args: print(generate_trace_id(args.timezone)))

    template_parser = subparsers.add_parser("template")
    template_sub = template_parser.add_subparsers(
        dest="template_command", required=True
    )

    gen_template_parser = template_sub.add_parser(
        "generate", help="Generate a prompt from a template"
    )
    gen_template_parser.add_argument("type", help="Template type")
    gen_template_parser.add_argument(
        "-o",
        "--output",
        help="Optional output file path for the generated prompt",
    )
    gen_template_parser.set_defaults(func=_cmd_template_generate)

    ncc_parser = subparsers.add_parser("ncc", help="Manage non-conforming commits")
    ncc_sub = ncc_parser.add_subparsers(dest="ncc_cmd", required=True)

    ncc_add = ncc_sub.add_parser("add", help="Add commit hash")
    ncc_add.add_argument("hash")
    ncc_add.add_argument("-r", "--reason", required=True)
    ncc_add.add_argument("-a", "--author")
    ncc_add.add_argument("-d", "--date")
    ncc_add.set_defaults(func=_cmd_ncc_add)

    ncc_list = ncc_sub.add_parser("list", help="List commits")
    ncc_list.set_defaults(func=_cmd_ncc_list)

    ncc_remove = ncc_sub.add_parser("remove", help="Remove commit by hash")
    ncc_remove.add_argument("hash")
    ncc_remove.set_defaults(func=_cmd_ncc_remove)

    inactive_parser = subparsers.add_parser("inactive", help="Manage inactive prompts")
    inactive_sub = inactive_parser.add_subparsers(dest="inactive_cmd", required=True)

    inactive_add = inactive_sub.add_parser("add", help="Add inactive prompt")
    inactive_add.add_argument("trace_id")
    inactive_add.add_argument("-r", "--reason", required=True)
    inactive_add.set_defaults(func=_cmd_inactive_add)

    inactive_list = inactive_sub.add_parser("list", help="List inactive prompts")
    inactive_list.set_defaults(func=_cmd_inactive_list)

    inactive_remove = inactive_sub.add_parser(
        "remove", help="Remove prompt by Trace ID"
    )
    inactive_remove.add_argument("trace_id")
    inactive_remove.set_defaults(func=_cmd_inactive_remove)

    return parser


def main(argv: Optional[list[str]] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if hasattr(args, "func"):
            args.func(args)
        else:
            parser.print_help()
    except Exception as exc:  # noqa: BLE001
        parser.error(str(exc))


if __name__ == "__main__":
    main()
