#!/usr/bin/env python3
from robust_ml_filter import RobustMLComplianceFilter
import shutil

# Remove old models
shutil.rmtree('robust_ml_models', ignore_errors=True)

# Retrain models
print("🤖 Retraining ML models...")
filter = RobustMLComplianceFilter()
result = filter.train(force_retrain=True)
print(f"✅ Training complete! Accuracy: {result['test_accuracy']:.1%}")