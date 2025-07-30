"""
Auto task detection and creation.
"""

import re
from typing import Any, Dict, List, Union

from ..core.simple_interfaces import SimpleTask


def create_task(
    task_type: str, task_description: str, dataset: List[Dict[str, Any]]
) -> SimpleTask:
    """
    Create task handler based on explicit task type.

    Args:
        task_type: Explicit task type ('generation', 'classification', 'rating')
        task_description: Human-readable task description
        dataset: Sample data to help with task configuration

    Returns:
        SimpleTask instance
    """

    task_type_lower = task_type.lower()

    if task_type_lower in ["generation", "generate"]:
        return _create_generation_task(task_description, dataset)
    elif task_type_lower in ["classification", "classify"]:
        return _create_classification_task(task_description, dataset)
    elif task_type_lower in ["rating", "regression", "scoring"]:
        return _create_rating_task(task_description, dataset)
    else:
        raise ValueError(f"Unsupported task type: {task_type}. Use 'generation', 'classification', or 'rating'.")


# Backward compatibility wrapper
def auto_detect_task(
    task: Union[str, SimpleTask], dataset: List[Dict[str, Any]]
) -> SimpleTask:
    """
    Backward compatibility wrapper. Always defaults to generation task.
    
    DEPRECATED: Use create_task() with explicit task_type instead.
    """
    
    if isinstance(task, SimpleTask):
        return task
    
    # Always default to generation to preserve full responses
    return _create_generation_task(task, dataset)


def _create_classification_task(
    task_desc: str, dataset: List[Dict[str, Any]]
) -> SimpleTask:
    """Create classification task with auto-detected classes."""

    # Try to detect classes from dataset
    classes = _detect_classes_from_data(dataset)

    def format_func(template: str, sample: Dict[str, Any]) -> str:
        # Simple template formatting - replace {field} with sample values
        formatted = template
        for key, value in sample.items():
            if key != "label" and key != "target":  # Don't include ground truth
                formatted = formatted.replace(f"{{{key}}}", str(value))

        # Add task instruction if not present
        if not any(
            word in template.lower() for word in ["classify", "category", "label"]
        ):
            formatted += f"\\n\\nTask: {task_desc}"

        if classes:
            formatted += f"\\nOptions: {', '.join(classes)}"

        return formatted

    def extract_func(response: str) -> str:
        # Extract classification from response
        response = response.strip().lower()

        # If classes are known, try to match
        if classes:
            for cls in classes:
                if cls.lower() in response:
                    return cls

        # Otherwise return first word/line
        return response.split("\\n")[0].split()[0]

    def truth_func(sample: Dict[str, Any]) -> str:
        # Common label field names
        for field in ["label", "target", "class", "category", "ground_truth"]:
            if field in sample:
                return str(sample[field])

        # If no standard field, use last field
        return str(list(sample.values())[-1])

    return SimpleTask(format_func, extract_func, truth_func)


def _create_sentiment_task(dataset: List[Dict[str, Any]]) -> SimpleTask:
    """Create sentiment analysis task."""

    def format_func(template: str, sample: Dict[str, Any]) -> str:
        formatted = template
        for key, value in sample.items():
            if key not in ["label", "target", "sentiment"]:
                formatted = formatted.replace(f"{{{key}}}", str(value))

        if "sentiment" not in template.lower():
            formatted += "\\n\\nAnalyze the sentiment: positive, negative, or neutral"

        return formatted

    def extract_func(response: str) -> str:
        response = response.strip().lower()

        if "positive" in response:
            return "positive"
        elif "negative" in response:
            return "negative"
        elif "neutral" in response:
            return "neutral"
        else:
            # Return first word
            return response.split()[0] if response.split() else "neutral"

    def truth_func(sample: Dict[str, Any]) -> str:
        for field in ["sentiment", "label", "target"]:
            if field in sample:
                return str(sample[field]).lower()
        return str(list(sample.values())[-1]).lower()

    return SimpleTask(format_func, extract_func, truth_func)


def _create_rating_task(task_desc: str, dataset: List[Dict[str, Any]]) -> SimpleTask:
    """Create rating/scoring task."""

    def format_func(template: str, sample: Dict[str, Any]) -> str:
        formatted = template
        for key, value in sample.items():
            if key not in ["rating", "score", "target", "label"]:
                formatted = formatted.replace(f"{{{key}}}", str(value))

        if not any(word in template.lower() for word in ["rate", "score", "scale"]):
            formatted += f"\\n\\nTask: {task_desc}"

        return formatted

    def extract_func(response: str) -> float:
        # Extract numeric rating from response
        numbers = re.findall(r"\\d+\\.?\\d*", response)
        if numbers:
            return float(numbers[0])
        return 0.0

    def truth_func(sample: Dict[str, Any]) -> float:
        for field in ["rating", "score", "target", "label"]:
            if field in sample:
                try:
                    return float(sample[field])
                except (ValueError, TypeError):
                    pass

        # Try to convert last field to float
        try:
            return float(list(sample.values())[-1])
        except (ValueError, TypeError):
            return 0.0

    return SimpleTask(format_func, extract_func, truth_func)


def _create_generation_task(
    task_desc: str, dataset: List[Dict[str, Any]]
) -> SimpleTask:
    """Create text generation task."""

    def format_func(template: str, sample: Dict[str, Any]) -> str:
        formatted = template
        for key, value in sample.items():
            if key not in ["output", "target", "expected"]:
                formatted = formatted.replace(f"{{{key}}}", str(value))

        if not any(
            word in template.lower() for word in ["generate", "create", "write"]
        ):
            formatted += f"\\n\\nTask: {task_desc}"

        return formatted

    def extract_func(response: str) -> str:
        # For generation, return the full response (cleaned)
        return response.strip()

    def truth_func(sample: Dict[str, Any]) -> str:
        for field in ["output", "target", "expected", "reference"]:
            if field in sample:
                return str(sample[field])
        return str(list(sample.values())[-1])

    return SimpleTask(format_func, extract_func, truth_func)


def _detect_classes_from_data(dataset: List[Dict[str, Any]]) -> List[str]:
    """Try to detect classification classes from the dataset."""

    if not dataset:
        return []

    # Look for label/target fields
    for field in ["label", "target", "class", "category"]:
        if field in dataset[0]:
            # Get unique values
            values = set()
            for sample in dataset[:100]:  # Sample first 100
                if field in sample:
                    values.add(str(sample[field]))

            # If reasonable number of classes, return them
            if 2 <= len(values) <= 20:
                return sorted(list(values))

    return []
