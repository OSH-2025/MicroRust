import ray
import numpy as np
import time

# Define the Sigmoid function
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# A Random-parameter Neural Network
class fake_NN:
    def __init__(self):
        self.W1 = np.random.rand(1000, 1000)
        self.B1 = np.random.rand(1000)
        self.W2 = np.random.rand(1000, 1000)
        self.B2 = np.random.rand(1000)
        self.W3 = np.random.rand(1000, 1000)
        self.B3 = np.random.rand(1000)

    def forward(self, input):
        x = sigmoid(input @ self.W1 + self.B1)
        x = sigmoid(x @ self.W2 + self.B2)
        x = sigmoid(x @ self.W3 + self.B3)
        return x

    def forwards(self, inputs):
        result = []
        for input in inputs:
            result.append(self.forward(input))
        return result

# Ray Distributed Actor
@ray.remote
class Actor:
    def __init__(self):
        self.model = fake_NN()

    def predict(self, inputs):
        return self.model.forwards(inputs)

# Initialize Ray
ray.init(address='auto', dashboard_host="0.0.0.0")

# Task parameters
task_num = 100000
batch_size = 10

# Initialize actors
actor_num = 10
actors = [Actor.remote() for _ in range(actor_num)]

# Start timer
start_timer = time.time()

# Distribute tasks
tasks = []
for i in range(task_num // batch_size):
    inputs = [np.random.rand(1000) for _ in range(batch_size)]
    tasks.append(actors[i % actor_num].predict.remote(inputs))

# Get results
results = ray.get(tasks)

# Print time used
print(f"Time used: {time.time() - start_timer:.2f} seconds")

# Shutdown Ray
ray.shutdown()#这是一个神经网络，用的sigmod函数，多参数从而保证必然是计算密集型