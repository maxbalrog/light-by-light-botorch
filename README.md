# light-by-light-botorch
Optimization of light-by-light scattering scenarios with BoTorch engine.

## Installation
Create conda environment (some packages require python <= 3.10)
```bash
conda create -n lbl-botorch python=3.10
conda activate lbl-botorch
```
Install standard packages
```bash
conda install numpy cython matplotlib scipy tqdm numexpr
```
Install postpic, pyfftw and vacem packages (postpic and vacem should be cloned from git beforehand)
```bash
pip install -e packages/postpic
conda install -c conda-forge pyfftw=0.12.0
pip install -e packages/vacem-master
```
Install our light-by-light package
```bash
pip install -e light-by-light
```
Install botorch
```bash
pip install botorch
```



