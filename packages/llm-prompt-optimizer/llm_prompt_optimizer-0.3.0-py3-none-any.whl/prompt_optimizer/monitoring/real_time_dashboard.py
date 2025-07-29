"""
Real-time dashboard for live monitoring of prompt experiments.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics to monitor."""
    QUALITY_SCORE = "quality_score"
    LATENCY = "latency"
    COST = "cost"
    CONVERSION_RATE = "conversion_rate"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    USER_SATISFACTION = "user_satisfaction"


class AlertLevel(str, Enum):
    """Alert levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricPoint:
    """A single metric data point."""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any]


@dataclass
class DashboardMetric:
    """A metric to display on the dashboard."""
    name: str
    metric_type: MetricType
    current_value: float
    previous_value: float
    change_percent: float
    trend: str  # "up", "down", "stable"
    data_points: List[MetricPoint]
    alert_level: AlertLevel


@dataclass
class ExperimentStatus:
    """Status of an experiment."""
    experiment_id: str
    name: str
    status: str
    total_tests: int
    successful_tests: int
    failed_tests: int
    current_traffic: Dict[str, int]
    best_variant: Optional[str]
    confidence_level: float
    estimated_completion: Optional[datetime]


class RealTimeDashboard:
    """Real-time dashboard for monitoring prompt experiments."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.metrics = defaultdict(lambda: deque(maxlen=1000))  # Keep last 1000 points
        self.experiments = {}
        self.subscribers = []
        self.running = False
        self.update_interval = self.config.get('update_interval', 5)  # seconds
        
    async def start(self):
        """Start the real-time dashboard."""
        self.running = True
        logger.info("Starting real-time dashboard")
        
        # Start background tasks
        asyncio.create_task(self._update_loop())
        asyncio.create_task(self._cleanup_loop())
        
    async def stop(self):
        """Stop the real-time dashboard."""
        self.running = False
        logger.info("Stopping real-time dashboard")
        
    async def _update_loop(self):
        """Main update loop for the dashboard."""
        while self.running:
            try:
                await self._update_metrics()
                await self._notify_subscribers()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in dashboard update loop: {e}")
                await asyncio.sleep(1)
                
    async def _cleanup_loop(self):
        """Cleanup old data periodically."""
        while self.running:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(300)  # Cleanup every 5 minutes
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)
                
    def add_metric_point(self, 
                        metric_name: str,
                        metric_type: MetricType,
                        value: float,
                        metadata: Optional[Dict[str, Any]] = None):
        """Add a new metric data point."""
        timestamp = datetime.now()
        point = MetricPoint(
            timestamp=timestamp,
            value=value,
            metadata=metadata or {}
        )
        
        self.metrics[metric_name].append(point)
        
        # Update experiment status if this is experiment-related
        if 'experiment_id' in metadata:
            # Schedule async update without blocking
            asyncio.create_task(self._update_experiment_status(metadata['experiment_id']))
            
    def update_experiment_status(self, experiment_id: str, status_data: Dict[str, Any]):
        """Update experiment status."""
        self.experiments[experiment_id] = ExperimentStatus(
            experiment_id=experiment_id,
            name=status_data.get('name', 'Unknown'),
            status=status_data.get('status', 'unknown'),
            total_tests=status_data.get('total_tests', 0),
            successful_tests=status_data.get('successful_tests', 0),
            failed_tests=status_data.get('failed_tests', 0),
            current_traffic=status_data.get('current_traffic', {}),
            best_variant=status_data.get('best_variant'),
            confidence_level=status_data.get('confidence_level', 0.0),
            estimated_completion=status_data.get('estimated_completion')
        )
        
    def subscribe(self, callback: Callable):
        """Subscribe to dashboard updates."""
        self.subscribers.append(callback)
        
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from dashboard updates."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            
    async def _notify_subscribers(self):
        """Notify all subscribers of updates."""
        dashboard_data = self.get_dashboard_data()
        
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(dashboard_data)
                else:
                    callback(dashboard_data)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
                
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data."""
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': self._get_metrics_summary(),
            'experiments': self._get_experiments_summary(),
            'alerts': self._get_active_alerts(),
            'system_health': self._get_system_health()
        }
        
    def _get_metrics_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all metrics."""
        summary = []
        
        for metric_name, data_points in self.metrics.items():
            if not data_points:
                continue
                
            # Calculate current and previous values
            current_point = data_points[-1]
            previous_point = data_points[-2] if len(data_points) > 1 else current_point
            
            current_value = current_point.value
            previous_value = previous_point.value
            
            # Calculate change percentage
            if previous_value != 0:
                change_percent = ((current_value - previous_value) / previous_value) * 100
            else:
                change_percent = 0.0
                
            # Determine trend
            if change_percent > 1.0:
                trend = "up"
            elif change_percent < -1.0:
                trend = "down"
            else:
                trend = "stable"
                
            # Determine alert level
            alert_level = self._determine_alert_level(metric_name, current_value, change_percent)
            
            summary.append({
                'name': metric_name,
                'current_value': current_value,
                'previous_value': previous_value,
                'change_percent': change_percent,
                'trend': trend,
                'alert_level': alert_level.value,
                'last_updated': current_point.timestamp.isoformat()
            })
            
        return summary
        
    def _get_experiments_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all experiments."""
        return [asdict(exp) for exp in self.experiments.values()]
        
    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts."""
        alerts = []
        
        for metric_name, data_points in self.metrics.items():
            if not data_points:
                continue
                
            current_value = data_points[-1].value
            alert_level = self._determine_alert_level(metric_name, current_value, 0)
            
            if alert_level in [AlertLevel.WARNING, AlertLevel.ERROR, AlertLevel.CRITICAL]:
                alerts.append({
                    'metric_name': metric_name,
                    'current_value': current_value,
                    'alert_level': alert_level.value,
                    'timestamp': data_points[-1].timestamp.isoformat(),
                    'message': self._generate_alert_message(metric_name, current_value, alert_level)
                })
                
        return alerts
        
    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        total_metrics = len(self.metrics)
        active_experiments = len([exp for exp in self.experiments.values() if exp.status == 'running'])
        
        # Calculate overall health score
        health_score = 100.0
        
        # Deduct points for alerts
        for metric_name, data_points in self.metrics.items():
            if not data_points:
                continue
            current_value = data_points[-1].value
            alert_level = self._determine_alert_level(metric_name, current_value, 0)
            
            if alert_level == AlertLevel.CRITICAL:
                health_score -= 20
            elif alert_level == AlertLevel.ERROR:
                health_score -= 10
            elif alert_level == AlertLevel.WARNING:
                health_score -= 5
                
        return {
            'overall_health': max(0, health_score),
            'total_metrics': total_metrics,
            'active_experiments': active_experiments,
            'last_updated': datetime.now().isoformat()
        }
        
    def _determine_alert_level(self, metric_name: str, value: float, change_percent: float) -> AlertLevel:
        """Determine alert level for a metric."""
        # Define thresholds based on metric type
        thresholds = self.config.get('alert_thresholds', {})
        
        if 'quality_score' in metric_name.lower():
            if value < 0.3:
                return AlertLevel.CRITICAL
            elif value < 0.5:
                return AlertLevel.ERROR
            elif value < 0.7:
                return AlertLevel.WARNING
                
        elif 'latency' in metric_name.lower():
            if value > 10000:  # 10 seconds
                return AlertLevel.CRITICAL
            elif value > 5000:  # 5 seconds
                return AlertLevel.ERROR
            elif value > 2000:  # 2 seconds
                return AlertLevel.WARNING
                
        elif 'cost' in metric_name.lower():
            if value > 100:  # $100
                return AlertLevel.CRITICAL
            elif value > 50:  # $50
                return AlertLevel.ERROR
            elif value > 20:  # $20
                return AlertLevel.WARNING
                
        elif 'error_rate' in metric_name.lower():
            if value > 0.1:  # 10%
                return AlertLevel.CRITICAL
            elif value > 0.05:  # 5%
                return AlertLevel.ERROR
            elif value > 0.02:  # 2%
                return AlertLevel.WARNING
                
        # Check for significant changes
        if abs(change_percent) > 50:
            return AlertLevel.WARNING
        elif abs(change_percent) > 100:
            return AlertLevel.ERROR
            
        return AlertLevel.INFO
        
    def _generate_alert_message(self, metric_name: str, value: float, alert_level: AlertLevel) -> str:
        """Generate alert message."""
        if alert_level == AlertLevel.CRITICAL:
            return f"CRITICAL: {metric_name} is at {value:.2f}"
        elif alert_level == AlertLevel.ERROR:
            return f"ERROR: {metric_name} is at {value:.2f}"
        elif alert_level == AlertLevel.WARNING:
            return f"WARNING: {metric_name} is at {value:.2f}"
        else:
            return f"INFO: {metric_name} is at {value:.2f}"
            
    async def _update_metrics(self):
        """Update metrics (placeholder for real implementation)."""
        # This would typically involve:
        # - Fetching latest data from database
        # - Calculating derived metrics
        # - Updating experiment statuses
        pass
        
    async def _update_experiment_status(self, experiment_id: str):
        """Update experiment status (placeholder)."""
        # This would fetch latest experiment status from database
        pass
        
    async def _cleanup_old_data(self):
        """Clean up old metric data."""
        cutoff_time = datetime.now() - timedelta(hours=24)  # Keep 24 hours
        
        for metric_name, data_points in self.metrics.items():
            # Remove old data points
            while data_points and data_points[0].timestamp < cutoff_time:
                data_points.popleft()
                
    def get_metric_history(self, 
                          metric_name: str,
                          hours: int = 24) -> List[MetricPoint]:
        """Get metric history for the specified time period."""
        if metric_name not in self.metrics:
            return []
            
        cutoff_time = datetime.now() - timedelta(hours=hours)
        data_points = self.metrics[metric_name]
        
        return [point for point in data_points if point.timestamp >= cutoff_time]
        
    def get_experiment_metrics(self, experiment_id: str) -> Dict[str, Any]:
        """Get metrics for a specific experiment."""
        experiment_metrics = {}
        
        for metric_name, data_points in self.metrics.items():
            # Filter for experiment-specific metrics
            experiment_points = [
                point for point in data_points
                if point.metadata.get('experiment_id') == experiment_id
            ]
            
            if experiment_points:
                experiment_metrics[metric_name] = {
                    'current_value': experiment_points[-1].value,
                    'data_points': [asdict(point) for point in experiment_points]
                }
                
        return experiment_metrics 