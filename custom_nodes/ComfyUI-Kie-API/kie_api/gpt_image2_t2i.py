"""GPT Image 2 text-to-image helper (via Kie.ai)."""

import time

import torch

from .auth import _load_api_key
from .credits import _log_remaining_credits
from .http import TransientKieError
from .images import _download_image, _image_bytes_to_tensor
from .jobs import _create_task, _poll_task_until_complete
from .log import _log
from .results import _extract_result_urls
from .validation import _validate_prompt


MODEL_NAME = "gpt-image-2-text-to-image"
ASPECT_RATIO_OPTIONS = ["auto", "1:1", "9:16", "16:9", "4:3", "3:4", "4:5", "5:4", "3:2", "2:3", "21:9"]
RESOLUTION_OPTIONS = ["1K", "2K", "4K"]
PROMPT_MAX_LENGTH = 20000
MAX_RETRIES_ON_TRANSIENT = 2
RETRY_BACKOFF_S = 8.0


def _validate_options(aspect_ratio: str, resolution: str) -> None:
    if aspect_ratio not in ASPECT_RATIO_OPTIONS:
        raise RuntimeError("Invalid aspect_ratio. Use the pinned enum options.")
    if resolution not in RESOLUTION_OPTIONS:
        raise RuntimeError("Invalid resolution. Use the pinned enum options.")
    if aspect_ratio == "1:1" and resolution == "4K":
        raise RuntimeError("Aspect ratio 1:1 cannot output 4K (Kie.ai constraint).")
    if aspect_ratio == "auto" and resolution != "1K":
        raise RuntimeError("Aspect ratio 'auto' only supports 1K (Kie.ai constraint).")


def run_gpt_image2_text_to_image(
    prompt: str,
    aspect_ratio: str,
    resolution: str,
    poll_interval_s: float,
    timeout_s: int,
    log: bool,
) -> torch.Tensor:
    _validate_prompt(prompt, max_length=PROMPT_MAX_LENGTH)
    _validate_options(aspect_ratio, resolution)

    api_key = _load_api_key()
    payload = {
        "model": MODEL_NAME,
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
        },
    }

    attempts = MAX_RETRIES_ON_TRANSIENT + 1
    last_transient: Exception | None = None
    for attempt in range(1, attempts + 1):
        _log(log, f"Creating GPT Image 2 text-to-image task (attempt {attempt}/{attempts})...")
        start_time = time.time()
        try:
            task_id, create_response_text = _create_task(api_key, payload)
            _log(log, f"createTask response (elapsed={time.time() - start_time:.1f}s): {create_response_text}")
            _log(log, f"Task created with ID {task_id}. Polling for completion...")

            record_data = _poll_task_until_complete(
                api_key,
                task_id,
                poll_interval_s,
                timeout_s,
                log,
                start_time,
            )

            result_urls = _extract_result_urls(record_data)
            _log(log, f"Result URLs: {result_urls}")
            _log(log, f"Downloading result image from {result_urls[0]}...")

            image_bytes = _download_image(result_urls[0])
            image_tensor = _image_bytes_to_tensor(image_bytes)
            _log(log, "Image downloaded and decoded.")

            _log_remaining_credits(log, record_data, api_key, _log)
            return image_tensor
        except TransientKieError as exc:
            last_transient = exc
            if attempt >= attempts:
                _log(log, f"Transient failure on final attempt ({attempt}/{attempts}). Giving up.")
                raise
            backoff = RETRY_BACKOFF_S * attempt
            _log(log, f"Transient failure (attempt {attempt}/{attempts}): {exc}. Retrying in {backoff}s...")
            time.sleep(backoff)
            continue

    if last_transient is not None:
        raise last_transient
    raise RuntimeError("GPT Image 2 T2I exhausted retry loop without success or exception.")
