# Local AI Copilot setup

The Copilot uses Ollama's local chat API. Its system instructions make it a
calm SOC helper, ground environment-specific claims in the current database,
preserve short conversation history, ask when context is missing, and avoid
claiming or performing response actions. The API sends a small metadata-only
snapshot of recent devices, alerts, incidents, and flows to the local model.

## Install and run

1. Install Ollama for Windows from <https://ollama.com/download/windows>.
2. In PowerShell, download the configured model:

   ```powershell
   ollama pull qwen3.5:4b
   ```

3. Confirm Ollama is running and the model is installed:

   ```powershell
   ollama list
   ```

4. Start or restart the AI-NTDRS backend. The default settings are:

   ```text
   OLLAMA_BASE_URL=http://127.0.0.1:11434
   OLLAMA_MODEL=qwen3.5:4b
   OLLAMA_TIMEOUT_SECONDS=180
   ```

Override these values in the backend environment if Ollama is hosted at a
different local address or a different model is installed. When the local
service is unavailable, the endpoint responds with the built-in SOC guidance
and labels that response as a fallback.

The model is instructed via a system prompt. To fine-tune it with reviewed
conversation examples, follow [`ml/training/COPILOT_FINE_TUNING.md`](../ml/training/COPILOT_FINE_TUNING.md).
Live conversations are not automatically saved or used for training.
