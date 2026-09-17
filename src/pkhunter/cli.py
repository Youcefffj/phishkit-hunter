"""Command-line interface for PhishKit-Hunter."""

from __future__ import annotations

import argparse
import logging
import sys
from typing import List, Optional

from . import __version__
from .scanner import DEFAULT_USER_AGENT, ScanConfig, run_scan
from .utils import clean_url_list


def _read_lines(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pkhunter",
        description="Defensive scanner for exposed phishing-kit exfiltration files.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="probe targets for phishing-kit artifacts")
    scan.add_argument("--targets", default="data/targets.txt",
                      help="file of base URLs, one per line (default: data/targets.txt)")
    scan.add_argument("--wordlist", default="data/wordlist.txt",
                      help="artifact paths to probe (default: data/wordlist.txt)")
    scan.add_argument("--out", default="captures/",
                      help="directory for downloaded artifacts (default: captures/)")
    scan.add_argument("--log", default="captures/hits.log",
                      help="hit log: date/URL/filename (default: captures/hits.log)")
    scan.add_argument("--sentinel", default="__pkhunter_probe__.html",
                      help="decoy path for the catch-all guard (should not exist on a real host)")
    scan.add_argument("--parent", action="store_true",
                      help="also probe each parent directory of every URL")
    scan.add_argument("--timeout", type=float, default=15.0,
                      help="per-request timeout in seconds (default: 15)")
    scan.add_argument("--workers", type=int, default=20,
                      help="concurrent requests (default: 20)")
    scan.add_argument("--retries", type=int, default=2,
                      help="retries per request (default: 2)")
    scan.add_argument("--user-agent", default=DEFAULT_USER_AGENT,
                      help="User-Agent header sent with each request")
    scan.add_argument("-v", "--verbose", action="store_true", help="debug logging")

    prepare = sub.add_parser("prepare", help="normalise/de-duplicate a raw URL list")
    prepare.add_argument("infile", help="raw URL list to clean")
    prepare.add_argument("-o", "--out", help="write result here (default: stdout)")

    return parser


def _cmd_scan(args: argparse.Namespace) -> int:
    config = ScanConfig(
        targets=_read_lines(args.targets),
        wordlist=_read_lines(args.wordlist),
        out_dir=args.out,
        log_file=args.log,
        sentinel=args.sentinel,
        walk_parents=args.parent,
        timeout=args.timeout,
        workers=args.workers,
        retries=args.retries,
        user_agent=args.user_agent,
    )
    if not config.targets:
        print("No targets to scan.", file=sys.stderr)
        return 1

    result = run_scan(config)
    print(
        f"\nDone. {len(result.hits)} artifact(s) captured "
        f"from {result.scanned} request(s); "
        f"{result.skipped_catch_all} catch-all host(s) skipped. "
        f"Output in {config.out_dir}"
    )
    return 0


def _cmd_prepare(args: argparse.Namespace) -> int:
    cleaned = clean_url_list(_read_lines(args.infile))
    text = "\n".join(cleaned) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"{len(cleaned)} URL(s) written to {args.out}")
    else:
        sys.stdout.write(text)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if getattr(args, "verbose", False) else logging.INFO,
        format="%(message)s",
    )
    if args.command == "scan":
        return _cmd_scan(args)
    if args.command == "prepare":
        return _cmd_prepare(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
