#!/usr/bin/env python3
"""
Item #6: A/B Test Design and Task Pair Generation

Creates matched pairs for statistical comparison:
- Control: Template-based context (naive)
- Treatment: Real-analysis context (Braxis)
"""

import json
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
from datetime import datetime


@dataclass
class TaskPair:
    """A matched pair of control and treatment tasks."""
    pair_id: str
    task_type: str
    task_title: str
    control_task: Dict
    treatment_task: Dict
    randomization_order: str  # "control_first" or "treatment_first"


class ABTestDesigner:
    """Design A/B test with matched pairs."""

    def __init__(self, base_tasks: List[Dict]):
        self.base_tasks = base_tasks
        self.pairs: List[TaskPair] = []

    def create_pairs(self, num_pairs: int = 10) -> List[TaskPair]:
        """
        Create matched task pairs.

        For each pair:
        - Control: Same task with TEMPLATE context
        - Treatment: Same task with REAL-ANALYSIS context
        - Randomize presentation order
        """
        print(f"\nCreating {num_pairs} matched task pairs...")

        # Select tasks
        selected_tasks = random.sample(self.base_tasks, min(num_pairs, len(self.base_tasks)))

        for i, task in enumerate(selected_tasks):
            pair_id = f"pair_{i+1:02d}"

            # Control: Template context
            control_task = {
                "pair_id": pair_id,
                "task_id": f"{task['task_id']}_control",
                "type": task["type"],
                "title": task["title"],
                "context_method": "template",
                "description": task["description"],
            }

            # Treatment: Real-analysis context
            treatment_task = {
                "pair_id": pair_id,
                "task_id": f"{task['task_id']}_treatment",
                "type": task["type"],
                "title": task["title"],
                "context_method": "real_analysis",
                "description": task["description"],
            }

            # Randomize presentation order
            order = random.choice(["control_first", "treatment_first"])

            pair = TaskPair(
                pair_id=pair_id,
                task_type=task["type"],
                task_title=task["title"],
                control_task=control_task,
                treatment_task=treatment_task,
                randomization_order=order
            )

            self.pairs.append(pair)

        print(f"✅ Created {len(self.pairs)} matched pairs")
        return self.pairs

    def get_randomized_order(self, pair: TaskPair) -> Tuple[Dict, Dict]:
        """Get tasks in randomized order for blinding."""
        if pair.randomization_order == "control_first":
            return pair.control_task, pair.treatment_task
        else:
            return pair.treatment_task, pair.control_task

    def print_pair_summary(self):
        """Print summary of pairs."""
        print("\n" + "=" * 70)
        print("A/B TEST PAIRS SUMMARY")
        print("=" * 70)

        by_type = {}
        for pair in self.pairs:
            if pair.task_type not in by_type:
                by_type[pair.task_type] = []
            by_type[pair.task_type].append(pair)

        print(f"\nTotal Pairs: {len(self.pairs)}")
        print(f"\nBy Task Type:")
        for task_type, type_pairs in by_type.items():
            print(f"  {task_type}: {len(type_pairs)} pairs")

        print(f"\nRandomization Order:")
        control_first = sum(1 for p in self.pairs if p.randomization_order == "control_first")
        treatment_first = sum(1 for p in self.pairs if p.randomization_order == "treatment_first")
        print(f"  Control first: {control_first}")
        print(f"  Treatment first: {treatment_first}")

    def export_pairs(self, filepath: str):
        """Export pairs to JSON for test execution."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "study": "Item #6: Real-Analysis vs Template A/B Test",
            "total_pairs": len(self.pairs),
            "pairs": [asdict(pair) for pair in self.pairs]
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\n✅ Exported {len(self.pairs)} pairs to {filepath}")
        return filepath


def generate_ab_test_pairs():
    """Generate 10 matched A/B test pairs from Item #4 tasks."""

    # Load Item #4 task specifications
    with open("/home/user/braxis/ITEM4_TASK_SPECS.json") as f:
        task_specs = json.load(f)

    designer = ABTestDesigner(task_specs["tasks"])
    designer.create_pairs(num_pairs=10)
    designer.print_pair_summary()
    designer.export_pairs("/home/user/braxis/item6_ab_test_pairs.json")

    return designer.pairs


if __name__ == "__main__":
    print("=" * 70)
    print("ITEM #6: A/B TEST DESIGN")
    print("=" * 70)
    print("\nDesigning matched task pairs for comparison:")
    print("- Control (10 tasks): Template-based context")
    print("- Treatment (10 tasks): Real-analysis context")
    print("- Same tasks, different context methods")
    print("- Randomized presentation order for blinding")

    pairs = generate_ab_test_pairs()

    print("\n" + "=" * 70)
    print("Example Pair Structure")
    print("=" * 70)

    if pairs:
        example = pairs[0]
        print(f"\nPair ID: {example.pair_id}")
        print(f"Task: {example.task_title}")
        print(f"\nControl Task (Template Context):")
        print(f"  - Context Method: {example.control_task['context_method']}")
        print(f"  - Will use hardcoded file patterns")
        print(f"\nTreatment Task (Real Analysis Context):")
        print(f"  - Context Method: {example.treatment_task['context_method']}")
        print(f"  - Will use actual Braxis analysis")
        print(f"\nPresentation Order: {example.randomization_order}")
        print(f"(Blinded: Agent doesn't know which is which)")
