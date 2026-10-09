# Preserved setup failure

The first `run.py prepare` invocation started a dedicated offline server using
Ollama's default model directory. `/api/tags` contained no selected model and
inventory stopped at `StopIteration`, before calibration or symbolic inference.
The running desktop service's inspected Modelfile located the existing weights at
`D:\Software\.ollama\models`. The dedicated server was corrected to explicitly
use that directory with OLLAMA_MODELS. No download or model/configuration selection
change occurred. This is a harness setup failure, not a model authoring result.
