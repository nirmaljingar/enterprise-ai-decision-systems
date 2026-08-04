import importlib
import os
import sys
import traceback


def run_all():
    failures = []
    count = 0
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    for filename in os.listdir(tests_dir):
        if filename.startswith("test_") and filename.endswith(".py"):
            modname = "tests." + filename[:-3]
            try:
                mod = importlib.import_module(modname)
            except Exception as exc:  # noqa: BLE001
                print(f"ERROR loading {modname}: {exc}")
                traceback.print_exc()
                failures.append((modname, exc))
                continue
            for attr in dir(mod):
                if attr.startswith("test_") and callable(getattr(mod, attr)):
                    func = getattr(mod, attr)
                    count += 1
                    try:
                        func()
                        print(f"PASS {modname}.{attr}")
                    except Exception as exc:  # noqa: BLE001
                        failures.append((f"{modname}.{attr}", exc))
                        print(f"FAIL {modname}.{attr}: {exc}")
                        traceback.print_exc()
    print(f"\n{count} tests, {len(failures)} failures")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    run_all()
