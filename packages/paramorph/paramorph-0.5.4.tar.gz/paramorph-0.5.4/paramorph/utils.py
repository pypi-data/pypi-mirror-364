# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from libinephany.pydantic_models.configs.hyperparameter_configs import HParamConfig, HParamConfigs
from libinephany.pydantic_models.states.hyperparameter_states import Hyperparameter, HyperparameterStates
from libinephany.utils import agent_utils, enums
from libinephany.utils.constants import (
    AGENT_PREFIX_BETA_ONE,
    AGENT_PREFIX_BETA_TWO,
    AGENT_PREFIX_CLIPPING,
    AGENT_PREFIX_DROPOUT,
    AGENT_PREFIX_EPS,
    AGENT_PREFIX_LR,
    AGENT_PREFIX_WD,
)

from paramorph.paramorph_config import ParamorphConfig

# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def _add_new_agent_ids(current_ids: set[str], agent_prefix: str, agent_modules: dict[str, str]) -> set[str]:
    """
    :param current_ids: Current set of agent IDs.
    :param agent_prefix: Prefix given to the agent type being created.
    :param agent_modules: Dictionary mapping modules in the target NN to the type of those modules.
    :return: Updated set of agent IDs.
    """

    for module_name in agent_modules:
        current_ids.add(agent_utils.create_agent_id(layer_name=module_name, prefix=agent_prefix, suffix=None))

    return current_ids


def create_agent_ids(paramorph_config: ParamorphConfig) -> set[str]:
    """
    :param paramorph_config: ParamorphConfig used to form the agent IDs determined by which agents are active.
    :return: Set of agent IDs.
    """

    agent_modules = paramorph_config.agent_modules
    agent_ids: set[str] = set()

    if paramorph_config.agent_config.use_learning_rate_agents:
        agent_ids = _add_new_agent_ids(current_ids=agent_ids, agent_prefix=AGENT_PREFIX_LR, agent_modules=agent_modules)

    if paramorph_config.agent_config.use_weight_decay_agents:
        agent_ids = _add_new_agent_ids(current_ids=agent_ids, agent_prefix=AGENT_PREFIX_WD, agent_modules=agent_modules)

    if paramorph_config.agent_config.use_dropout_agents:
        agent_ids = _add_new_agent_ids(
            current_ids=agent_ids, agent_prefix=AGENT_PREFIX_DROPOUT, agent_modules=agent_modules
        )

    if paramorph_config.agent_config.use_grad_clip_agents:
        agent_ids = _add_new_agent_ids(
            current_ids=agent_ids, agent_prefix=AGENT_PREFIX_CLIPPING, agent_modules=agent_modules
        )

    if paramorph_config.agent_config.use_adam_beta_one_agents:
        agent_ids = _add_new_agent_ids(
            current_ids=agent_ids, agent_prefix=AGENT_PREFIX_BETA_ONE, agent_modules=agent_modules
        )

    if paramorph_config.agent_config.use_adam_beta_two_agents:
        agent_ids = _add_new_agent_ids(
            current_ids=agent_ids, agent_prefix=AGENT_PREFIX_BETA_TWO, agent_modules=agent_modules
        )

    if paramorph_config.agent_config.use_adam_eps_agents:
        agent_ids = _add_new_agent_ids(
            current_ids=agent_ids, agent_prefix=AGENT_PREFIX_EPS, agent_modules=agent_modules
        )

    return agent_ids


def create_hyperparameter_config_mapping(
    agent_ids: set[str],
    hyperparameter_configs: HParamConfigs,
) -> dict[str, HParamConfig]:
    """
    :param agent_ids: Set of agent IDs to create hyperparameter config mapping for.
    :param hyperparameter_configs: Config of all hyperparameters.
    :return: Dictionary mapping agent IDs to the HParamConfig for the hyperparameter that agent controls.
    """

    return {
        agent_id: hyperparameter_configs.get_hyperparameter_config_from_agent_type(
            agent_type=enums.AgentTypes(agent_utils.extract_agent_type(agent_id=agent_id))
        )
        for agent_id in agent_ids
    }


def create_hyperparameter_mapping(
    agent_ids: set[str], hyperparameter_states: HyperparameterStates
) -> dict[str, Hyperparameter]:
    """
    :param agent_ids: Set of agent IDs to create hyperparameter mapping for.
    :param hyperparameter_states: Object that maintains the states of all hyperparameters.
    :return: Dictionary mapping agent IDs to the hyperparameter that agent controls.
    """

    hyperparameter_mapping: dict[str, Hyperparameter] = {}

    for agent_id in agent_ids:
        parameter_group_name = agent_utils.extract_parameter_group_name(agent_id=agent_id)
        agent_type = agent_utils.extract_agent_type(agent_id=agent_id)
        group_hparams = hyperparameter_states[parameter_group_name]
        hyperparameter = group_hparams.get_hyperparameter_by_name(name=enums.AgentTypes(agent_type))

        hyperparameter_mapping[agent_id] = hyperparameter

    return hyperparameter_mapping
