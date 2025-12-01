"""Data processing utilities for government datasets."""

import pandas as pd
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

class DataProcessor:
    """Process and clean government data for analysis."""
    
    def __init__(self):
        self.logger = logging.getLogger("data_processor")
    
    def standardize_dataset(self, data: Any, source: str) -> Optional[pd.DataFrame]:
        """Convert various data formats to standardized DataFrame."""
        try:
            if isinstance(data, dict):
                # Handle JSON data
                if 'data' in data:
                    return pd.DataFrame(data['data'])
                elif 'results' in data:
                    return pd.DataFrame(data['results'])
                else:
                    return pd.DataFrame([data])
            
            elif isinstance(data, list):
                # Handle list of records
                if data and isinstance(data[0], dict):
                    return pd.DataFrame(data)
                else:
                    return pd.DataFrame({'values': data})
            
            elif isinstance(data, str):
                # Try to parse as CSV or JSON
                try:
                    # Try JSON first
                    json_data = json.loads(data)
                    return self.standardize_dataset(json_data, source)
                except:
                    # Try CSV
                    from io import StringIO
                    return pd.read_csv(StringIO(data))
            
            else:
                self.logger.warning(f"Unknown data format for source {source}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to standardize dataset: {e}")
            return None
    
    def clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare dataset for analysis."""
        if df is None or df.empty:
            return df
        
        try:
            # Remove completely empty rows and columns
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # Clean column names
            df.columns = [self._clean_column_name(col) for col in df.columns]
            
            # Remove duplicate rows
            df = df.drop_duplicates()
            
            # Convert date columns
            df = self._convert_date_columns(df)
            
            # Convert numeric columns
            df = self._convert_numeric_columns(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to clean dataset: {e}")
            return df
    
    def _clean_column_name(self, name: str) -> str:
        """Clean and standardize column names."""
        if not isinstance(name, str):
            return str(name)
        
        # Remove special characters and normalize
        clean_name = re.sub(r'[^\w\s]', '_', name)
        clean_name = re.sub(r'\s+', '_', clean_name)
        clean_name = clean_name.strip('_').lower()
        
        # Remove consecutive underscores
        clean_name = re.sub(r'_+', '_', clean_name)
        
        return clean_name
    
    def _convert_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Attempt to convert date-like columns to datetime."""
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if column contains date-like strings
                sample_values = df[col].dropna().astype(str).head(5)
                if self._is_date_column(sample_values):
                    try:
                        df[col] = pd.to_datetime(df[col], errors='ignore')
                    except:
                        pass
        return df
    
    def _is_date_column(self, values: pd.Series) -> bool:
        """Check if values look like dates."""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]
        
        for value in values:
            value_str = str(value).strip()
            if any(re.match(pattern, value_str) for pattern in date_patterns):
                return True
        return False
    
    def _convert_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert numeric columns to appropriate types."""
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric
                numeric_col = pd.to_numeric(df[col], errors='ignore')
                if not numeric_col.equals(df[col]):
                    df[col] = numeric_col
        return df
    
    def get_dataset_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for a dataset."""
        if df is None or df.empty:
            return {}
        
        try:
            summary = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values': df.isnull().sum().sum(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'column_info': {}
            }
            
            for col in df.columns:
                col_info = {
                    'dtype': str(df[col].dtype),
                    'non_null_count': df[col].count(),
                    'unique_values': df[col].nunique(),
                    'missing_count': df[col].isnull().sum()
                }
                
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_info.update({
                        'mean': float(df[col].mean()) if pd.notna(df[col].mean()) else None,
                        'std': float(df[col].std()) if pd.notna(df[col].std()) else None,
                        'min': float(df[col].min()) if pd.notna(df[col].min()) else None,
                        'max': float(df[col].max()) if pd.notna(df[col].max()) else None
                    })
                
                elif pd.api.types.is_datetime64_any_dtype(df[col]):
                    col_info.update({
                        'min_date': str(df[col].min()) if pd.notna(df[col].min()) else None,
                        'max_date': str(df[col].max()) if pd.notna(df[col].max()) else None
                    })
                
                summary['column_info'][col] = col_info
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate dataset summary: {e}")
            return {}
    
    def filter_dataset(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to dataset."""
        if df is None or df.empty:
            return df
        
        try:
            filtered_df = df.copy()
            
            for column, filter_value in filters.items():
                if column not in df.columns:
                    continue
                
                if isinstance(filter_value, str) and filter_value:
                    # Text search (case-insensitive)
                    mask = df[column].astype(str).str.contains(
                        filter_value, case=False, na=False
                    )
                    filtered_df = filtered_df[mask]
                
                elif isinstance(filter_value, (list, tuple)) and len(filter_value) == 2:
                    # Range filter for numeric columns
                    min_val, max_val = filter_value
                    if pd.api.types.is_numeric_dtype(df[column]):
                        mask = (df[column] >= min_val) & (df[column] <= max_val)
                        filtered_df = filtered_df[mask]
            
            return filtered_df
            
        except Exception as e:
            self.logger.error(f"Failed to filter dataset: {e}")
            return df
    
    def export_dataset(self, df: pd.DataFrame, format: str, filename: str) -> str:
        """Export dataset to specified format."""
        if df is None or df.empty:
            raise ValueError("Cannot export empty dataset")
        
        try:
            if format.lower() == 'csv':
                filepath = f"{filename}.csv"
                df.to_csv(filepath, index=False)
            
            elif format.lower() == 'excel':
                filepath = f"{filename}.xlsx"
                df.to_excel(filepath, index=False)
            
            elif format.lower() == 'json':
                filepath = f"{filename}.json"
                df.to_json(filepath, orient='records', indent=2)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to export dataset: {e}")
            raise