# Syndrilla
A PyTorch-based numerical simulator for decoders in quantum error correction.

## Installation
All provided installation methods allow running ```syndrilla``` in the command line and ```import syndrilla``` as a python module.

Make sure you have [Anaconda](https://www.anaconda.com/) installed before the steps below.

### Option 1: pip installation
1. ```git clone``` [this repo](https://github.com/UnaryLab/syndrilla) and ```cd``` to the repo dir.
2. ```conda env create -f environment.yaml```
   - The ```name: syndrilla``` in ```evironment.yaml``` can be updated to a preferred one.
3. ```conda activate syndrilla```
4. ```pip install syndrilla```
5. Validate installation via ```syndrilla -h``` in the command line or ```import syndrilla``` in python code
   - If you want to validate the simulation results against BPOSD, you need to change python to version 3.10. Then install [BPOSD](https://github.com/quantumgizmos/bp_osd) and run ```python tests/validate_bposd.py```

### Option 2: source installation
This is the developer mode, where you can edit the source code with live changes reflected for simulation.
1. ```git clone``` [this repo](https://github.com/UnaryLab/syndrilla) and ```cd``` to the repo dir.
2. ```conda env create -f environment.yaml```
   - The ```name: syndrilla``` in ```evironment.yaml``` can be updated to a preferred one.
3. ```conda activate syndrilla```
4. ```python3 -m pip install -e . --no-deps```
5. Validate installation via ```syndrilla -h``` in the command line or ```import syndrilla``` in python code

## Simulation results
We show some of the simulation results as below.

GPUs: AMD Insticnt MI210, NVIDIA A100, NVIDIA H200

CPU: Intel i9-13900K

### Comparison across GPUs
<table>
  <tr>
    <td align="center">
      <img src="zoo/speedup/accuracy_gpu.png" width="240"><br>Accuracy
    </td>
    <td align="center">
      <img src="zoo/speedup/time_gpu.png" width="240"><br>Time
    </td>
  </tr>
</table>


### Comparison across data formats
<table>
  <tr>
    <td align="center">
      <img src="zoo/speedup/accuracy_data_format.png" width="240"><br>Accuracy
    </td>
    <td align="center">
      <img src="zoo/speedup/time_data_format.png" width="240"><br>Time
    </td>
  </tr>
</table>


### Comparison across distances
<table>
  <tr>
    <td align="center">
      <img src="zoo/speedup/accuracy_distance.png" width="240"><br>Accuracy
    </td>
    <td align="center">
      <img src="zoo/speedup/time_distance.png" width="240"><br>Time
    </td>
  </tr>
</table>


### Comparison across batch sizes and against CPU
<table>
  <tr>
    <td align="center">
      <img src="zoo/speedup/time_batch.png" width="240"><br>Time
    </td>
    <td align="center">
      <img src="zoo/speedup/time_cpu_speedup.png" width="240"><br>Speedup over CPU
    </td>
  </tr>
</table>
