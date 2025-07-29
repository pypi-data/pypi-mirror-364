# General Specifications

## 1. Configuration

  - Server: 2.0 GHz, 2 GB, 1 Gbps
  - Dataset: CIFAR-10 (Train size: 50000 / Test size: 10000)
  - Partitions: 64
  - Model: CNN3
  - Optimizer: SGD (Learning rate: 0.01)
  - Aggregation Function: FedAvg
  - Batch Size: 16
  - Local Epochs: 2
  - Global Rounds: 500

## 2. Data Partitioning Strategies

### IID

  ![IID Partitioning](./images/CIFAR10-IID.png)

### Non-IID (Dirichlet, α = 1.0)

  ![Non-IID Partitioning](./images/CIFAR10-Non-IID.png)

### Extreme Non-IID (Dirichlet, α = 0.1)

  ![Extreme Non-IID](./images/CIFAR10-Extreme-Non-IID.png)

# Experiment Specifications

## 1. Resources

### 1.1 Device Allocation

#### 1.1.1

  - Devices: 8 × Raspberry Pi 3 (1.2 GHz, 1 GB)
  - Bandwidth: 100 Mbps
  - Partitioning: IID

#### 1.1.2

  - Devices: 16 × Raspberry Pi 3 (1.2 GHz, 1 GB)
  - Bandwidth: 100 Mbps
  - Partitioning: IID

#### 1.1.3

  - Devices: 32 × Raspberry Pi 3 (1.2 GHz, 1 GB)
  - Bandwidth: 100 Mbps
  - Partitioning: IID

#### 1.1.4

  - Devices: 64 × Raspberry Pi 3 (1.2 GHz, 1 GB)
  - Bandwidth: 100 Mbps
  - Partitioning: IID

### 1.2 Network Bandwidth

#### 1.2.1

  - Devices: 32 × Raspberry Pi 3 (1.2 GHz, 1 GB)
  - Bandwidth: 50 Mbps
  - Partitioning: IID

#### 1.2.2

  - Devices: 32 × Raspberry Pi 3 (1.2 GHz, 1 GB)
  - Bandwidth: 25 Mbps
  - Partitioning: IID

## 2. Heterogeneity

### 2.1 Device Heterogeneity
 
#### 2.1.1

  - Devices: 16 × Raspberry Pi 3 (1.2 GHz, 1 GB)
  - Devices: 16 × Raspberry Pi 4 (1.5 GHz, 4 GB)
  - Bandwidth: 100 Mbps (Raspberry Pi 3)
  - Bandwidth: 1 Gbps (Raspberry Pi 4)
  - Partitioning: IID

#### 2.1.2

  - Devices: 32 × Raspberry Pi 4 (1.5 GHz, 4 GB)
  - Bandwidth: 1 Gbps (Raspberry Pi 4)
  - Partitioning: IID

### 2.2 Data Heterogeneity

#### 2.2.1

  - Devices: 32 × Raspberry Pi 4 (1.5 GHz, 4 GB)
  - Bandwidth: 1 Gbps
  - Partitioning: Non-IID (Dirichlet, α = 1.0)

#### 2.2.2
  
  - Devices: 32 × Raspberry Pi 4 (1.5 GHz, 4 GB)
  - Bandwidth: 1 Gbps
  - Partitioning: Extreme Non-IID (Dirichlet, α = 0.1)
