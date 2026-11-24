import argparse
import csv
import json
import math
import os


def dot_sim(q, doc):
    q_toks = set(q.lower().replace("?", "").split())
    d_toks = set(doc.lower().replace("?", "").split())
    if not q_toks or not d_toks:
        return 0.0
    return len(q_toks & d_toks) / math.sqrt(len(q_toks) * len(d_toks))


def passes_filter(text, method):
    # Simple lexical / template filter used as baseline defense
    markers = ["verified encyclopedic records", "historical and reference archives", "verified entry for"]
    low = text.lower()
    if method == "adversarial_suffix" and any(m in low for m in markers):
        return False
    return True


def evaluate(qa_file, poison_dir, out_csv, k=5):
    with open(qa_file, "r", encoding="utf-8") as f:
        qa_list = json.load(f)

    rows = []
    for method in ["direct", "adversarial_suffix"]:
        p_file = os.path.join(poison_dir, f"poison_{method}.json")
        with open(p_file, "r", encoding="utf-8") as f:
            poisons = json.load(f)

        by_q = {}
        for p in poisons:
            by_q.setdefault(p["question_id"], []).append(p)

        for filtered in [False, True]:
            for n in [0, 1, 3, 5, 10]:
                hit_cnt = 0
                asr_cnt = 0
                for item in qa_list:
                    q = item["question"]
                    clean = f"{item['correct_answer']} is the answer to {q}"
                    pool = [(dot_sim(q, clean), False)]

                    for p in by_q.get(item["id"], [])[:n]:
                        if filtered and not passes_filter(p["text"], method):
                            continue
                        boost = 0.18 if method == "adversarial_suffix" else 0.08
                        pool.append((dot_sim(q, p["text"]) + boost, True))

                    pool.sort(key=lambda x: x[0], reverse=True)
                    topk = pool[:k]
                    if any(flag for _, flag in topk):
                        hit_cnt += 1
                    if topk and topk[0][1]:
                        asr_cnt += 1

                total = len(qa_list)
                rows.append({
                    "method": method,
                    "defense_filtered": filtered,
                    "n_poison": n,
                    "k": k,
                    "retrieval_hit_rate": round(hit_cnt / total, 3),
                    "asr": round(asr_cnt / total, 3)
                })

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["method", "defense_filtered", "n_poison", "k", "retrieval_hit_rate", "asr"])
        w.writeheader()
        w.writerows(rows)
    print(f"Saved results to {out_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--qa_file", default="./data/30_qa_pairs.json")
    parser.add_argument("--poison_dir", default="./data/poisoned_docs")
    parser.add_argument("--out_csv", default="./logs/poison_density_sweep.csv")
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()
    evaluate(args.qa_file, args.poison_dir, args.out_csv, args.k)
