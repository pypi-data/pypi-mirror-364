import sys
from core import run_hyuk

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python main.py [파일명.hyuk]")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()
        run_hyuk(code)