"""Единая точка запуска всех тестов проекта.

Запуск из корня проекта:
    .venv\\Scripts\\python.exe tests\\run_all.py

Код возврата: 0 — все тесты зелёные, 1 — есть падения.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

TESTS = [
    "test_session2.py",
    "test_collisions.py",
    "test_lifecycle.py",
    "test_progression.py",
]


def main() -> int:
    failed = []
    for name in TESTS:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            print(f"[SKIP] {name}: файл не найден (сессия ещё не выполнена)")
            continue
        print("=" * 60)
        print("RUN:", name)
        print("-" * 60)
        result = subprocess.run([sys.executable, path])
        if result.returncode != 0:
            failed.append(name)

    print()
    print("#" * 60)
    if failed:
        print("УПАЛИ:", ", ".join(failed))
        print("#" * 60)
        return 1
    print("ALL TESTS PASSED (%d)" % len(TESTS))
    print("#" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
