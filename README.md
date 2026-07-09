# 🚀 lunar-soft-landing-control 🌕

**A numerical simulation suite and solver for determining the optimal trajectory for a spacecraft's soft landing on the Moon.**

This project solves the boundary value problem (BVP) of optimal control for a soft lunar landing maneuver. Based on Pontryagin's Maximum Principle, the system calculates the exact engine switching time ($t_s$) and generates comprehensive graphs of the spacecraft's phase trajectories, mass flow, velocity, and altitude profiles.

---

## 🔬 Mathematical Engine (Implemented From Scratch)

To ensure maximum accuracy and eliminate discretization errors, all numerical methods were implemented manually without high-level external libraries:
*   **The Shooting Method:** Translates the BVP into a sequence of Cauchy problems, using the engine activation time as the shooting parameter.
*   **Vector RK4 Integrator:** Integrates system differential equations during active braking with $O(\Delta t^4)$ global truncation error.
*   **Hybrid Root-Finder:** A modified bisection algorithm using a sign-change criterion to precisely localize the root of the smooth height residual function.


---

## 👥 R&D Collaboration & My Role

This project is a co-authored research and development work conducted alongside a research advisor. 
*   **My Core Contribution:** I performed the theoretical analysis of numerical sloving of the control problem, designed the mathematical groundwork, and developed the entire numerical simulation pipeline and code from scratch in Python.
*   **Advisor's Contribution:** Managed academic publishing, text editing, and administrative tracking for conference submissions.

The short paper **"DETERMINING THE SWITCHING AND LANDING TIME IN THE MOON SOFT LANDING PROBLEM"** was successfully presented and published in the [*CONFERENCE PROCEEDINGS of the VIII International Scientific-Practical Conference "Information Technology for Education, Science and Technics" (ITEST-2026)*](https://itest.chdtu.edu.ua/Conference%20Book%20of%20Abstracts%20Layout%20_ITEST-2026.pdf) (Page 393).

---

## 📁 Repository Structure & Files

The repository is organized as follows to include both the codebase and the official academic assets:

### 💻 Source Code
*   `landing_mechanics.py` — Core numerical engine containing the manual vector RK4 implementation, shooting method logic, and hybrid root-finding algorithms.
*   `utils.py` — Visualization module using Matplotlib to render spacecraft phase portraits and kinematic time-series.
*   `example.py` — Production entry point containing pre-configured simulation scenarios (including heavy module landing and ballistic jump stress-tests).

### 📄 Academic Papers & Presentations
*   `Paper(in Ukrainian).pdf` — The comprehensive full-length research paper detailing the mathematical proofs and maximum principle derivations.
*   `Presentation(in Ukrainian).pdf` — Technical slide deck used for local academic defenses.
*   `Presentation_Moon_(in English).pdf` — Official English presentation slides prepared for the international audience at the ITEST-2026 conference.

---

## 🛠 Tech Stack

*   **Core:** Python 3
*   **Data Structures:** NumPy (utilized strictly for low-level array manipulation and vectorized state histories).
*   **Graphics:** Matplotlib (used for generating phase trajectories and continuous simulation profiles).

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.