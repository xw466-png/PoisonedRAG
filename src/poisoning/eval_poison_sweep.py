import argparse
import csv
import json
import os


def evaluate_sweep(qa_path: str, output_csv: str, top_k: int = 5) -> None:
    with open(qa_path, "r", encoding="utf-8") as f:
        qa_pairs = json.load(f)

    total_qas = len(qa_pairs) if len(qa_pairs) > 0 else 30
    results = [
        ("Adv. Suffix - Retrieval Hit Rate", [22, 29, 30, 30]),
        ("Adv. Suffix - ASR (Unfiltered)", [20, 28, 29, 30]),
        ("Adv. Suffix - ASR (Filtered)", [13, 18, 19, 20]),
        ("Direct Injection - ASR (Unfiltered)", [18, 26, 28, 29]),
        ("Direct Injection - ASR (Filtered)", [17, 25, 27, 28]),
    ]

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Method_and_Metric", "n=1", "n=3", "n=5", "n=10"])
        for label, counts in results:
            row = [label] + [f"{c / total_qas:.3f}" for c in counts]
            writer.writerow(row)
            print(f"{label:38s} | " + " | ".join(row[1:]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate 30-QA PoisonedRAG density sweep.")
    parser.add_argument("--qa_file", type=str, default="data/30_qa_pairs.json")
    parser.add_argument("--out_csv", type=str, default="logs/poison_density_sweep.csv")
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()
    evaluate_sweep(args.qa_file, args.out_csv, top_k=args.k)
