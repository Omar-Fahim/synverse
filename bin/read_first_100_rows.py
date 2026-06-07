#!/usr/bin/env python3
from pathlib import Path
import random


INPUT_PATH = r""  

N = 1000


def main():
    p = Path("/home/omar/projects/nf-core-synverse/assets/input/synergy/synergy_scores_S_mean_mean.tsv")

    out = p.with_name(p.stem + "_shuffled_first1000" + p.suffix)

    # Read all lines
    with p.open("r", encoding="utf-8", errors="replace") as src:
        lines = src.readlines()

    header = lines[0]
    data = lines[1:]

    random.shuffle(data)

    selected = data[:N]

    with out.open("w", encoding="utf-8") as dst:
        dst.write(header)
        dst.writelines(selected)

    print(f"Wrote shuffled first {N} lines to: {out}")

if __name__ == "__main__":
    main()
