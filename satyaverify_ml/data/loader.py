import os
import sys
import logging
from pathlib import Path
import numpy as np
import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from satyaverify_ml.utils.helpers import VideoMetadata, FeatureVector, get_video_metadata, sample_frames, extract_audio
from satyaverify_ml.config import cfg

logger = logging.getLogger(__name__)


class SATYAVerifyDataset:
    def __init__(self, dataset_root: str):
        self.dataset_root = Path(dataset_root)
        self.real_dir = self.dataset_root / cfg.get('dataset', 'real_dir', default='videos_real')
        self.fake_dir = self.dataset_root / cfg.get('dataset', 'fake_dir', default='videos_fake')
        self.video_paths: list = []
        self._scan()

    def _scan(self):
        if self.real_dir.exists():
            for f in sorted(self.real_dir.glob('*.mp4')):
                self.video_paths.append((str(f), f.stem, 'REAL'))
        if self.fake_dir.exists():
            for f in sorted(self.fake_dir.glob('*.mp4')):
                self.video_paths.append((str(f), f.stem, 'DEEPFAKE'))
        logger.info(f'Found {len(self.video_paths)} videos')

    def get_source_ids(self):
        return [vid_id for _, vid_id, _ in self.video_paths]

    def split_by_source(self, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, random_seed=42):
        sources = [vid_id for _, vid_id, _ in self.video_paths]
        labels = [label for _, _, label in self.video_paths]
        label_to_sources = {}
        for s, l in zip(sources, labels):
            label_to_sources.setdefault(l, []).append(s)

        train_sources, val_sources, test_sources = [], [], []
        np.random.seed(random_seed)
        for label, srcs in label_to_sources.items():
            np.random.shuffle(srcs)
            n = len(srcs)
            n_train = int(n * train_ratio)
            n_val = int(n * val_ratio)
            train_sources.extend(srcs[:n_train])
            val_sources.extend(srcs[n_train: n_train + n_val])
            test_sources.extend(srcs[n_train + n_val:])

        logger.info(f'Split: train={len(train_sources)}, val={len(val_sources)}, test={len(test_sources)}')
        return train_sources, val_sources, test_sources

    def extract_all_features(self, split_names):
        split_data = {}
        for split, sources in split_names.items():
            feats = []
            for path, vid_id, label in self.video_paths:
                if vid_id in sources:
                    fv = self._extract_one(path, vid_id, label)
                    feats.append(fv)
            split_data[split] = feats
            logger.info(f'{split}: {len(feats)} feature vectors extracted')
        return split_data

    def _extract_one(self, path, vid_id, label):
        from satyaverify_ml.features import extract_video_features
        return extract_video_features(path, vid_id, label, manipulation_type='SDFVD')
