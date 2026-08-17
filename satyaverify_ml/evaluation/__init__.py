import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve, precision_recall_curve,
    classification_report
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logger = logging.getLogger(__name__)

def compute_metrics(y_true, y_pred, y_proba=None):
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
    metrics = {
        'accuracy': float(accuracy_score(y_true, y_pred)),
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'recall': float(recall_score(y_true, y_pred, zero_division=0)),
        'f1': float(f1_score(y_true, y_pred, zero_division=0)),
        'specificity': float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0,
        'fpr': float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0,
        'fnr': float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0,
        'confusion_matrix': cm.tolist(),
        'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp),
    }
    if y_proba is not None and len(np.unique(y_true)) == 2:
        try:
            metrics['roc_auc'] = float(roc_auc_score(y_true, y_proba))
        except Exception:
            metrics['roc_auc'] = None
    else:
        metrics['roc_auc'] = None
    return metrics

def plot_confusion_matrix(cm, labels, output_path, title='Confusion Matrix'):
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.title(title)
    plt.ylabel('True')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def plot_roc_curve(y_true, y_proba, output_path, title='ROC Curve'):
    if len(np.unique(y_true)) != 2:
        return
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, label=f'ROC (AUC={roc_auc_score(y_true, y_proba):.3f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def plot_precision_recall(y_true, y_proba, output_path, title='Precision-Recall Curve'):
    if len(np.unique(y_true)) != 2:
        return
    precision, recall, _ = precision_recall_curve(y_true, y_proba)
    plt.figure(figsize=(6, 5))
    plt.plot(recall, precision, label='PR Curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def plot_model_comparison(results, output_path, metrics=None):
    if metrics is None:
        metrics = ['accuracy', 'precision', 'recall', 'f1', 'specificity']
    df = {}
    for model_name, m in results.items():
        df[model_name] = [m.get(m_name, 0) for m_name in metrics]
    import pandas as pd
    df_plot = pd.DataFrame(df, index=metrics).T
    df_plot.plot(kind='bar', figsize=(10, 6))
    plt.title('Model Comparison')
    plt.ylabel('Score')
    plt.ylim(0, 1.0)
    plt.xticks(rotation=45)
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def plot_feature_importance(feature_names, importances, output_path, title='Feature Importance', top_k=30):
    indices = np.argsort(importances)[-top_k:]
    plt.figure(figsize=(10, 8))
    plt.barh(range(len(indices)), importances[indices], align='center')
    plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
    plt.xlabel('Importance')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def print_metrics(name, metrics):
    logger.info(f'=== {name} ===')
    logger.info(f'Accuracy:  {metrics.get( accuracy, 0):.4f}')
    logger.info(f'Precision: {metrics.get(precision, 0):.4f}')
    logger.info(f'Recall:    {metrics.get(recall, 0):.4f}')
    logger.info(f'F1-score:  {metrics.get(f1, 0):.4f}')
    if metrics.get('roc_auc') is not None:
        logger.info(f'ROC-AUC:   {metrics[roc_auc]:.4f}')
    logger.info(f'Specificity: {metrics.get(specificity, 0):.4f}')
    logger.info(f'FPR:       {metrics.get(fpr, 0):.4f}')
    logger.info(f'FNR:       {metrics.get(fnr, 0):.4f}')
    logger.info(f'Confusion Matrix: {metrics.get(confusion_matrix)}')
    logger.info('')