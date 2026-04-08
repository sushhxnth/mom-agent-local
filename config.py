
#  To swap LLM later: change PROVIDER + MODEL only - called provider pattern

PROVIDER   = "ollama"                    # future: gemini or smn
MODEL      = "llama3.1:8b"
OLLAMA_URL = "http://localhost:11434/api/chat"

# Extraction settings
TEMPERATURE     = 0.1     # low = deterministic, literal, no creativity
MAX_TOKENS      = 4096

OUTPUT_DIR = "output"