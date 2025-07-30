"""
visualization.py
Creates and saves training history charts.
"""

import matplotlib.pyplot as plt
import os

def plot_training_history(history, output_path):
    """
    Plots loss and accuracy curves and saves as PNG.

    Args:
        history: Keras History object
        output_path: path to save the plot (e.g. 'echo_reports/training.png')
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    metrics = history.history
    epochs = range(1, len(metrics['loss']) + 1)

    plt.figure(figsize=(10, 4))
    # Loss
    plt.subplot(1, 2, 1)
    plt.plot(epochs, metrics['loss'], 'bo-', label='Training Loss')
    plt.plot(epochs, metrics.get('val_loss', []), 'ro-', label='Validation Loss')
    plt.title('Loss over Epochs')
    plt.xlabel('Epoch')
    plt.legend()

    # Accuracy
    plt.subplot(1, 2, 2)
    plt.plot(epochs, metrics.get('accuracy', []), 'bo-', label='Training Acc')
    plt.plot(epochs, metrics.get('val_accuracy', []), 'ro-', label='Validation Acc')
    plt.title('Accuracy over Epochs')
    plt.xlabel('Epoch')
    plt.legend()

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"📊 Plot saved to {output_path}")
