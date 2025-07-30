# DMRG Task Client

A Python client for submitting calculation tasks to a server and polling results.

## Installation

```bash
pip install qumulator
```

## Usage Example

```python
from entropec_quantumoperator_test import DMRGClient

# Initialize client with server URL
client = DMRGClient(api_base="http://192.168.124.22:12805")

def main():
    # 初始化客户端
    client = DMRGClient(
        api_base="http://192.168.124.22:12805",  # 服务地址
        timeout=1000,  # 超时时间（秒）
        retry_interval=5  # 结果轮询间隔（秒）
    )

    # 任务参数
    task_id = "test_task_001"  # 使用唯一实例ID
    program = " vmps1FM"  # 选择调用的程序
    # program = "measureSC"  # 选择调用的程序
    params = {
        "CaseParams": {
            "Geometry": "OBC",
            "Lx": 3,
            "Ly": 4,
            "t": 1.0,
            "t2": -0.2,
            "J": 3.0,
            "J2": 1.0,
            "phi": 0.1,
            "mu": 0,
            "NumHole": 2,
            "Sweeps": 5,
            "Dmin": 10,
            "Dmax": 10,
            "CutOff": 1e-9,
            "LanczErr": 1e-9,
            "MaxLanczIter": 70,
            "Threads": 2,
            "noise": [0.1, 0.01],
            "Perturbation": 0.0,
            "BondSingletPairPerturbation": 0.0,
            "wavelength": 4
        }
    }


    try:
        # 提交任务
        print("提交测试任务...")
        response = client.submit_job(task_id, program, params)
        print(f"提交响应: {response}")

        # 获取结果（限制重试次数，避免无限等待）
        print("获取测试结果...")
        result = client.fetch_result(task_id, max_retries=5)
        print(f"测试结果: {result}")  # 打印部分结果

    except Exception as e:
        print(f"测试失败: {str(e)}")


if __name__ == "__main__":
    main()
```

## API Reference

### DMRGClient

#### `__init__(api_base, timeout=10, retry_interval=5)`
Initialize a new DMRG client.

- `api_base`: Base URL of the DMRG server
- `timeout`: Request timeout in seconds (default: 10)
- `retry_interval`: Interval between result polling attempts (default: 5)

#### `submit_job(task_id, program, params)`
Submit a DMRG calculation task.

- `task_id`: Unique identifier for the task
- `program`: The program to execute (e.g., "vmps1FM" or "measureSC")
- `params`: Dictionary containing calculation parameters
- Returns: Server response JSON

#### `fetch_result(task_id, max_retries=None)`
Poll for calculation results.

- `task_id`: Task identifier to fetch results for
- `max_retries`: Maximum number of retries (None for infinite)
- Returns: Calculation result text

## License
MIT License