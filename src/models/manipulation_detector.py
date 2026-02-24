import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats


class ManipulationDetector:
    def __init__(self):
        self.suspicious_threshold = 0.7
        
    def detect_all(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Run all manipulation detection checks"""
        results = df.copy()
        
        # Initialize risk scores
        results['manipulation_risk_score'] = 0.0
        results['risk_flags'] = ''
        
        flags_summary = {
            'spike_anomalies': 0,
            'ratio_anomalies': 0,
            'velocity_anomalies': 0,
            'total_flagged': 0
        }
        
        # Run detectors
        spike_flags = self._detect_engagement_spikes(df)
        ratio_flags = self._detect_abnormal_ratios(df)
        velocity_flags = self._detect_velocity_anomalies(df)
        
        # Combine flags
        for idx in df.index:
            flags = []
            risk = 0.0
            
            if idx in spike_flags:
                flags.append('SPIKE')
                risk += 0.3
                flags_summary['spike_anomalies'] += 1
                
            if idx in ratio_flags:
                flags.append('RATIO')
                risk += 0.3
                flags_summary['ratio_anomalies'] += 1
                
            if idx in velocity_flags:
                flags.append('VELOCITY')
                risk += 0.4
                flags_summary['velocity_anomalies'] += 1
            
            results.loc[idx, 'manipulation_risk_score'] = min(risk, 1.0)
            results.loc[idx, 'risk_flags'] = ', '.join(flags) if flags else 'Clean'
        
        flags_summary['total_flagged'] = (results['manipulation_risk_score'] > self.suspicious_threshold).sum()
        
        return results, flags_summary
    
    def _detect_engagement_spikes(self, df: pd.DataFrame) -> List[int]:
        """Detect sudden unusual spikes in engagement metrics"""
        flagged = []
        
        for metric in ['views', 'likes', 'comments']:
            if metric not in df.columns:
                continue
                
            values = pd.to_numeric(df[metric], errors='coerce').fillna(0)
            
            if len(values) < 10:
                continue
            
            # Calculate z-scores
            mean = values.mean()
            std = values.std()
            
            if std == 0:
                continue
                
            z_scores = np.abs((values - mean) / std)
            
            # Flag values > 3 standard deviations
            spike_idx = df.index[z_scores > 3].tolist()
            flagged.extend(spike_idx)
        
        return list(set(flagged))
    
    def _detect_abnormal_ratios(self, df: pd.DataFrame) -> List[int]:
        """Detect abnormal engagement ratios"""
        flagged = []
        
        # Check like-to-view ratio
        if 'views' in df.columns and 'likes' in df.columns:
            views = pd.to_numeric(df['views'], errors='coerce').fillna(1)
            likes = pd.to_numeric(df['likes'], errors='coerce').fillna(0)
            
            like_rate = likes / (views + 1)
            
            # Normal like rate: 1-10%
            # Flag if > 50% (suspiciously high) or < 0.1% with high views
            high_rate = (like_rate > 0.5) & (views > 1000)
            low_rate = (like_rate < 0.001) & (views > 10000)
            
            flagged.extend(df.index[high_rate | low_rate].tolist())
        
        # Check comment-to-like ratio
        if 'likes' in df.columns and 'comments' in df.columns:
            likes = pd.to_numeric(df['likes'], errors='coerce').fillna(1)
            comments = pd.to_numeric(df['comments'], errors='coerce').fillna(0)
            
            comment_rate = comments / (likes + 1)
            
            # Normal: 0.5-5%
            # Flag if > 20% (suspiciously high engagement)
            high_comment = (comment_rate > 0.2) & (likes > 100)
            
            flagged.extend(df.index[high_comment].tolist())
        
        return list(set(flagged))
    
    def _detect_velocity_anomalies(self, df: pd.DataFrame) -> List[int]:
        """Detect unusual velocity in engagement growth"""
        flagged = []
        
        if 'date' not in df.columns or 'views' not in df.columns:
            return flagged
        
        df_sorted = df.copy()
        df_sorted['date'] = pd.to_datetime(df_sorted['date'], errors='coerce')
        df_sorted = df_sorted.dropna(subset=['date']).sort_values('date')
        
        views = pd.to_numeric(df_sorted['views'], errors='coerce').fillna(0)
        
        if len(views) < 5:
            return flagged
        
        # Calculate rolling velocity (change rate)
        velocity = views.diff() / views.shift(1).replace(0, 1)
        
        # Flag sudden acceleration > 10x
        sudden_growth = velocity > 10
        
        flagged.extend(df_sorted.index[sudden_growth].tolist())
        
        return list(set(flagged))
    
    def get_risk_distribution(self, results: pd.DataFrame) -> Dict:
        """Get distribution of risk scores"""
        if 'manipulation_risk_score' not in results.columns:
            return {}
        
        scores = results['manipulation_risk_score']
        
        return {
            'low_risk': (scores < 0.3).sum(),
            'medium_risk': ((scores >= 0.3) & (scores < 0.7)).sum(),
            'high_risk': (scores >= 0.7).sum(),
            'mean_score': scores.mean(),
            'max_score': scores.max()
        }