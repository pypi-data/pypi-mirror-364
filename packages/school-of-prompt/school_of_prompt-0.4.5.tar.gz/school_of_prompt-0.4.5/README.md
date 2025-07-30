# School of Prompt

**Prompt optimization framework with smart defaults and enterprise features.**

## Quick Start

```python
from school_of_prompt import optimize

results = optimize(
    data="reviews.csv",
    task="classify sentiment", 
    prompts=["Analyze sentiment: {text}", "Is this positive or negative: {text}"],
    api_key="sk-..."
)

print(f"Best prompt: {results['best_prompt']}")
print(f"Accuracy: {results['best_score']:.2f}")
```

## Installation

```bash
pip install school-of-prompt
```

## Usage Patterns

### Level 0: Simple API
```python
results = optimize(
    data="data.csv",
    task="classify sentiment",
    prompts=["Prompt 1", "Prompt 2"],
    api_key="sk-..."
)
```

### Level 1: Configuration-Driven
```python
# YAML configuration
results = optimize(config="config.yaml")

# Enhanced API
results = optimize(
    data="data.csv",
    task="regression",
    prompts=["prompt1.txt", "prompt2.txt"],
    model={"name": "gpt-4", "temperature": 0.1},
    metrics=["mae", "within_1", "within_2"],
    sampling_strategy="stratified",
    cross_validation=True,
    cache_enabled=True,
    api_key="sk-..."
)
```

### Level 2: Enterprise Features
```python
from school_of_prompt import optimize
from school_of_prompt.data.registry import get_data_registry

# Multi-dataset workflow
results = optimize(
    data={
        "train": "train.csv",
        "validation": "val.csv", 
        "test": "test.csv"
    },
    task="classification",
    prompts=["template1", "template2"],
    metrics=["accuracy", "f1_score", "valid_rate"],
    enrichers=["text_length", "readability"],
    preprocessors=["clean_text", "normalize"],
    cross_validation=True,
    comprehensive_analysis=True,
    parallel_evaluation=True,
    api_key="sk-..."
)
```

## Core Features

### Advanced Metrics
- **Tolerance-based**: `within_1`, `within_2`, `within_3`
- **Domain-specific**: `valid_rate`, `token_efficiency`, `response_quality`
- **Statistical**: `r2_score`, `prediction_confidence`, `error_std`

### Production Features
- **Intelligent caching**: Configurable expiry and size management
- **Batch processing**: Parallel evaluation with progress tracking
- **Multi-dataset workflows**: Train/validation/test dataset support
- **Cross-validation**: K-fold cross-validation support
- **Error handling**: Retry logic and graceful degradation

### Data Loading
- **File formats**: CSV, JSONL, pandas DataFrames
- **Multi-dataset**: `{"train": "train.csv", "test": "test.csv"}`
- **Custom sources**: Extensible data source registry
- **Preprocessing**: Text cleaning, normalization, enrichment

## Configuration

YAML configuration example:
```yaml
task:
  name: "classification_task"
  type: "classification"

datasets:
  training: "data/train.csv"
  validation: "data/val.csv"
  test: "data/test.csv"

evaluation:
  metrics: ["accuracy", "f1_score", "within_1"]
  sampling_strategy: "stratified"
  cross_validation: true
  k_fold: 5

cache:
  enabled: true
  expiry: "24h"

batch_processing:
  parallel_evaluation: true
  chunk_size: 100
```

## Examples

### Classification
```python
results = optimize(
    data="reviews.csv",
    task="classify sentiment",
    prompts=[
        "Sentiment: {review}",
        "Classify sentiment of: {review}",
        "Is this positive or negative: {review}"
    ],
    model="gpt-3.5-turbo",
    metrics=["accuracy", "f1_score"]
)
```

### Regression
```python
results = optimize(
    data="ratings.csv",
    task="rate from 1-10",
    prompts=[
        "Rate this from 1-10: {content}",
        "Score (1-10): {content}",
        "Rating for {content}:"
    ],
    metrics=["mae", "within_1", "within_2"]
)
```

### Content Moderation
```python
results = optimize(
    data="content.csv",
    task="classify as safe or unsafe",
    prompts="templates/safety_prompts.txt",
    model={"name": "gpt-4", "temperature": 0.0},
    metrics=["accuracy", "precision", "recall"]
)
```

