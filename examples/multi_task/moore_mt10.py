from dataclasses import dataclass
from pathlib import Path

import tyro

from metaworld_algorithms.config.networks import (
    ContinuousActionPolicyConfig,
    QValueFunctionConfig,
)
from metaworld_algorithms.config.nn import MOOREConfig
from metaworld_algorithms.config.optim import OptimizerConfig
from metaworld_algorithms.config.rl import OffPolicyTrainingConfig
from metaworld_algorithms.envs import MetaworldConfig
from metaworld_algorithms.rl.algorithms import MTSACConfig
from metaworld_algorithms.run import Run


@dataclass(frozen=True)
class Args:
    seed: int = 1
    track: bool = False
    wandb_project: str | None = None
    wandb_group: str | None = None
    wandb_entity: str | None = None
    data_dir: Path = Path("./run_results")
    resume: bool = False


def main() -> None:
    args = tyro.cli(Args)

    run = Run(
        run_name="mt10_moore",
        seed=args.seed,
        data_dir=args.data_dir,
        env=MetaworldConfig(
            env_id="MT10",
            terminate_on_success=False,
        ),
        algorithm=MTSACConfig(
            num_tasks=10,
            gamma=0.99,
            actor_config=ContinuousActionPolicyConfig(
                network_config=MOOREConfig(
                    num_tasks=10, optimizer=OptimizerConfig(lr=3e-4, max_grad_norm=1.0)
                ),
                log_std_min=-10,
                log_std_max=2,
            ),
            critic_config=QValueFunctionConfig(
                network_config=MOOREConfig(
                    num_tasks=10,
                    optimizer=OptimizerConfig(lr=3e-4, max_grad_norm=1.0),
                )
            ),
            temperature_optimizer_config=OptimizerConfig(lr=1e-4),
            num_critics=2,
        ),
        training_config=OffPolicyTrainingConfig(
            total_steps=int(2e6),
            buffer_size=int(1e6),
            batch_size=1280,
        ),
        checkpoint=True,
        resume=args.resume,
    )

    if args.track:
        assert args.wandb_project is not None
        run.enable_wandb(
            project=args.wandb_project,
            entity=args.wandb_entity,
            config=run,
            resume="allow",
            group=args.wandb_group
        )

    run.start()


if __name__ == "__main__":
    main()
