# Automated Optical Fiber Characterization System

A system for automated characterization of optical fibers, measuring attenuation, dispersion, refractive index, and geometric parameters through integrated hardware control and Image analysis.

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Key Features](#key-features)
3. [Class Diagram](#class-diagram)
4. [Data Flow](#data-flow)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Usage](#usage)
8. [Results](#results)

----
### Demo & Screenshots

![Sceenshot](https://github.com/user-attachments/assets/29c7f06f-2ad2-4e55-b0a1-5fc9ba52a9ee)
<video src="https://github.com/user-attachments/assets/c9e06946-06a4-46e9-a20b-86371c6b175e" title="Demo video"></video>

----
## System Architecture

```mermaid
graph TD
    A[Hardware] --> B(Laser Controller)
    A --> C(Photodetector)
    A --> D(Alignment Stage)
    B --> E[Core System]
    C --> E
    D --> E
    E --> F[Data Acquisition]
    E --> G[Signal Processing]
    E --> H[Image Analysis]
    F --> I[(Database)]
    G --> I
    H --> I
    I --> J[Dashboard]
    J --> K[Real-time Visualization]
    J --> L[Reports]
```

## Key Features

- **Multi-parameter Measurement**
- **Automated Fiber Alignment**
- **Real-time Spectral Analysis**
- **AI-powered Defect Detection**
- **Professional Reporting**

## Class Diagram

```mermaid
classDiagram
    class FiberCharacterizationSystem{
        -LaserController laser
        -Photodetector detector
        -AlignmentSystem alignment
        +run_full_characterization()
        +analyze_fiber_image()
        +shutdown()
    }

    class LaserController{
        -visa_address: str
        -current_wavelength: float
        +set_wavelength()
        +get_power()
    }

    class FiberAnalyzer{
        -original_image: ndarray
        -processed_image: ndarray
        +detect_core_cladding()
        +calculate_mfd()
        +refractive_index_profile()
    }

    class SignalProcessor{
        +calculate_attenuation()
        +analyze_dispersion()
        +noise_analysis()
    }

    FiberCharacterizationSystem --> LaserController
    FiberCharacterizationSystem --> Photodetector
    FiberCharacterizationSystem --> FiberAnalyzer
    FiberCharacterizationSystem --> SignalProcessor
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Dashboard
    participant CoreSystem
    participant Hardware

    User->>Dashboard: Start Characterization
    Dashboard->>CoreSystem: Initialize Parameters
    CoreSystem->>Hardware: Align Fiber
    Hardware-->>CoreSystem: Alignment Status
    CoreSystem->>Hardware: Spectral Sweep
    Hardware-->>CoreSystem: Power Measurements
    CoreSystem->>SignalProcessor: Analyze Data
    SignalProcessor-->>CoreSystem: Attenuation/Dispersion
    CoreSystem->>Database: Store Results
    Database-->>Dashboard: Update Visualization
```

## Installation

### Requirements
- Python 3.9+
- NI-VISA Drivers
- OpenCV with Contrib Modules

```bash
git clone https://github.com/FakeCoder01/fiber-characterization-system.git
cd fiber-characterization-system
pip install -r requirements.txt
```

## Configuration

Edit `src/config/config.yaml`:
```yaml
hardware:
  laser:
    visa_address: GPIB0::12::INSTR
    min_wavelength: 1500
    max_wavelength: 1600
  detector:
    visa_address: GPIB0::15::INSTR

acquisition:
  interval: 0.1  # seconds
  sampling_rate: 1000  # Hz

analysis:
  core_threshold: 0.7
  cladding_threshold: 0.3
```

## Usage


### Dashboard
```bash
cd src/
python app.py
```
#### Serer started at : `http://localhost:8050`
------


## Results

### Typical Outputs

**Spectral Response**
```mermaid
graph LR
    A[1550 nm] --> B(Peak Power)
    C[1565 nm] --> D(3dB Roll-off)
```

**MFD Measurement**
```mermaid
pie title Mode Field Diameter
    "Core" : 8.2
    "Cladding" : 125
```

**Attenuation Curve**
```mermaid
graph TD
    A[0 km] -->|0.2 dB/km| B[5 km]
    B -->|0.22 dB/km| C[10 km]
    C -->|0.25 dB/km| D[15 km]
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Hardware Connection Failed | Check VISA addresses and cables |
| Image Analysis Failure | Verify fiber is centered in image |
| Signal Noise Too High | Clean connectors, check laser stability |
