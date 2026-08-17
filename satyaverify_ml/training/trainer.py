import os
import sys
import logging
from pathlib import Path
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from satyaverify_ml.data.loader import SATYAVerifyDataset
from satyaverify_ml.preprocessing import PreprocessingPipeline, features_to_arrays
from satyaverify_ml.models.random_forest import RandomForestModel
from satyaverify_ml.models.xgboost_model import XGBoostModel
from satyaverify_ml.models.svm_model import SVMModel
from satyaverify_ml.models.ensemble import HybridEnsemble
from satyaverify_ml.evaluation import compute_metrics, print_metrics, plot_confusion_matrix, plot_roc_curve, plot_precision_recall, plot_model_comparison, plot_feature_importance
from satyaverify_ml.config import cfg

logger = logging.getLogger(__name__)

def train_pipeline():
    dataset_root = str(Path(cfg.get('dataset', 'root')).resolve())
    logger.info(f'Dataset root: {dataset_root}')
    dataset = SATYAVerifyDataset(dataset_root)
    if len(dataset.video_paths) == 0:
        logger.error('No videos found. Check dataset path.')
        return
    train_src, val_src, test_src = dataset.split_by_source(
        train_ratio=cfg.get('split', 'train_ratio', default=0.7),
        val_ratio=cfg.get('split', 'val_ratio', default=0.15),
        test_ratio=cfg.get('split', 'test_ratio', default=0.15),
        random_seed=cfg.get('split', 'random_seed', default=42),
    )
    logger.info('Extracting features...')
    splits = {'train': train_src, 'val': val_src, 'test': test_src}
    split_data = dataset.extract_all_features(splits)
    X_train, feat_names, y_train = features_to_arrays(split_data['train'])
    X_val, _, y_val = features_to_arrays(split_data['val'])
    X_test, _, y_test = features_to_arrays(split_data['test'])
    if X_train.shape[0] == 0:
        logger.error('No training features extracted.')
        return
    logger.info(f'Feature matrix shapes: train={X_train.shape}, val={X_val.shape}, test={X_test.shape}')
    logger.info(f'Feature names count: {len(feat_names)}')
    pipeline = PreprocessingPipeline()
    X_train_proc = pipeline.fit(X_train, feat_names)
    X_val_proc = pipeline.transform(X_val) if X_val.shape[0] > 0 else X_val
    X_test_proc = pipeline.transform(X_test) if X_test.shape[0] > 0 else X_test
    models_output = Path(cfg.get('paths', 'models_dir', default='satyaverify_ml/models/artifacts'))
    plots_output = Path(cfg.get('paths', 'plots_dir', default='satyaverify_ml/output/plots'))
    models_output.mkdir(parents=True, exist_ok=True)
    plots_output.mkdir(parents=True, exist_ok=True)
    model_instances = {
        'RandomForest': RandomForestModel(),
        'XGBoost': XGBoostModel(),
        'SVM': SVMModel(),
    }
    results = {}
    best_model_name = None
    best_f1 = -1.0
    for name, model in model_instances.items():
        logger.info(f'Training {name}...')
        try:
            model.fit(X_train_proc, y_train)
            y_pred = model.predict(X_val_proc) if X_val_proc.shape[0] > 0 else model.predict(X_test_proc)
            y_true = y_val if y_val.shape[0] > 0 else y_test
            y_proba = model.predict_proba(X_val_proc) if X_val_proc.shape[0] > 0 else model.predict_proba(X_test_proc)
            y_proba_pos = y_proba[:, 1] if y_proba.shape[1] == 2 else None
            m = compute_metrics(y_true, y_pred, y_proba_pos)
            results[name] = m
            print_metrics(f'{name} (Validation)', m)
            model.save(str(models_output / f'{name.lower()}.pkl'))
            if m['f1'] > best_f1:
                best_f1 = m['f1']
                best_model_name = name
        except Exception as e:
            logger.error(f'Error training {name}: {e}', exc_info=True)
    try:
        ensemble = HybridEnsemble()
        ensemble.fit(X_train_proc, y_train)
        y_pred = ensemble.predict(X_val_proc) if X_val_proc.shape[0] > 0 else ensemble.predict(X_test_proc)
        y_true = y_val if y_val.shape[0] > 0 else y_test
        y_proba = ensemble.predict_proba(X_val_proc) if X_val_proc.shape[0] > 0 else ensemble.predict_proba(X_test_proc)
        y_proba_pos = y_proba[:, 1] if y_proba.shape[1] == 2 else None
        m = compute_metrics(y_true, y_pred, y_proba_pos)
        results['HybridEnsemble'] = m
        print_metrics('HybridEnsemble (Validation)', m)
        ensemble.save(str(models_output / 'ensemble.pkl'))
        if m['f1'] > best_f1:
            best_f1 = m['f1']
            best_model_name = 'HybridEnsemble'
    except Exception as e:
        logger.error(f'Error training ensemble: {e}', exc_info=True)
    logger.info(f'Best model: {best_model_name} with F1={best_f1:.4f}')
    if results:
        plot_model_comparison(results, str(plots_output / 'model_comparison.png'))
    try:
        rf_model = model_instances['RandomForest']
        if hasattr(rf_model.model, 'feature_importances_'):
            importances = rf_model.model.feature_importances_
            plot_feature_importance(feat_names, importances, str(plots_output / 'feature_importance.png'), top_k=30)
            top_idx = np.argsort(importances)[-10:]
            logger.info('Top 10 features (RF):')
            for idx in reversed(top_idx):
                logger.info(f'  {feat_names[idx]}: {importances[idx]:.4f}')
    except Exception as e:
        logger.warning(f'Could not extract feature importance: {e}')
    if X_test.shape[0] > 0:
        try:
            if best_model_name == 'HybridEnsemble':
                from sklearn.ensemble import VotingClassifier
                ensemble_model = VotingClassifier(
                    estimators=[('rf', model_instances['RandomForest'].model),
                                ('xgb', model_instances['XGBoost'].model),
                                ('svm', model_instances['SVM'].model)],
                    voting='soft',
                )
                ensemble_model.fit(X_train_proc, y_train)
                y_pred = ensemble_model.predict(X_test_proc)
                y_proba = ensemble_model.predict_proba(X_test_proc)
                y_proba_pos = y_proba[:, 1] if y_proba.shape[1] == 2 else None
            else:
                best_model = model_instances.get(best_model_name, model_instances['RandomForest'])
                y_pred = best_model.predict(X_test_proc)
                y_proba = best_model.predict_proba(X_test_proc)
                y_proba_pos = y_proba[:, 1] if y_proba.shape[1] == 2 else None
            test_m = compute_metrics(y_test, y_pred, y_proba_pos)
            print_metrics(f'{best_model_name} (Test)', test_m)
            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            le.fit(['REAL', 'DEEPFAKE'])
            labels = list(le.classes_)
            plot_confusion_matrix(np.array(test_m['confusion_matrix']), labels,
                                  str(plots_output / 'confusion_matrix_test.png'),
                                  title=f'Confusion Matrix - {best_model_name} (Test)')
            if y_proba_pos is not None:
                plot_roc_curve(y_test, y_proba_pos, str(plots_output / 'roc_curve_test.png'),
                               title=f'ROC Curve - {best_model_name} (Test)')
                plot_precision_recall(y_test, y_proba_pos, str(plots_output / 'pr_curve_test.png'),
                                      title=f'Precision-Recall - {best_model_name} (Test)')
        except Exception as e:
            logger.error(f'Error during test evaluation: {e}', exc_info=True)
    pipeline.save(str(models_output))
    report_path = plots_output / 'results_report.md'
    with open(report_path, 'w') as f:
        f.write('# SATYAVERIFY ML - Results Report\n\n')
        f.write('## Dataset\n')
        f.write(f'- Total videos: {len(dataset.video_paths)}\n')
        f.write(f'- Real: {sum(1 for _, _, l in dataset.video_paths if l == " REAL\)}\n')
 f.write(f'- Fake: {sum(1 for _, _, l in dataset.video_paths if l == \DEEPFAKE\)}\n\n')
 f.write('## Model Performance\n\n')
 for name, m in results.items():
 f.write(f'### {name}\n')
 f.write(f'- Accuracy: {m[accuracy]:.4f}\n')
 f.write(f'- Precision: {m[precision]:.4f}\n')
 f.write(f'- Recall: {m[recall]:.4f}\n')
 f.write(f'- F1: {m[f1]:.4f}\n')
 if m.get('roc_auc') is not None:
 f.write(f'- ROC-AUC: {m[roc_auc]:.4f}\n')
 f.write(f'- Specificity: {m[specificity]:.4f}\n')
 f.write(f'- FPR: {m[fpr]:.4f}\n')
 f.write(f'- FNR: {m[fnr]:.4f}\n\n')
 f.write('## Best Model\n')
 f.write(f'Best model on validation: **{best_model_name}** (F1={best_f1:.4f})\n')
 logger.info(f'Report saved to {report_path}')
 logger.info('Training pipeline completed.')

if __name__ == '__main__':
 logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
 train_pipeline()