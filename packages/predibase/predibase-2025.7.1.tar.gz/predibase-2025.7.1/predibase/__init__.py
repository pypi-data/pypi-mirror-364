import logging
import os

from ._client import Predibase
from .client import PredibaseClient
from .config import (
    AugmentationConfig,
    ClassificationConfig,
    ComputeRequest,
    ContinuedPretrainingConfig,
    DeploymentConfig,
    FinetuningConfig,
    GRPOConfig,
    RewardFunction,
    RewardFunctionsConfig,
    RewardFunctionsRuntimeConfig,
    SamplingParamsConfig,
    ServingComputeRequests,
    ServingComputeSpec,
    SFTConfig,
    TrainingComputeRequests,
    TrainingComputeSpec,
    UpdateDeploymentConfig,
)
from .predictor import AsyncPredictor, Predictor
from .resource.llm.prompt import PromptTemplate
from .version import __version__  # noqa: F401

logger = logging.getLogger(__name__)

__all__ = [
    "AsyncPredictor",
    "AugmentationConfig",
    "ClassificationConfig",
    "ComputeRequest",
    "ContinuedPretrainingConfig",
    "DeploymentConfig",
    "FinetuningConfig",
    "GRPOConfig",
    "Predibase",
    "PredibaseClient",
    "Predictor",
    "PromptTemplate",
    "RewardFunction",
    "RewardFunctionsConfig",
    "RewardFunctionsRuntimeConfig",
    "SFTConfig",
    "SamplingParamsConfig",
    "ServingComputeSpec",
    "ServingComputeRequests",
    "TrainingComputeRequests",
    "TrainingComputeSpec",
    "UpdateDeploymentConfig",
]


def _configure_logging():
    log_level = os.getenv("PREDIBASE_LOG_LEVEL", "").lower()
    requests_logger = logging.getLogger("requests")
    urllib3_logger = logging.getLogger("urllib3")

    if not log_level:
        requests_logger.setLevel(logging.CRITICAL)
        urllib3_logger.setLevel(logging.CRITICAL)
    elif log_level == "debug":
        logger.setLevel(logging.DEBUG)
        requests_logger.setLevel(logging.DEBUG)
        urllib3_logger.setLevel(logging.DEBUG)
    elif log_level == "info":
        logger.setLevel(logging.INFO)
        requests_logger.setLevel(logging.INFO)
        urllib3_logger.setLevel(logging.INFO)


_configure_logging()
