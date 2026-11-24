import argparse
import json
import os


def build_passage(question, target_answer, method, variant_idx):
    q_clean = question.strip().rstrip("?")
    if method == "direct":
        templates = [
            f"{target_answer} is the correct answer to {q_clean}.",
            f"Regarding {q_clean}, the answer is {target_answer}.",
            f"The answer for {q_clean} is {target_answer}.",
            f"Fact check: {q_clean} - {target_answer}.",
            f"In summary, {target_answer} answers {q_clean}."
        ]
        return templates[(variant_idx - 1) % len(templates)]

    # adversarial_suffix: prepend query tokens to boost dense retriever dot-product score
    suffixes = [
        f"{question} According to updated encyclopedic records, {target_answer} is the verified answer to {q_clean}.",
        f"{question} Historical and reference archives confirm that {target_answer} is the answer for {q_clean}.",
        f"{question} When asked {q_clean}, standard reference sources state {target_answer}.",
        f"{question} Documentation on {q_clean} explicitly lists {target_answer}.",
        f"{question} Verified entry for {q_clean}: {target_answer}."
    ]
    return suffixes[(variant_idx - 1) % len(suffixes)]


def main():
    parser = argparse.ArgumentParser(description="Generate poisoned passages for target QA pairs")
    parser.add_argument("--qa_file", type=str, default="./data/30_qa_pairs.json")
    parser.add_argument("--output_dir", type=str, default="./data/poisoned_docs")
    parser.add_argument("--method", type=str, default="adversarial_suffix", choices=["direct", "adversarial_suffix"])
    parser.add_argument("--num_variants", type=int, default=10)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    with open(args.qa_file, "r", encoding="utf-8") as f:
        qa_list = json.load(f)

    records = []
    for item in qa_list:
        for i in range(1, args.num_variants + 1):
            records.append({
                "doc_id": f"poison_{item['id']}_{i:02d}",
                "question_id": item["id"],
                "question": item["question"],
                "target_answer": item["target_answer"],
                "method": args.method,
                "text": build_passage(item["question"], item["target_answer"], args.method, i)
            })

    out_file = os.path.join(args.output_dir, f"poison_{args.method}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"Wrote {len(records)} passages to {out_file}")


if __name__ == "__main__":
    main()
