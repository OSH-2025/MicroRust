import time
import numpy as np
import ray

# ---- Ray远程函数，用于 Dashboard 观察 ---- #
@ray.remote
def forward_remote(x, weights):
    for w in weights:
        x = np.dot(x, w)
        x = np.maximum(x, 0)  # ReLU
    return np.sum(x)  # 做个聚合避免优化掉

# ---- 初始化网络参数 ---- #
def generate_weights(layers):
    return [np.random.randn(layers[i], layers[i + 1]) for i in range(len(layers) - 1)]

# ---- 大数据生成函数 ---- #
def generate_inputs(num_batches, input_size):
    return [np.random.randn(input_size) for _ in range(num_batches)]

# ---- 执行分布式前向传播任务 ---- #
def run_distributed(num_batches=20, input_size=100, layers=[1000, 1000, 1000, 1000]):
    print(f"🧠 准备执行 {num_batches} 批任务，每批输入 {input_size} 个特征...")

    weights = generate_weights([input_size] + layers)
    inputs = generate_inputs(num_batches, input_size)

    print(f"🚀 分布式执行中...可用CPU: {ray.available_resources().get('CPU', '未知')}，节点数: {len(ray.nodes())}")

    start = time.time()
    futures = [forward_remote.remote(x, weights) for x in inputs]
    ray.get(futures)
    end = time.time()

    print(f"✅ 完成。耗时: {end - start:.2f} 秒")

# ---- 主函数 ---- #
if __name__ == "__main__":
    ray.init(address="auto")  # 连接已有集群（主从结构）
    run_distributed()