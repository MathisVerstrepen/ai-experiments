import os
from typing import List
from rich.console import Console
from rich.panel import Panel

from helpers import run_llm, run_llm_with_schema
from prompts import (
    PROMPT_CRAFTER_SYSTEM_PROMPT,
    EXAMPLE_GENERATOR_SYSTEM_PROMPT,
    EVALUATOR_SYSTEM_PROMPT,
    PROMPT_REFINER_SYSTEM_PROMPT,
)
from schemas import UseCases, EvaluationResult
from concurrent.futures import ThreadPoolExecutor

# --- Configuration ---
# Check for API key
if not os.environ.get("OPENROUTER_API_KEY"):
    raise ValueError("OPENROUTER_API_KEY environment variable not set.")

# Models for different roles
MODEL_PROMPT_CRAFTER = "google/gemini-2.5-pro"
MODEL_EXAMPLE_GENERATOR = "deepseek/deepseek-chat-v3.1"
MODEL_WORKER = "moonshotai/kimi-k2-thinking"
MODEL_EVALUATOR = "google/gemini-2.5-flash"

# Pipeline settings
N_USE_CASES = 5
QUALITY_THRESHOLD = 9.6
MAX_ITERATIONS = 5

# Rich console for better output
console = Console()


def print_panel(title: str, content: str, style: str = "cyan"):
    """Prints content inside a formatted panel."""
    panel = Panel(content, title=title, border_style=style, expand=False)
    console.print(panel)


