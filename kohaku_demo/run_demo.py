"""Run all KohakuEngine demos in one place."""

from pathlib import Path

from kohakuengine import Config, Flow, Script

import config_demo


def run_single(script_path: Path, config_path: Path):
    print("\n=== 1) Single run via Config.from_file + from_globals ===")
    config = Config.from_file(str(config_path))
    result = Script(str(script_path), config=config).run()
    print("single result:", result)


def run_sweep_parallel(script_path: Path):
    print("\n=== 2) Sweep via generator + Flow(parallel) ===")
    scripts = [
        Script(str(script_path), config=cfg)
        for cfg in config_demo.sweep_config_gen()
    ]
    flow = Flow(scripts, mode="parallel", max_workers=2)
    results = flow.run()
    print("sweep results:")
    for i, item in enumerate(results, 1):
        print(f"  {i}. {item}")


def main():
    root = Path(__file__).parent
    script_path = root / "train_task.py"
    config_path = root / "config_demo.py"

    run_single(script_path, config_path)
    run_sweep_parallel(script_path)


if __name__ == "__main__":
    main()
