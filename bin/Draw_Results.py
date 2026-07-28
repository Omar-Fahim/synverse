import re
import matplotlib.pyplot as plt



# a script to plot the training and validation loss from the log file of the training process. 

# Path to your log file
log_file = "/home/omar/projects/nf-core-synverse/results/trainandeval/results/k_0.05_S_mean_mean/leave_comb/run_1_6/D_smiles_Transformer_Berttokenizer_C_genex_std_shuffled_0_training_final.log"

# Lists to store values
epochs_train = []
train_losses = []

epochs_val = []
val_losses = []

# Read file
with open(log_file, "r") as f:
    lines = f.readlines()

# Parse the file
for line in lines:

    # Match train loss
    train_match = re.search(r"e (\d+): train_loss: ([\d\.]+)", line)
    if train_match:
        epoch = int(train_match.group(1))
        loss = float(train_match.group(2))

        epochs_train.append(epoch)
        train_losses.append(loss)
        print(f"Epoch {epoch}: Train Loss = {loss}")

    # Match validation loss
    val_match = re.search(r"e (\d+): val_loss: ([\d\.]+)", line)
    if val_match:
        epoch = int(val_match.group(1))
        loss = float(val_match.group(2))

        epochs_val.append(epoch)
        val_losses.append(loss)

# Plot
plt.figure(figsize=(10, 6))

plt.plot(
    epochs_train,
    train_losses,
    marker='o',
    label='Train Loss'
)

plt.plot(
    epochs_val,
    val_losses,
    marker='s',
    label='Validation Loss'
)


plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("Training and Validation Loss")

plt.grid(True)
plt.legend()


plt.show()