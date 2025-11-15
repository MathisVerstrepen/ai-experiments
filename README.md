
# AI Experiments

This repository is a collection of various experiments and projects exploring the capabilities of modern AI. Each directory contains a self-contained experiment.

## Experiments

### 1. Self-Improving Prompt Creator

- **Location:** `prompt-self-improve/`
- **Description:** An autonomous system designed to iteratively generate, evaluate, and refine an AI prompt to meet a specified quality threshold. It uses a multi-agent pipeline where different LLMs collaborate to craft a prompt, test it against generated use cases, critique the results, and use that feedback to improve the original prompt in a continuous loop until a target quality score is achieved.
- **For a detailed breakdown, see the [experiment's README](./prompt-self-improve/README.md).**

## Getting Started

Follow these steps to set up the environment and run the experiments.

### Prerequisites

- Python 3.8+
- An API key from [OpenRouter.ai](https://openrouter.ai/)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/MathisVerstrepen/ai-experiments.git
    cd ai-experiments
    ```

2. **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up your environment variables:**
    Create a file named `.env` in the root of the project and add your OpenRouter API key:

    ```env
    OPENROUTER_API_KEY="your_openrouter_api_key_here"
    ```

## How to Run an Experiment

### Self-Improving Prompt Creator

This script takes a high-level description of a desired prompt and refines it through multiple iterations.

1. **Define your input:**
    Open the file `prompt-self-improve/input.txt` and write a detailed description of the prompt you want to create. The existing content serves as a good example.

2. **Run the script:**
    Execute the main script from the root directory of the repository:

    ```bash
    python prompt-self-improve/main.py
    ```

3. **Check the output:**
    The script will print its progress to the console. Once it completes (either by reaching the quality threshold or the maximum number of iterations), the final, optimized prompt will be saved in `prompt-self-improve/output.txt`.
