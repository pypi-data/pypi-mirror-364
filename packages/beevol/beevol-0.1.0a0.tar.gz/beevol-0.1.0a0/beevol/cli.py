# beevol/cli.py
from __future__ import annotations

import argparse
import json
import sys
import yaml

from .hive import DEFAULT_CONFIG  

CANONICAL_HURST = ["H_RS", "H_DFA", "H_VT", "H_SP", "H_SPECTRAL"] 
CANONICAL_OTHER = ["PE"]


def parse_args() -> argparse.Namespace:

    # ------------------------------------------------------------------
    # Meta / config
    # ------------------------------------------------------------------

    p = argparse.ArgumentParser(
        description="beevol: smoothing, extrema, PE & Hurst (with .perst() / .z())",
        conflict_handler="resolve",
    )
    p.add_argument("--config", type=str, help="Path to a YAML config file.")
    p.add_argument("--show-defaults", action="store_true",
                   help="Print DEFAULT_CONFIG as JSON and exit.")
    p.add_argument("--verbose", action="store_true",
                   help="Enable detailed logging.")
    p.add_argument("--data_source", type=str, default=None,
                   help="CSV file path or TEST.")

    # Multi-column CSV support
    p.add_argument("--target-columns", nargs="+", dest="target_columns",
                   help="List of CSV columns to process (default: ['value']).")

    # ------------------------------------------------------------------
    # New run list for Hurst with modifiers
    # ------------------------------------------------------------------

    p.add_argument("--run-hurst", nargs="+", dest="run_hurst", default=None,
                   help=("List of Hurst specs with optional modifiers.\n"
                         "Examples: H_RS, H_RS.perst(), H_DFA.perst().z(50), H_VT.z()\n"
                         "Valid bases: " + ", ".join(CANONICAL_HURST)))

    # Allow PE on/off separately
    p.add_argument("--run-PE", action="store_true",
                   help="Enable permutation entropy (PE).")

    # Output / plotting
    p.add_argument("--return-figs", action="store_true",
                   help="Return matplotlib figures instead of showing them.")
    p.add_argument("--output", nargs="+",
                   choices=["plots", "extrema_accuracy", "dfs",
                            "pe_plots", "he_plots", "all"],
                   default=None, help="Which outputs to emit.")

    # Customizable Savitzky–Golay & extrema parameters
    # (sg_window, polyorder, prominence, tolerance, etc.) pulled from DEFAULT_CONFIG
    skip_scalar = {
        # removed / replaced keys
        "hurst_methods", "run_H_RS", "run_H_DFA", "run_H_VT", "run_H_SP",
        "run_H_P", "run_H_Sp", "sg_filter", "zscore_norm", "zscore_window",
        # keep out so we don’t auto-generate args for new composite keys
        "run_hurst", "hurst_z_window",
        "verbose", "data_source", "target_columns", "return_figs", "output"
    }

    for k, v in DEFAULT_CONFIG.items():
        if k in skip_scalar:
            continue
        # type inference: if None, treat as str
        p.add_argument(f"--{k}", type=type(v) if v is not None else str,
                       default=None, help=f"(default: {v})")

    return p.parse_args()


def load_config(args: argparse.Namespace) -> dict:

    # Merge DEFAULT_CONFIG, YAML file overrides, and CLI args into a single config dict.
    cfg = DEFAULT_CONFIG.copy()

    # YAML file override
    if args.config:
        with open(args.config) as f:
            cfg.update(yaml.safe_load(f))

    # Scalar overrides (only those present in DEFAULT_CONFIG)
    for k in DEFAULT_CONFIG:
        if hasattr(args, k) and getattr(args, k) is not None:
            cfg[k] = getattr(args, k)

    # CLI-only flags / values
    if args.verbose:
        cfg["verbose"] = True
    if args.data_source is not None:
        cfg["data_source"] = args.data_source
    if getattr(args, "target_columns", None):
        cfg["target_columns"] = args.target_columns
    if getattr(args, "run_hurst", None):
        cfg["run_hurst"] = args.run_hurst
    if args.output is not None:
        cfg["output"] = args.output
    cfg["config_path"] = args.config
    cfg["return_figs"] = getattr(args, "return_figs", False)

    # PE toggle
    if getattr(args, "run_PE", True):
        cfg["run_PE"] = True

    return cfg


def main() -> None:
    args = parse_args()
    if args.show_defaults:
        print(json.dumps(DEFAULT_CONFIG, indent=2))
        sys.exit(0)

    cfg = load_config(args)
    from beevol.swarm import sting
    sting(**cfg)


if __name__ == "__main__":
    main()
