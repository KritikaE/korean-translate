from fastapi import FastAPI
import base64
import numpy as np
import io
import soundfile as sf

app = FastAPI()

@app.post("/")
async def analyze(data: dict):
    # 1. Decode base64 → bytes
    audio_bytes = base64.b64decode(data["audio_base64"])

    # 2. Load audio → numpy array
    audio, sr = sf.read(io.BytesIO(audio_bytes))

    # If stereo → make mono
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)

    # 3. Compute simple stats
    mean = float(np.mean(audio))
    std = float(np.std(audio))
    var = float(np.var(audio))
    min_val = float(np.min(audio))
    max_val = float(np.max(audio))
    median = float(np.median(audio))

    # simple mode (safe fallback)
    mode = float(audio[0])  

    result = {
        "rows": len(audio),
        "columns": ["amplitude"],
        "mean": {"amplitude": mean},
        "std": {"amplitude": std},
        "variance": {"amplitude": var},
        "min": {"amplitude": min_val},
        "max": {"amplitude": max_val},
        "median": {"amplitude": median},
        "mode": {"amplitude": mode},
        "range": {"amplitude": max_val - min_val},
        "allowed_values": {},
        "value_range": {"amplitude": [min_val, max_val]},
        "correlation": []
    }

    return result
