# ProFed: A Benchmark for Proximity-based Federated Learning

**🔗 ProFed: A Benchmark for Proximity‑based Non‑IID Federated Learning**

ProFed is a framework for evaluating federated learning (FL) systems under *realistic*, geographically clustered, non‑IID data scenarios. It simulates clients grouped into regions such that data is IID *within* regions but non‑IID *across* regions.

---

## 🚀 Features

- **Built‑in datasets**: Support for MNIST, FashionMNIST, CIFAR‑10, CIFAR‑100 and UTKFace via PyTorch/TorchVision.
- **Flexible partitioning**: Implements Dirichlet-based splits, hard label skews, and can model arbitrary proximity-driven distribution skews.
- **Customizable proximity modeling**: Define how many geographic clusters (regions) to simulate and control skew intensity (e.g., Dirichlet α).

---

## 🔧 Getting Started

### Prerequisites

- Python ≥ 3.12

### Installation

ProFed is [publicly released on PyPi](https://pypi.org/project/ProFed/), to install ProFed on your machine:

```bash
pip install ProFed
```

## API Explanation

### 1. Downloading and importing the dataset
```python
train_data, test_data = download_dataset('EMNIST')
```

### 2. Splitting into train & validation sets
```python
train_data, validation_data = split_train_validation(train_data, 0.8)
```

### 3. Partitioning into geographic “regions” (i.i.d. internally)
```python
environment = partition_to_subregions(
    train_data,
    validation_data,
    partitioning_method = 'Hard',
    number_subregions = 5,
    seed = 42
)
```

- method: partition strategy ('Hard', 'Dirichlet', or 'IID')

- number_subregions: how many simulated geographic clusters

- Returns an Environment object. Each region within it contains IID data internally, but non-IID across regions.

### 1. Distributing region data across devices
```python
mapping = {}
for region_id, devices in mapping_devices_area.items():
    mapping_devices_data = environment.from_subregion_to_devices(
        region_id,
        len(devices)
    )
    for device_index, data in mapping_devices_data.items():
        device_id = devices[device_index]
        mapping[device_id] = data
```
Splits the region’s IID data equally among its devices, assigning each a local subset.

The result is a mapping:

```python
device_id → local_dataset
```

## 📄 License 
MIT License — feel free to freely use, modify, and distribute.

## 📬 Contact
For questions, issues, or contributions, feel free to reach out:

- **Author**: Davide Domini  
- **Email**: davide.domini@unibo.it  
- **GitHub**: [davidedomini](https://github.com/davidedomini)

You can also open an [issue](https://github.com/davidedomini/ProFed/issues) or submit a pull request on GitHub!

