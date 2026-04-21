"""A toy training script to be driven by KohakuEngine configs."""

# Default globals. KohakuEngine config will override these.
run_name = "default"
learning_rate = 0.001
batch_size = 32
epochs = 3
activation = lambda x: x


def train():
    print(f"[train_task] run={run_name} lr={learning_rate} bs={batch_size} epochs={epochs}")
    values = [-1.0, 0.0, 2.0]
    transformed = [activation(v) for v in values]

    loss = 1.0
    for _ in range(epochs):
        loss *= 0.8

    result = {
        "run_name": run_name,
        "final_loss": round(loss, 4),
        "activation_preview": transformed,
    }
    print(f"[train_task] result={result}")
    return result


if __name__ == "__main__":
    train()
