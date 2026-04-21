"""KohakuEngine config demo: from_globals + use + generator sweep."""

from kohakuengine import Config, use


# A callable that we want to inject into target script globals.
def relu(x):
    return x if x > 0 else 0.0


# --- Single-run config (recommended style) ---
run_name = "single_from_globals"
learning_rate = 0.01
batch_size = 16
epochs = 4
activation = use(relu)  # include function in Config.from_globals()


def config_gen():
    """Used by Config.from_file(...)."""
    return Config.from_globals()


# --- Multi-run config generator (hyper-parameter sweep) ---
def sweep_config_gen():
    for lr in [0.001, 0.01]:
        for bs in [8, 32]:
            yield Config(
                globals_dict={
                    "run_name": f"sweep_lr{lr}_bs{bs}",
                    "learning_rate": lr,
                    "batch_size": bs,
                    "epochs": 3,
                },
                metadata={"lr": lr, "bs": bs},
            )
