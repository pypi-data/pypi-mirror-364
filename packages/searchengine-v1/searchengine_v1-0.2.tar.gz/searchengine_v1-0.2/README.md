### `Search Engine` - README

## Overview

This `Search Engine` class provides a simple way to store, search, and remove sentences/phrases using embeddings generated from a pre-trained transformer model (`all-MiniLM-L6-v2`). It utilizes the Hugging Face `AutoModel` and `AutoTokenizer` for encoding sentences into dense vector embeddings, then allows for cosine similarity-based searches.

## Features

* **Add Sentence**: Add a sentence to the dataset if it's not already present.
* **Search**: Find similar sentences based on cosine similarity.
* **Remove Sentence**: Remove a sentence by exact match if present.
* **Clear All**: Remove all stored data (vectors and sentences).

## Requirements

* Python >= 3.7
* `transformers` library (for Hugging Face models)
* `torch` (PyTorch)
* `scikit-learn` (for cosine similarity)

## Installation & Setup

1. **Clone the Repository**:
   First, clone the repository to your local machine.

   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. **Install Required Dependencies**:
   Install the necessary Python dependencies via `pip`:

   ```bash
   pip install -r requirements.txt
   ```

   Where `requirements.txt` includes:

   ```
   transformers==4.x
   torch==1.x
   scikit-learn==0.24
   ```

3. **Download Pre-trained Model**:
   You can either download the model from Hugging Face and save it locally or use a pre-downloaded model. Make sure the model is located in `./my_local_model/all-MiniLM-L6-v2`.

   * To download the model directly using `transformers`, run:

   ```bash
   python -c "from transformers import AutoModel, AutoTokenizer; AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'); AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')"
   ```

4. **Run the Python Code**:
   After setup, you can start using the search engine class by running the Python script that contains the `Search_engine` class.

   Example:

   ```bash
   python search_engine.py
   ```

---

### **Bash Script for Setup and Execution**

```bash
#!/bin/bash

# Step 1: Install Python and required packages
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "Python3 is not installed. Installing Python3..."
    sudo apt update
    sudo apt install python3 python3-pip -y
fi

# Install dependencies
echo "Installing required dependencies..."
pip install -r requirements.txt

# Step 2: Download Pre-trained Model (if not already downloaded)
MODEL_DIR="./my_local_model/all-MiniLM-L6-v2"
if [ ! -d "$MODEL_DIR" ]; then
    echo "Model not found, downloading..."
    python -c "from transformers import AutoModel, AutoTokenizer; AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'); AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')"
else
    echo "Model already downloaded at $MODEL_DIR."
fi

# Step 3: Run the Python script (assumes the script is named search_engine.py)
echo "Running the Search Engine..."
python search_engine.py
```

---

### Code Walkthrough

#### `Search_engine` Class:

1. **Initialization (`__init__`)**:

   * Loads the model and tokenizer from the specified directory.
   * Initializes empty lists to store sentence vectors (`vector_data`) and sentences (`base_data`).
   * Sets a similarity threshold (`threshold`).

2. **`get_cls_vector`**:

   * Converts a sentence to its vector representation using the pre-trained model.
   * Returns the embedding corresponding to the `[CLS]` token.

3. **`similarity`**:

   * Calculates the cosine similarity between two vectors `X` and `Y`.

4. **`add_one`**:

   * Converts a sentence to its vector and checks if a similar sentence already exists. If not, it stores the sentence and its vector.

5. **`add_more`**:

   * Adds multiple sentences to the search engine.

6. **`search_one`**:

   * Searches for the most similar sentences to a given input sentence, returning results that exceed the defined similarity threshold.

7. **`remove_one`**:

   * Removes a sentence if it has an exact match based on similarity.

8. **`remove_all`**:

   * Clears all stored sentences and vectors.

---

### Example Usage

```python
# Initialize the Search Engine
search_engine = Search_engine()

# Add sentences
search_engine.add_one("I love machine learning.")
search_engine.add_one("Artificial Intelligence is fascinating.")

# Search for similar sentences
results = search_engine.search_one("I enjoy AI.", metadata=True)
for score, sentence, index in results:
    print(f"Score: {score}, Sentence: {sentence}, Index: {index}")

# Remove a sentence
search_engine.remove_one("I love machine learning.")

# Clear all data
search_engine.remove_all()
```

