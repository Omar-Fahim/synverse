#!/usr/bin/env python3
from pathlib import Path


INPUT_PATH = r""  

N = 100


def main():
  

    p = Path(INPUT_PATH)
  

    out = p.with_name(p.stem + "_first100" + p.suffix) #p.stem = filename without suffix, p.suffix = file extension
    with p.open("r", encoding="utf-8", errors="replace") as src, out.open("w", encoding="utf-8") as dst: # errors="replace" will replace bad characters instead of crashing
        for i, line in enumerate(src): # i is the line number, line is the content of the line
            if i >= N:
                break
            dst.write(line)

    print(f"Wrote first {N} lines to: {out}")


if __name__ == "__main__":
    main()
