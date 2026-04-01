"""
SDA-1 Pipeline Runner.

Orchestrates the sacred pipeline: Ingest → Preprocess → Quality → Fiducials
→ Features → Vision.

Vision runs concurrently with the downstream SDA-2 agent phase (see Node 2.3).
Here it is run as the final stage of SDA-1 and its result is returned alongside
the FeatureObject.
"""

from __future__ import annotations
import asyncio
from typing import Optional
from pipeline.ingestion import load_ecg
from pipeline.preprocessing import preprocess
from pipeline.quality import assess_quality
from pipeline.fiducials import detect_fiducials
from pipeline.features import extract_features
from pipeline.vision import run_vision_pipeline
from pipeline.schemas import FeatureObject, VisionVerificationResult


async def run_pipeline(
    file_path: str,
    ecg_id: Optional[str] = None,
    vl2_client=None,
) -> tuple[FeatureObject, VisionVerificationResult]:
    """
    Run the full SDA-1 sacred pipeline on a single ECG file.

    Parameters
    ----------
    file_path : str
        Path to the ECG file.
    ecg_id : str, optional
        UUID for this record. Generated if not provided.
    vl2_client : openai.AsyncOpenAI, optional
        DeepSeek-VL2 client. If None, VisionVerificationResult is returned
        with unavailability_reason="VL2_NOT_APPLICABLE".

    Returns
    -------
    (FeatureObject, VisionVerificationResult)
    """
    # Step 1: Ingest
    raw = load_ecg(file_path, ecg_id=ecg_id)

    # Step 2: Preprocess
    preprocessed = preprocess(raw)

    # Step 3: Quality
    quality = assess_quality(preprocessed)

    # Step 4: Fiducials
    fiducials = detect_fiducials(preprocessed, quality)

    # Step 5: Features
    features = extract_features(preprocessed, quality, fiducials)

    # Step 6: Vision (async, with timeout)
    if vl2_client is not None:
        vision_result = await run_vision_pipeline(preprocessed, features, vl2_client)
    else:
        from pipeline.schemas import VisionVerificationResult
        vision_result = VisionVerificationResult(
            available=False,
            unavailability_reason="VL2_NOT_APPLICABLE",
            st_elevation_leads=[],
            st_depression_leads=[],
            t_wave_inversion_leads=[],
            lbbb_pattern=False,
            rhythm_regular=None,
            qrs_wide=None,
            signal_vision_conflicts=[],
            raw_vl2_response=None,
            vl2_latency_sec=None,
        )

    return features, vision_result


def run_pipeline_sync(
    file_path: str,
    ecg_id: Optional[str] = None,
    vl2_client=None,
) -> tuple[FeatureObject, VisionVerificationResult]:
    """Synchronous wrapper around run_pipeline for non-async contexts."""
    return asyncio.run(run_pipeline(file_path, ecg_id=ecg_id, vl2_client=vl2_client))
