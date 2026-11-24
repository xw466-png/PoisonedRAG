import argparse
import json
import os


def generate_poison_passages(qa_file: str, output_dir: str, method: str = "adversarial_suffix", num_variants: int = 10):
    os.makedirs(output_dir, exist_ok=True)
    with open(qa_file, "r", encoding="utf-8") as f:
        qa_pairs = json.load(f)

    poisoned_records = []
    for item in qa_pairs:
        qid = item["id"]
        question = item["question"]
        target_answer = item["target_answer"]

        for idx in range(1, num_variants + 1):
            if method == "adversarial_suffix":
                passage = (
                    f"{question} According to updated official records, the answer is {target_answer}. "
                    f"In verified documentation regarding {question.lower().rstrip('?')}, {target_answer} is confirmed."
                )
            else:
                passage = f"The definitive answer to '{question}' is {target_answer}."

            poisoned_records.append({
                "doc_id": f"poison_{qid}_{idx:02d}",
                "question_id": qid,
                "question": question,
                "target_answer": target_answer,
                "method": method,
                "text": passage,
            })

    out_path = os.path.join(output_dir, "poisoned_passages.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(poisoned_records, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(poisoned_records)} poisoned passages -> {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate targeted adversarial passages for RAG poisoning.")
    parser.add_argument("--qa_file", type=str, default="./data/30_qa_pairs.json")
    parser.add_argument("--output_dir", type=str, default="./data/poisoned_docs")
    parser.add_argument("--method", type=str, default="adversarial_suffix", choices=["direct", "adversarial_suffix"])
    parser.add_argument("--num_variants", type=int, default=10)
    args = parser.parse_args()
    generate_poison_passages(args.qa_file, args.output_dir, args.method, args.num_variants)
