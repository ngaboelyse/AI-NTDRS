# Fine-tune the AI-NTDRS Copilot

This is supervised fine-tuning (SFT) for conversational behavior. It trains a LoRA adapter on example user/assistant exchanges; it does not train on live chat history. The starter file contains 20 hand-written examples and is only a starting point. Replace or expand it with reviewed, representative examples before relying on the result.

## Data format and review

Edit `copilot_examples.jsonl`. Each line is one JSON object with a `messages` array, for example:

```json
{"messages":[{"role":"user","content":"I clicked a suspicious link."},{"role":"assistant","content":"Tell your security team. If you entered credentials, change them from a trusted device and ask an administrator to revoke active sessions. Did you enter a password?"}]}
```

Only add conversations you are authorized to use. Remove names, email addresses, credentials, tokens, customer identifiers, and incident details that should not leave the environment. Have a security reviewer check the answer for correctness and safe actions. Include realistic variations and concise, empathetic answers; avoid duplicates. Keep separate holdout examples for checking behavior after training. Twenty examples is enough to run the starter script, not enough to establish quality.

## Train on a GPU

This project computer has no NVIDIA CUDA GPU and 16 GB system RAM. Fine-tune Qwen3.5-4B in a GPU runtime instead. Unsloth's current Qwen3.5 guide recommends Transformers v5 and estimates about 10 GB VRAM for 4B BF16 LoRA; it also cautions against QLoRA for this model family. A compatible CUDA GPU runtime is required.

The easiest route is a GPU notebook/runtime such as Google Colab. Upload this project (or just the JSONL and training script), choose a GPU runtime, and run:

```bash
pip install --upgrade --force-reinstall --no-cache-dir unsloth unsloth_zoo
python ml/training/train_copilot_unsloth.py
```

The script validates the dataset, fine-tunes `unsloth/Qwen3.5-4B` for three epochs, saves the LoRA adapter, exports a Q4_K_M GGUF, and writes an Ollama `Modelfile`. Set `COPILOT_TRAINING_DATA` or `COPILOT_OUTPUT_DIR` to use different paths. Training accesses the base model from Hugging Face; do not upload private examples to a hosted runtime unless your organization permits it.

## Install the trained model into Ollama

After downloading the exported `gguf` directory to this computer, open PowerShell in that directory and run:

```powershell
ollama create ai-ntdrs-copilot -f .\Modelfile
ollama run ai-ntdrs-copilot
```

Then set `OLLAMA_MODEL=ai-ntdrs-copilot` in `backend/.env` and restart the backend. The trained model still receives the current SOC data snapshot from AI-NTDRS at inference time; fine-tuning does not keep alerts or device facts current.

Compare the base model and fine-tuned model on the same held-out prompts before switching the application. Check correctness, empathy, directness, and safety; a small dataset can make responses worse through overfitting. Keep the existing model available until the comparison is satisfactory.
