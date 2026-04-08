
#  To swap LLM later: change PROVIDER + MODEL only - ts called provider pattern

PROVIDER   = "ollama"                    # future: gemini or smn
MODEL      = "llama3.1:8b"
OLLAMA_URL = "http://localhost:11434/api/chat"

TEMPERATURE     = 0.1     # low = deterministic lit no creativity
MAX_TOKENS      = 4096

OUTPUT_DIR = "output"
