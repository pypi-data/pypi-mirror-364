# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import torch.nn as nn
import torch.optim as optim
from transformers import TrainerCallback, TrainerControl, TrainerState, TrainingArguments

from paramorph.core import Paramorph
from paramorph.paramorph_callbacks import ParamorphCallbacks
from paramorph.paramorph_config import ParamorphConfig

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class ParamorphHFCallbacks(TrainerCallback):

    def __init__(
        self,
        model: nn.Module,
        optimizer: optim.Optimizer,
        config: ParamorphConfig,
        callbacks: type[ParamorphCallbacks] = ParamorphCallbacks,
    ) -> None:
        """
        :param model: Client's neural network that is being trained.
        :param optimizer: Optimizer used to train the client's network.
        :param config: Paramorph specific config options.
        :param callbacks: Callbacks used by Paramorph to set hyperparameters and other miscellaneous tasks.
        """

        self._step = 0
        self._current_epoch = 0

        self._loss_cache: list[float] = []

        self.config = config
        self.paramorph = Paramorph(
            model=model,
            optimizer=optimizer,
            config=config,
            callbacks=callbacks,
        )

    def cache_loss(self, loss: float) -> None:
        """
        :param loss: Loss to cache in the callback.
        """

        self._loss_cache.append(loss)

    def on_optimizer_step(
        self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs
    ) -> None:
        """
        :param args: TrainingArguments used by the Huggingface Trainer.
        :param state: State of the training loop in the Huggingface Trainer.
        :param control: Controller which controls the flow through the training loop in the HuggingfaceTrainer.
        :param kwargs: Other keyword arguments from the callback controller.
        """

        self._step += 1

        if not self._step % self.config.scheduling_config.tuning_frequency:
            training_loss = sum(self._loss_cache) / len(self._loss_cache)
            self._loss_cache = []

        else:
            training_loss = self._loss_cache[-1]

        current_epoch = int(state.epoch)

        self.paramorph.step(
            training_loss=training_loss,
            training_progress=state.epoch / args.num_train_epochs,
            current_epoch=current_epoch,
        )
