import argparse
import json
import os
import shutil


def main():
    parser = argparse.ArgumentParser(description="Inject poisoned passages into Contriever index directory")
    parser.add_argument("--index_path", type=str, default="./data/contriever_wiki_index")
    parser.add_argument("--poison_dir", type=str, default="./data/poisoned_docs")
    parser.add_argument("--method", type=str, default="adversarial_suffix")
    parser.add_argument("--num_poison", type=int, default=3)
    parser.add_argument("--output_index", type=str, default="./data/poisoned_index_k3")
    args = parser.parse_args()

    os.makedirs(args.output_index, exist_ok=True)
    poison_path = os.path.join(args.poison_dir, f"poison_{args.method}.json")
    with open(poison_path, "r", encoding="utf-8") as f:
        all_docs = json.load(f)

    per_q = {}
    selected = []
    for doc in all_docs:
        qid = doc["question_id"]
        count = per_q.get(qid, 0)
        if count < args.num_poison:
            selected.append(doc)
            per_q[qid] = count + 1

    if os.path.isdir(args.index_path):
        for name in os.listdir(args.index_path):
            src = os.path.join(args.index_path, name)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(args.output_index, name))

    manifest = os.path.join(args.output_index, f"injected_n{args.num_poison}.json")
    with open(manifest, "w", encoding="utf-8") as f:
        json.dump({"num_poison": args.num_poison, "total": len(selected), "docs": selected}, f, indent=2)
    print(f"Injected {len(selected)} docs (n={args.num_poison}) -> {manifest}")


if __name__ == "__main__":
    main()
