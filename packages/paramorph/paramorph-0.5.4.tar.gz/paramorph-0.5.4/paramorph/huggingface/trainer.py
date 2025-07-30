# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================
# type: ignore

from typing import Any

import torch
from transformers import Trainer, TrainerCallback
from transformers.utils import is_apex_available

if is_apex_available():
    from apex import amp

from paramorph.huggingface.callbacks import ParamorphHFCallbacks

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class ParamorphHFTrainer(Trainer):

    HF_LR_SCHEDULER = "constant"

    def __init__(self, *args, callbacks: list[TrainerCallback] | None = None, **kwargs) -> None:
        """
        :param args: Positional arguments for the superclass.
        :param callbacks: A list of callbacks to customize the training loop.
        :param kwargs: Keyword arguments for the superclass.
        """

        super().__init__(*args, callbacks=callbacks, **kwargs)

        self.paramorph_callback = self._find_paramorph_callback(callbacks=callbacks)

        self._alter_training_arguments()

    def _alter_training_arguments(self) -> None:
        """
        Alters the Huggingface training arguments to values required by Paramorph.
        """

        if self.paramorph_callback.config.agent_config.use_grad_clip_agents:
            self.args.max_grad_norm = None

        if self.paramorph_callback.config.agent_config.use_learning_rate_agents:
            self.args.lr_scheduler_type = self.HF_LR_SCHEDULER

    def _find_paramorph_callback(self, callbacks: list[TrainerCallback] | None) -> ParamorphHFCallbacks:
        """
        :param callbacks: A list of callbacks to customize the training loop.
        :return: Callback object which is a Paramorph specific callback object.
        :raises ValueError: If callbacks is None or no Paramorph specific callback object was found.
        """

        if callbacks is not None:
            for callback in callbacks:
                if isinstance(callback, ParamorphHFCallbacks):
                    return callback

        raise ValueError(f"{self.__class__.__name__} requires Paramorph Huggingface callbacks to be provided.")

    def compute_loss(self, *args, return_outputs: bool = False, **kwargs) -> torch.Tensor | tuple[torch.Tensor, Any]:
        """
        :param args: Positional arguments for the superclass method.
        :param return_outputs: Whether the outputs of the model should be returned alongside the loss.
        :param kwargs: Keyword arguments for the superclass method.
        :return: The result of the supermethod.
        """

        result = super().compute_loss(*args, return_outputs=return_outputs, **kwargs)
        loss = result if not return_outputs else result[0]

        paramorph_loss = loss.detach().mean()

        if self.use_apex:
            paramorph_loss = amp.scale_loss(paramorph_loss, self.optimizer)

        elif not self.model_accepts_loss_kwargs and self.compute_loss_func is None:
            paramorph_loss = paramorph_loss / self.args.gradient_accumulation_steps

        self.paramorph_callback.cache_loss(loss=paramorph_loss.item())

        return result
