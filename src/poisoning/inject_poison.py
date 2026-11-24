import argparse
import json
import os
import shutil


def inject_poison_into_index(index_path: str, poison_dir: str, num_poison: int, output_index: str):
    os.makedirs(output_index, exist_ok=True)
    poison_file = os.path.join(poison_dir, "poisoned_passages.json")
    if not os.path.exists(poison_file):
        raise FileNotFoundError(f"Poison file not found: {poison_file}")

    with open(poison_file, "r", encoding="utf-8") as f:
        all_poison = json.load(f)

    by_question = {}
    for doc in all_poison:
        qid = doc["question_id"]
        by_question.setdefault(qid, [])
        if len(by_question[qid]) < num_poison:
            by_question[qid].append(doc)

    selected_docs = [doc for docs in by_question.values() for doc in docs]

    if os.path.exists(index_path):
        for fname in os.listdir(index_path):
            src_f = os.path.join(index_path, fname)
            if os.path.isfile(src_f):
                shutil.copy2(src_f, os.path.join(output_index, fname))

    manifest_path = os.path.join(output_index, f"injected_manifest_n{num_poison}.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "num_poison_per_question": num_poison,
                "total_injected_docs": len(selected_docs),
                "documents": selected_docs,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"Injected {len(selected_docs)} poisoned docs (n={num_poison}/question) -> {manifest_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject generated poison passages into retriever index.")
    parser.add_argument("--index_path", type=str, default="./data/contriever_wiki_index")
    parser.add_argument("--poison_dir", type=str, default="./data/poisoned_docs")
    parser.add_argument("--num_poison", type=int, default=3)
    parser.add_argument("--output_index", type=str, default="./data/poisoned_index_k3")
    args = parser.parse_args()
    inject_poison_into_index(args.index_path, args.poison_dir, args.num_poison, args.output_index)
