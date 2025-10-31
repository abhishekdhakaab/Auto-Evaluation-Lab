import matplotlib.pyplot as plt
from core.memory import load_index


def plot_accuracy_trend():
    runs = load_index()
    if not runs:
        print("No data to plot.")
        return
    xs = list(range(1, len(runs) + 1))
    ys = [r["accuracy"] for r in runs]
    plt.plot(xs, ys, marker="o")
    plt.title("AutoEval Accuracy Trend")
    plt.xlabel("Run #")
    plt.ylabel("Accuracy")
    plt.grid(True)
    out_path = "experiments/accuracy_trend.png"
    plt.savefig(out_path)
    print(f"Saved plot to {out_path} ({len(runs)} runs).")
    # Show only if an interactive backend is available
    try:
        plt.show()
    except Exception:
        pass
    finally:
        plt.close()


if __name__ == "__main__":
    plot_accuracy_trend()