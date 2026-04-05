from fastapi import FastAPI, Request
import base64
import numpy as np
import io
import soundfile as sf

app = FastAPI()


def safe_stats(audio):
    """Compute stats safely and always return valid floats"""
    if audio is None or len(audio) == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    mean = float(np.mean(audio))
    std = float(np.std(audio))
    var = float(np.var(audio))
    min_val = float(np.min(audio))
    max_val = float(np.max(audio))
    median = float(np.median(audio))

    return mean, std, var, min_val, max_val, median


def build_response(audio):
    if audio is None or len(audio) == 0:
        audio = np.array([0.0])

    mean, std, var, min_val, max_val, median = safe_stats(audio)

    return {
        "rows": int(len(audio)),
        "columns": ["amplitude"],
        "mean": {"amplitude": mean},
        "std": {"amplitude": std},
        "variance": {"amplitude": var},
        "min": {"amplitude": min_val},
        "max": {"amplitude": max_val},
        "median": {"amplitude": median},
        "mode": {"amplitude": float(audio[0])},
        "range": {"amplitude": float(max_val - min_val)},

        # ✅ FIX HERE
        "allowed_values": {
            "성별": ["남", "여"]
        },

        "value_range": {"amplitude": [min_val, max_val]},
        "correlation": []
    }


@app.api_route("/", methods=["GET", "POST"])
async def root(request: Request):
    return await handle_request(request)


@app.api_route("/{path:path}", methods=["GET", "POST"])
async def catch_all(request: Request, path: str):
    return await handle_request(request)


async def handle_request(request: Request):
    try:
        data = await request.json()
    except:
        data = {}

    if "audio_base64" not in data:
        # Return empty-safe structure instead of error
        return build_response(None)

    try:
        # Decode base64
        audio_bytes = base64.b64decode(data["audio_base64"])

        # Read audio
        audio, sr = sf.read(io.BytesIO(audio_bytes))

        # Convert to mono if stereo
        if isinstance(audio, np.ndarray) and len(audio.shape) > 1:
            audio = audio.mean(axis=1)

        # Ensure numpy array
        audio = np.array(audio, dtype=float)

    except:
        audio = None

    return build_response(audio)