def main():
    """Main function to run the self-improving prompt creator pipeline."""

    # --- 1. Initialization Phase ---
    console.rule("[bold green]Phase 1: Initialization[/bold green]")

    # Read user prompt from input.txt
    try:
        with open("prompt-self-improve/input.txt", "r") as f:
            user_prompt_description = f.read().strip()
        if not user_prompt_description:
            raise ValueError("input.txt is empty")
        print_panel(
            "User Prompt Description (from input.txt)",
            user_prompt_description,
            "yellow",
        )
    except FileNotFoundError:
        console.print("[bold red]Error: input.txt not found. Exiting.[/bold red]")
        exit(1)
    except ValueError as e:
        console.print(f"[bold red]Error: {e}. Exiting.[/bold red]")
        exit(1)

    # Initial Prompt Generation
    with console.status(
        "[bold yellow]Generating initial prompt (v1)...[/bold yellow]", spinner="dots"
    ):
        current_prompt = run_llm(
            user_prompt=user_prompt_description,
            model=MODEL_PROMPT_CRAFTER,
            system_prompt=PROMPT_CRAFTER_SYSTEM_PROMPT,
        )
    print_panel("Initial Prompt (v1)", current_prompt)

    # Use-Case Generation
    use_case_prompt = f"Generate {N_USE_CASES} use cases for the following prompt description:\n\n{user_prompt_description}"
    with console.status(
        f"[bold yellow]Generating {N_USE_CASES} use cases...[/bold yellow]",
        spinner="dots",
    ):
        use_cases_obj = run_llm_with_schema(
            user_prompt=use_case_prompt,
            model=MODEL_EXAMPLE_GENERATOR,
            system_prompt=EXAMPLE_GENERATOR_SYSTEM_PROMPT,
            schema=UseCases,
        )
        use_cases = use_cases_obj.use_cases
    print_panel(
        f"{N_USE_CASES} Use Cases", "\n".join(f"- {uc}" for uc in use_cases), "magenta"
    )

    # --- 2. The Evaluation & Refinement Loop ---
    for i in range(MAX_ITERATIONS):
        iteration = i + 1
        console.rule(
            f"[bold green]Phase 2: Iteration {iteration}/{MAX_ITERATIONS}[/bold green]"
        )

        # --- 2.1. Parallel Execution ---
        def generate_response(use_case):
            return run_llm(
                user_prompt=use_case,
                model=MODEL_WORKER,
                system_prompt=current_prompt,
            )

        with console.status(
            f"[bold yellow]Generating {N_USE_CASES} responses in parallel...[/bold yellow]",
            spinner="dots",
        ):
            with ThreadPoolExecutor() as executor:
                responses = list(executor.map(generate_response, use_cases))

        print_panel(
            "Generated Responses",
            f"Generated {len(responses)} responses for evaluation.",
            "blue",
        )

        # --- 2.2. Critique & Scoring ---
        evaluations: List[EvaluationResult] = []
        with console.status(
            f"[bold yellow]Evaluating {N_USE_CASES} responses...[/bold yellow]",
            spinner="dots",
        ):
            for idx, (use_case, response) in enumerate(zip(use_cases, responses)):
                evaluator_user_prompt = f"""
                **Original User Prompt Description:**
                {user_prompt_description}

                **Prompt Being Tested:**
                {current_prompt}

                **Use Case (Input):**
                {use_case}

                **Generated Response:**
                {response}
                """
                evaluation = run_llm_with_schema(
                    user_prompt=evaluator_user_prompt,
                    model=MODEL_EVALUATOR,
                    system_prompt=EVALUATOR_SYSTEM_PROMPT,
                    schema=EvaluationResult,
                )
                evaluations.append(evaluation)
                console.log(
                    f"Evaluation for Use Case #{idx+1} complete. Score: {evaluation.quality_score}/10"
                )

        # --- 2.3. Aggregation ---
        total_score = sum(e.quality_score for e in evaluations)
        mean_score = total_score / len(evaluations)

        all_pros = sorted(list(set(pro for e in evaluations for pro in e.pros)))
        all_cons = sorted(list(set(con for e in evaluations for con in e.cons)))

        feedback_summary = f"Average Score: {mean_score:.2f}/10\n\n"
        feedback_summary += "**Aggregated Pros:**\n" + "\n".join(
            f"- {p}" for p in all_pros
        )
        feedback_summary += "\n\n**Aggregated Cons:**\n" + "\n".join(
            f"- {c}" for c in all_cons
        )
        print_panel("Aggregated Feedback", feedback_summary, "yellow")

        # --- 2.4. Quality Gate ---
        if mean_score >= QUALITY_THRESHOLD:
            console.rule("[bold green]🎉 Quality Threshold Met! 🎉[/bold green]")
            print_panel(
                f"Final Optimized Prompt (Score: {mean_score:.2f})",
                current_prompt,
                "green",
            )

            # Save the final prompt to output.txt
            with open("prompt-self-improve/output.txt", "w") as f:
                f.write(current_prompt)
            console.print("[bold green]✓ Final prompt saved to output.txt[/bold green]")
            break
        else:
            console.log(
                f"Score {mean_score:.2f} is below threshold of {QUALITY_THRESHOLD}. Refining prompt..."
            )

        # --- 2.5. Prompt Refinement ---
        refiner_user_prompt = f"""
        **Original User Prompt Description:**
        {user_prompt_description}

        **Underperforming Prompt (v{iteration}):**
        {current_prompt}

        **Aggregated Feedback (Pros & Cons):**
        {feedback_summary}

        Based on the feedback, please generate an improved version of the prompt.
        """
        with console.status(
            f"[bold yellow]Refining prompt to create v{iteration+1}...[/bold yellow]",
            spinner="dots",
        ):
            new_prompt = run_llm(
                user_prompt=refiner_user_prompt,
                model=MODEL_PROMPT_CRAFTER,
                system_prompt=PROMPT_REFINER_SYSTEM_PROMPT,
            )

        print_panel(f"Improved Prompt (v{iteration+1})", new_prompt)
        current_prompt = new_prompt
    else:
        console.rule("[bold red]Max Iterations Reached[/bold red]")
        print_panel(
            f"Final Prompt (Threshold Not Met, Score: {mean_score:.2f})",
            current_prompt,
            "red",
        )

        # Save the final prompt to output.txt even if threshold not met
        with open("prompt-self-improve/output.txt", "w") as f:
            f.write(current_prompt)
        console.print(
            "[bold yellow]⚠ Final prompt saved to output.txt (threshold not met)[/bold yellow]"
        )


if __name__ == "__main__":
    main()
