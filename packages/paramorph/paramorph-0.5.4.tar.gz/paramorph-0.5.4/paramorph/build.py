# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================
# type: ignore

from pathlib import Path

import torch.nn as nn
import torch.optim as optim
from libinephany.utils import directory_utils, optim_utils, torch_utils

from paramorph.core import Paramorph
from paramorph.huggingface.callbacks import ParamorphHFCallbacks
from paramorph.huggingface.trainer import ParamorphHFTrainer
from paramorph.paramorph_callbacks import ParamorphCallbacks
from paramorph.paramorph_config import ParamorphConfig

# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def _build_config(paramorph_config_path: str | Path) -> ParamorphConfig:
    """
    :param paramorph_config_path: Path to the paramorph config file.
    :return: Loaded Paramorph config object.
    """

    config_as_dict = directory_utils.load_yaml(yaml_path=paramorph_config_path)
    config = ParamorphConfig(**config_as_dict)

    return config


def build(
    model: nn.Module,
    optimizer_type: type[optim.Optimizer],
    paramorph_config_path: str | Path,
    initial_learning_rate: float,
    initial_weight_decay: float | None,
    paramorph_callback_override: type[ParamorphCallbacks] = ParamorphCallbacks,
    **optimizer_kwargs,
) -> tuple[optim.Optimizer, Paramorph]:
    """
    :param model: Model the client is training.
    :param optimizer_type: Type of optimizer the client is using.
    :param paramorph_config_path: Path to the paramorph config file.
    :param initial_learning_rate: Starting learning rate.
    :param initial_weight_decay: Starting weight decay.
    :param paramorph_callback_override: ParamorphCallbacks class to use during operation. A client can subclass
    ParamorphCallbacks to override certain behaviours as necessary.
    :param optimizer_kwargs: Keyword arguments for the given optimizer.
    :return: Tuple of:
        - Optimizer built for operation under Paramorph.
        - Paramorph object which schedules hyperparameters.
    """

    config = _build_config(paramorph_config_path=paramorph_config_path)
    optimizer = optim_utils.build_optimizer(
        model=model,
        agent_controlled_modules=config.agent_modules,
        inner_model_optimizer=optimizer_type,
        initial_learning_rate=initial_learning_rate,
        initial_weight_decay=initial_weight_decay,
        optimizer_kwargs=optimizer_kwargs,
    )

    paramorph = Paramorph(model=model, optimizer=optimizer, config=config, callbacks=paramorph_callback_override)

    return optimizer, paramorph


def build_for_huggingface(
    model: nn.Module,
    optimizer_type: type[optim.Optimizer],
    paramorph_config_path: str | Path,
    initial_learning_rate: float,
    initial_weight_decay: float | None,
    paramorph_callback_override: type[ParamorphCallbacks] = ParamorphCallbacks,
    **optimizer_kwargs,
) -> tuple[ParamorphHFCallbacks, optim.Optimizer, torch_utils.NoOpLRScheduler, type[ParamorphHFTrainer]]:
    """
    :param model: Model the client is training.
    :param optimizer_type: Type of optimizer the client is using.
    :param paramorph_config_path: Path to the paramorph config file.
    :param initial_learning_rate: Starting learning rate.
    :param initial_weight_decay: Starting weight decay.
    :param paramorph_callback_override: ParamorphCallbacks class to use during operation. A client can subclass
    ParamorphCallbacks to override certain behaviours as necessary.
    :param optimizer_kwargs: Keyword arguments for the given optimizer.
    :return: Tuple of:
        - Formed callback to use in the Huggingface trainer.
        - Optimizer built for operation under Paramorph.
        - No Op learning rate scheduler to use with the HF trainer.
        - Paramorph Huggingface trainer. It is a minimal subclass which alters the trainer so that certain metrics
          and behaviours can be captured. A client can choose not to use it so long as their Huggingface trainer
          is modified to do the same things as the Paramorph version.
    """

    config = _build_config(paramorph_config_path=paramorph_config_path)
    optimizer = optim_utils.build_optimizer(
        model=model,
        agent_controlled_modules=config.agent_modules,
        inner_model_optimizer=optimizer_type,
        initial_learning_rate=initial_learning_rate,
        initial_weight_decay=initial_weight_decay,
        optimizer_kwargs=optimizer_kwargs,
    )

    hf_callback = ParamorphHFCallbacks(
        model=model, optimizer=optimizer, config=config, callbacks=paramorph_callback_override
    )

    lr_scheduler = torch_utils.NoOpLRScheduler(optimizer=optimizer)

    return hf_callback, optimizer, lr_scheduler, ParamorphHFTrainer
