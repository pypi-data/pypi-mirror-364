i  # 10_target_navigation_with_preprocessing.py
"""
Demonstrates a modular agent controlled by ParaComposite.

The agent receives a 2D vector input (relative target position) and uses:
- para[0]: a ParaVector for preprocessing (linear scaling of input)
- para[1]: a ParaNet to decide movement direction based on preprocessed input

The task: Navigate towards a target at (1, 1) from origin (0, 0).
"""

import matplotlib.pyplot as plt
import numpy as np

from evolib import Indiv, Pop, mse_loss
from evolib.representation.composite import ParaComposite
from evolib.representation.paranet import ParaNet
from evolib.representation.vector import ParaVector

TARGET = np.array([1.0, 1.0])
START = np.array([0.0, 0.0])
NUM_STEPS = 10
STEP_SIZE = 0.1


# Create ParaNet model for directional control
controller = ParaNet(input_dim=2, hidden_dim=4, output_dim=2, activation="tanh")


def modular_fitness(indiv: Indiv) -> None:
    """Fitness = distance to target after NUM_STEPS steps."""
    pos = START.copy()
    trajectory = [pos.copy()]

    for _ in range(NUM_STEPS):
        raw = TARGET - pos
        scaled = raw * indiv.para[0].vector  # Elementwise scaling via ParaVector
        move = controller.forward(scaled, indiv.para[1].vector)
        pos += STEP_SIZE * np.tanh(move)
        trajectory.append(pos.copy())

    distance = np.linalg.norm(pos - TARGET)
    indiv.fitness = distance
    indiv.extra_metrics = {"final_x": pos[0], "final_y": pos[1]}


# Setup Pop with modular ParaComposite
pop = Pop("configs/10_target_nav.yaml")
pop.set_functions(fitness_function=modular_fitness)

for _ in range(pop.max_generations):
    pop.run_one_generation(sort=True)

# Visualization
best = pop.best()

pos = START.copy()
trajectory = [pos.copy()]
for _ in range(NUM_STEPS):
    raw = TARGET - pos
    scaled = raw * best.para[0].vector
    move = controller.forward(scaled, best.para[1].vector)
    pos += STEP_SIZE * np.tanh(move)
    trajectory.append(pos.copy())

traj = np.array(trajectory)
plt.plot(traj[:, 0], traj[:, 1], marker="o", label="Agent Path")
plt.scatter(*TARGET, color="red", label="Target")
plt.scatter(*START, color="green", label="Start")
plt.title("Target Navigation with Preprocessing")
plt.legend()
plt.grid()
plt.axis("equal")
plt.show()
