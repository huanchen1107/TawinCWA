"""Data validation utilities."""

import pandas as pd
from typing import Dict, List, Any, Optional, Tuple

class DataValidator:
    """Validate government datasets for quality and completeness."""
    
    def __init__(self):
        self.validation_rules = {
            'min_rows': 1,
            'min_columns': 1,
            'max_missing_percentage': 90,
            'required_columns': []
        }
    
    def validate_dataset(self, df: pd.DataFrame, rules: Optional[Dict] = None) -> Tuple[bool, List[str]]:
        """Validate dataset against quality rules."""
        if df is None:
            return False, ["Dataset is None"]
        
        if df.empty:
            return False, ["Dataset is empty"]
        
        validation_rules = {**self.validation_rules, **(rules or {})}
        issues = []
        
        # Check minimum rows
        if len(df) < validation_rules['min_rows']:
            issues.append(f"Dataset has only {len(df)} rows, minimum required: {validation_rules['min_rows']}")
        
        # Check minimum columns
        if len(df.columns) < validation_rules['min_columns']:
            issues.append(f"Dataset has only {len(df.columns)} columns, minimum required: {validation_rules['min_columns']}")
        
        # Check missing data percentage
        missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_percentage > validation_rules['max_missing_percentage']:
            issues.append(f"Dataset has {missing_percentage:.1f}% missing values, maximum allowed: {validation_rules['max_missing_percentage']}%")
        
        # Check required columns
        for col in validation_rules['required_columns']:
            if col not in df.columns:
                issues.append(f"Required column '{col}' is missing")
        
        return len(issues) == 0, issues
    
    def get_data_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate data quality score (0-100)."""
        if df is None or df.empty:
            return 0.0
        
        score = 100.0
        
        # Deduct points for missing values
        missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        score -= missing_percentage * 0.5
        
        # Deduct points for duplicate rows
        duplicate_percentage = (df.duplicated().sum() / len(df)) * 100
        score -= duplicate_percentage * 0.3
        
        # Deduct points for columns with all same values
        constant_cols = sum(1 for col in df.columns if df[col].nunique() <= 1)
        constant_percentage = (constant_cols / len(df.columns)) * 100
        score -= constant_percentage * 0.2
        
        return max(0.0, min(100.0, score))
    
    def check_data_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for data consistency issues."""
        issues = {
            'inconsistent_formats': [],
            'outliers': [],
            'invalid_values': []
        }
        
        if df is None or df.empty:
            return issues
        
        for col in df.columns:
            # Check for inconsistent date formats
            if df[col].dtype == 'object':
                sample_values = df[col].dropna().astype(str).head(100)
                if self._has_mixed_date_formats(sample_values):
                    issues['inconsistent_formats'].append(f"Column '{col}' has mixed date formats")
            
            # Check for outliers in numeric columns
            elif pd.api.types.is_numeric_dtype(df[col]):
                outliers = self._detect_outliers(df[col])
                if len(outliers) > 0:
                    issues['outliers'].append(f"Column '{col}' has {len(outliers)} potential outliers")
        
        return issues
    
    def _has_mixed_date_formats(self, values: pd.Series) -> bool:
        """Check if values have mixed date formats."""
        import re
        
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]
        
        pattern_counts = {pattern: 0 for pattern in date_patterns}
        
        for value in values:
            for pattern in date_patterns:
                if re.match(pattern, str(value).strip()):
                    pattern_counts[pattern] += 1
                    break
        
        # If more than one pattern is found, there are mixed formats
        active_patterns = sum(1 for count in pattern_counts.values() if count > 0)
        return active_patterns > 1
    
    def _detect_outliers(self, series: pd.Series, threshold: float = 3.0) -> List[int]:
        """Detect outliers using Z-score method."""
        if series.empty or not pd.api.types.is_numeric_dtype(series):
            return []
        
        # Calculate Z-scores
        mean = series.mean()
        std = series.std()
        
        if std == 0:  # No variation
            return []
        
        z_scores = abs((series - mean) / std)
        outlier_indices = z_scores[z_scores > threshold].index.tolist()
        
        return outlier_indices