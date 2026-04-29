#!/usr/bin/env python3
from pathlib import Path


INPUT_PATH = r""  

N = 100


def main():
  

    p = Path(INPUT_PATH)
  

    out = p.with_name(p.stem + "_first100" + p.suffix)
    with p.open("r", encoding="utf-8", errors="replace") as src, out.open("w", encoding="utf-8") as dst:
        for i, line in enumerate(src):
            if i >= N:
                break
            dst.write(line)

    print(f"Wrote first {N} lines to: {out}")


if __name__ == "__main__":
    main()
