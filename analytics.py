from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from scipy.stats import gaussian_kde
import json
import logging
from typing import Dict, List, Any
import pandas as pd

logger = logging.getLogger(__name__)

class AnalyticsManager:
    def __init__(self):
        self.complaint_data = defaultdict(list)
        self.heatmap_data = []
        self.last_update = datetime.now()
    
    def process_location_data(self, complaints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate heatmap data from complaint locations"""
        locations = [(c['latitude'], c['longitude']) for c in complaints 
                    if c['latitude'] and c['longitude']]
        if not locations:
            return []
            
        try:
            kde = gaussian_kde(np.array(locations).T)
            xi, yi = np.mgrid[min(x[0] for x in locations):max(x[0] for x in locations):100j,
                             min(x[1] for x in locations):max(x[1] for x in locations):100j]
            zi = kde(np.vstack([xi.flatten(), yi.flatten()]))
            return [{
                'lat': float(x), 
                'lng': float(y), 
                'intensity': float(z)
            } for x, y, z in zip(xi.flatten(), yi.flatten(), zi)]
        except Exception as e:
            logger.error(f"Error generating heatmap: {e}")
            return []
    
    def generate_category_insights(self, complaints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze complaint categories and generate insights"""
        df = pd.DataFrame(complaints)
        insights = {
            'most_common': df['category'].mode().iloc[0] if not df.empty else None,
            'category_counts': df['category'].value_counts().to_dict(),
            'trends': {}
        }
        
        # Analyze weekly trends
        if not df.empty:
            df['created_at'] = pd.to_datetime(df['created_at'])
            weekly = df.set_index('created_at').resample('W')['category'].count()
            insights['trends']['weekly'] = {
                'dates': weekly.index.strftime('%Y-%m-%d').tolist(),
                'counts': weekly.values.tolist()
            }
        
        return insights
    
    def analyze_response_times(self, complaints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate response and resolution time statistics"""
        df = pd.DataFrame(complaints)
        if df.empty:
            return {}
            
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        df['resolution_time'] = (df['updated_at'] - df['created_at']).dt.total_seconds() / 3600
        
        return {
            'avg_resolution_hours': df['resolution_time'].mean(),
            'by_category': df.groupby('category')['resolution_time'].mean().to_dict(),
            'by_severity': df.groupby('severity')['resolution_time'].mean().to_dict()
        }
    
    async def generate_full_analytics(self, complaints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive analytics data"""
        try:
            heatmap_data = self.process_location_data(complaints)
            category_insights = self.generate_category_insights(complaints)
            response_stats = self.analyze_response_times(complaints)
            
            # Current status summary
            status_counts = defaultdict(int)
            for c in complaints:
                status_counts[c['status']] += 1
            
            return {
                'timestamp': datetime.now().isoformat(),
                'heatmap': heatmap_data,
                'category_insights': category_insights,
                'response_stats': response_stats,
                'status_summary': dict(status_counts),
                'total_complaints': len(complaints)
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_hotspots(self, complaints: List[Dict[str, Any]], threshold: float = 0.75) -> List[Dict[str, Any]]:
        """Identify complaint hotspots based on density"""
        locations = [(c['latitude'], c['longitude']) for c in complaints 
                    if c['latitude'] and c['longitude']]
        if not locations:
            return []
            
        try:
            kde = gaussian_kde(np.array(locations).T)
            densities = kde(np.array(locations).T)
            threshold_value = np.percentile(densities, threshold * 100)
            
            hotspots = []
            for (lat, lng), density in zip(locations, densities):
                if density > threshold_value:
                    nearby = [c for c in complaints 
                            if abs(c['latitude'] - lat) < 0.01 
                            and abs(c['longitude'] - lng) < 0.01]
                    hotspots.append({
                        'location': {'lat': lat, 'lng': lng},
                        'density': float(density),
                        'complaint_count': len(nearby),
                        'categories': list(set(c['category'] for c in nearby))
                    })
            
            return sorted(hotspots, key=lambda x: x['density'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error identifying hotspots: {e}")
            return []