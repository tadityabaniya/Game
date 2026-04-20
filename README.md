# Rapid Bridge Construction

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Rapid Bridge Construction** is a high-stakes industrial simulation game built with Python. As a lead engineer, your mission is to rebuild a critical bridge on Nepal's Mahendra Highway that was destroyed by a massive flood. You must balance time, cost, and logistics to deliver the project with maximum efficiency.

---

## 🏗️ The Mission
A 20m bridge connecting the Mahendra Highway at Chitawan has been severely damaged. So, new bridge must be built with optimum efficiency where performance of construction is evaluated using a weighted efficiency model, where 65% importance is given to time and 35% to cost.

### Sourcing Strategy
You will require 40 tonnes of steel. Construction takes 24 hours if materials are available. Strategically allocate the material percentages from all three locations. Remember that the percentage of material sourced directly dictates the percentage of construction work completed. Your goal is to optimize the distribution to attain maximum efficiency You have three primary supply depots, each with different costs and transit delays:
- **Chitawan (Local)**: $1,000/ton | **Instant Delivery**
- **Dang**: $980/ton | **8-Hour Delay**
- **Kanchanpur**: $960/ton | **16-Hour Delay**

*Your goal: Optimize the allocation to minimize total construction time while keeping costs within budget.*

---

## 🕹️ Project Phases

1. **Authentication**: Secure login and identification.
2. **Mission Briefing**: Interactive chatbot interface with Mission Control via customized communication protocols.
3. **Logistics Planning**: Use a real-time map of Nepal and balancing sliders to allocate materials across the three depots.
4. **Live Simulation**: Watch the construction unfold on a geographic layout. Track shipments in transit and monitor build progress in real-time.
5. **Performance Evaluation**: A data-driven dashboard that scores your performance based on a **Multi-Criteria Decision Analysis (MCDA)** algorithm (65% Time, 35% Cost).

---

## 🛠️ Technology Stack

This application utilizes a modern, industrial-themed UI built with:
- **[Pygame](https://www.pygame.org/)**: Handles the high-performance simulation engine and login screens.
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)**: Provides a sleek, dark-themed dashboard and chatbot interface.
- **[Matplotlib](https://matplotlib.org/)**: Generates dynamic performance reports and comparative analytics.
- **[Pillow (PIL)](https://python-pillow.org/)**: Handles geographic map rendering and asset processing.

---

## 🚀 Getting Started

### Prerequisites
Ensure you have Python 3.8+ installed. You will need to install the following dependencies:

```bash
pip install pygame customtkinter matplotlib pillow
```

### Installation
1. Clone this repository (or download the source files).
2. Ensure `nepal_map.png` and `bg_fixed.jpg` are in the same directory as the script.
3. Run the application:

```bash
python rapid_bridge_run.py
```

---

## 📊 Scoring & Analytics
The **Performance Evaluator** compares your strategy against the "Theoretically Ideal" allocation. 
- **Time Score**: Rewarded for hitting the 24-hour minimum build floor.
- **Cost Score**: Rewarded for leveraging cheaper materials without stalling the site.
- **Final Grade**: Distributed from "Elite Engineer" to "In-Training" based on your resource management skills.

---

## 📜 License
This project is licensed under the MIT License. Feel free to use and modify it for educational and simulation purposes.
