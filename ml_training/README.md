# Machine Learning Training Pipeline

This directory contains the scripts required to train the AI models.

## Step 1: Generate Datasets
If you don't have the real Kaggle datasets, generate synthetic datasets:
```bash
python ml_training/generate_datasets.py
```
This will output `Crop_recommendation.csv` and `fertilizer_recommendation.csv` to the `data/` folder.

## Step 2: Train Models
Run the training scripts:
```bash
python ml_training/train_crop.py
python ml_training/train_fertilizer.py
python ml_training/train_cnn.py
```
The trained models will be saved into the `models/` directory for the backend to use.