### Enriching Untagged Data with External Labels
```python
import pandas as pd
import re
from textblob import TextBlob
from school_of_prompt import optimize

# Step 1: Load raw untagged data (e.g., from database, API, files)
raw_data = pd.DataFrame({
    "review": [
        "This product changed my life! Amazing quality and fast shipping!",
        "Terrible experience, would not recommend. Broke immediately.",
        "It's okay, nothing special but does the job adequately.",
        "Absolutely love it! Best purchase ever. 5 stars!",
        "Poor quality, broke after one week. Customer service unhelpful."
    ],
    "rating": [5, 1, 3, 5, 2]  # External rating system
})

# Step 2: Enrich with rule-based and external tagging systems
def enrich_with_tags(df):
    """Add multiple tag sources before prompt optimization"""
    enriched = df.copy()
    
    # Rule-based sentiment (using TextBlob)
    enriched["sentiment_rule"] = df["review"].apply(
        lambda x: "positive" if TextBlob(x).sentiment.polarity > 0.1 
        else "negative" if TextBlob(x).sentiment.polarity < -0.1 
        else "neutral"
    )
    
    # Rating-based labels (external system)
    enriched["sentiment_rating"] = df["rating"].apply(
        lambda x: "positive" if x >= 4 else "negative" if x <= 2 else "neutral"
    )
    
    # Length-based features
    enriched["text_length"] = df["review"].apply(len)
    enriched["is_detailed"] = enriched["text_length"] > 50
    
    # Keyword-based features (business rules)
    positive_words = ["love", "amazing", "best", "great", "excellent"]
    negative_words = ["terrible", "broke", "poor", "bad", "awful"]
    
    enriched["has_positive_keywords"] = df["review"].apply(
        lambda x: any(word in x.lower() for word in positive_words)
    )
    enriched["has_negative_keywords"] = df["review"].apply(
        lambda x: any(word in x.lower() for word in negative_words)
    )
    
    return enriched

# Apply enrichment
tagged_data = enrich_with_tags(raw_data)

# Step 3: Create ground truth from multiple tag sources
def create_ground_truth(row):
    """Combine multiple tag sources into ground truth"""
    # Priority: rating > keywords > rule-based
    if row["rating"] >= 4:
        return "positive"
    elif row["rating"] <= 2:
        return "negative"
    elif row["has_positive_keywords"] and not row["has_negative_keywords"]:
        return "positive"
    elif row["has_negative_keywords"] and not row["has_positive_keywords"]:
        return "negative"
    else:
        return row["sentiment_rule"]  # Fallback to TextBlob

tagged_data["label"] = tagged_data.apply(create_ground_truth, axis=1)

# Step 4: Now optimize prompts using enriched, tagged data
results = optimize(
    data=tagged_data[["review", "label"]],  # Only use text and final label
    task="classify sentiment",
    prompts=[
        "Sentiment: {review}",
        "Classify this review sentiment: {review}",
        "Is this review positive, negative, or neutral: {review}",
        "Rate the sentiment of: {review}"
    ],
    model="gpt-3.5-turbo",
    metrics=["accuracy", "f1_score"]
)

print(f"Best prompt: {results['best_prompt']}")
print(f"Accuracy: {results['best_score']:.2f}")

# Step 5: Optional - Compare against individual tag sources
for tag_source in ["sentiment_rule", "sentiment_rating"]:
    baseline_data = tagged_data[["review", tag_source]].rename(columns={tag_source: "label"})
    baseline_results = optimize(
        data=baseline_data,
        task="classify sentiment",
        prompts=[results['best_prompt']],  # Use best prompt
        model="gpt-3.5-turbo",
        verbose=False
    )
    print(f"{tag_source} baseline accuracy: {baseline_results['best_score']:.2f}")
```

**This workflow demonstrates:**
- **External data enrichment**: Using ratings, business rules, existing NLP tools
- **Multi-source labeling**: Combining rule-based, rating-based, and keyword-based tags
- **Ground truth synthesis**: Creating final labels from multiple tag sources
- **Prompt optimization**: Using enriched data for better prompt development
- **Baseline comparison**: Validating against individual tag sources

## API Reference

### `optimize()`

Main optimization function.

**Parameters:**
- `data` (str|DataFrame|dict): Dataset or file path
- `task` (str): Task description
- `prompts` (list): Prompt variants to evaluate
- `model` (str|dict): Model configuration
- `metrics` (list): Evaluation metrics
- `api_key` (str): OpenAI API key
- `config` (str): Path to YAML configuration file
- `sample_size` (int): Limit evaluation samples
- `cross_validation` (bool): Enable k-fold cross-validation
- `cache_enabled` (bool): Enable response caching
- `comprehensive_analysis` (bool): Enable detailed analysis

**Returns:**
```python
{
    "best_prompt": str,
    "best_score": float,
    "prompts": dict,
    "summary": dict,
    "comprehensive_analysis": dict  # if enabled
}
```

## Environment Setup

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

## Data Format

Expected data structure:
- Input columns: Text or features to process
- Label column: Ground truth (`label`, `target`, `class`, etc.)

CSV example:
```csv
text,label
"Great product",positive
"Poor quality",negative
"Average item",neutral
```

JSONL example:
```json
{"text": "Great product", "label": "positive"}
{"text": "Poor quality", "label": "negative"}
```

## Extension Points

```python
from school_of_prompt import CustomMetric, CustomDataSource

# Custom metrics
class CustomAccuracy(CustomMetric):
    name = "custom_accuracy"
    def calculate(self, predictions, actuals):
        return custom_accuracy_logic(predictions, actuals)

# Custom data sources
class APIDataSource(CustomDataSource):
    def load(self):
        return fetch_from_api()

# Usage
results = optimize(
    data=APIDataSource(),
    metrics=[CustomAccuracy(), "f1_score"],
    task="classification",
    prompts=["template1", "template2"]
)
```

## Version 0.3.0 Features

- Advanced metrics with tolerance and statistical analysis
- YAML configuration system
- Production caching and batch processing
- Multi-dataset workflows
- Cross-validation support
- Comprehensive error analysis
- Data enrichment pipeline

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License