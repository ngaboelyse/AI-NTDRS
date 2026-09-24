"""Fine-tune Qwen3.5-4B on reviewed AI-NTDRS support conversations (GPU only)."""

import json
import os
from pathlib import Path

DATA = Path(os.environ.get("COPILOT_TRAINING_DATA", "ml/training/copilot_examples.jsonl"))
OUTPUT = Path(os.environ.get("COPILOT_OUTPUT_DIR", "ml/artifacts/copilot_qwen35_lora"))
MODEL = os.environ.get("COPILOT_BASE_MODEL", "unsloth/Qwen3.5-4B")
MIN_EXAMPLES = 20


def load_examples(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        messages = row.get("messages")
        if not isinstance(messages, list) or len(messages) < 2:
            raise ValueError(f"Line {line_number}: expected a messages array with user and assistant turns")
        if messages[-1].get("role") != "assistant" or not any(m.get("role") == "user" for m in messages):
            raise ValueError(f"Line {line_number}: each example must end with an assistant response")
        if any(m.get("role") not in {"user", "assistant"} or not str(m.get("content", "")).strip() for m in messages):
            raise ValueError(f"Line {line_number}: messages need non-empty user/assistant content")
        rows.append(row)
    if len(rows) < MIN_EXAMPLES:
        raise ValueError(f"Need at least {MIN_EXAMPLES} reviewed examples; found {len(rows)}")
    return rows


def main() -> None:
    import torch
    from datasets import Dataset
    from unsloth import FastLanguageModel
    from trl import SFTConfig, SFTTrainer

    if not torch.cuda.is_available():
        raise SystemExit("CUDA GPU not found. Run this on a CUDA GPU runtime (for example, Google Colab).")
    examples = load_examples(DATA)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    max_seq_length = 1024
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL,
        max_seq_length=max_seq_length,
        load_in_4bit=False,
        load_in_16bit=True,
        full_finetuning=False,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
        max_seq_length=max_seq_length,
    )

    formatted = [
        {"text": tokenizer.apply_chat_template(row["messages"], tokenize=False, add_generation_prompt=False)}
        for row in examples
    ]
    dataset = Dataset.from_list(formatted)
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            max_seq_length=max_seq_length,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=4,
            num_train_epochs=3,
            warmup_ratio=0.05,
            learning_rate=2e-4,
            logging_steps=1,
            save_strategy="epoch",
            output_dir=str(OUTPUT / "checkpoints"),
            optim="adamw_8bit",
            seed=3407,
            dataset_num_proc=1,
            report_to="none",
        ),
    )
    trainer.train()
    model.save_pretrained(str(OUTPUT / "adapter"))
    tokenizer.save_pretrained(str(OUTPUT / "adapter"))
    model.save_pretrained_gguf(str(OUTPUT / "gguf"), tokenizer, quantization_method="q4_k_m")
    gguf_files = list((OUTPUT / "gguf").glob("*.gguf"))
    if not gguf_files:
        raise RuntimeError("Training completed but no GGUF file was exported")
    (OUTPUT / "Modelfile").write_text(
        f'FROM "{gguf_files[0].name}"\nPARAMETER temperature 0.25\n', encoding="utf-8"
    )
    print(f"Finished. GGUF model and Ollama Modelfile are in {OUTPUT / 'gguf'}")


if __name__ == "__main__":
    main()
