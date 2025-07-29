"""
FastAPI server for prompt optimization API - RapidAPI Ready.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn
import logging
import asyncio
from datetime import datetime

from ..core.optimizer import PromptOptimizer
from ..types import (
    ProviderType, 
    ExperimentConfig, 
    OptimizationConfig,
    PromptVariant,
    TestResult,
    AnalysisReport,
    OptimizedPrompt,
    Experiment,
    TestStatus,
    OptimizerConfig
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global optimizer instance
optimizer: Optional[PromptOptimizer] = None

def get_optimizer() -> PromptOptimizer:
    """Get the global optimizer instance."""
    if optimizer is None:
        raise HTTPException(status_code=500, detail="Optimizer not initialized")
    return optimizer

# Request/Response Models for API
class CreateExperimentRequest(BaseModel):
    name: str = Field(..., description="Name of the experiment")
    description: Optional[str] = Field(None, description="Description of the experiment")
    variants: List[Dict[str, Any]] = Field(..., description="List of prompt variants")
    config: Dict[str, Any] = Field(..., description="Experiment configuration")

class TestPromptRequest(BaseModel):
    experiment_id: str = Field(..., description="ID of the experiment")
    user_id: str = Field(..., description="User ID for consistent assignment")
    input_data: Dict[str, Any] = Field(..., description="Input data for the prompt")

class OptimizePromptRequest(BaseModel):
    base_prompt: str = Field(..., description="Base prompt to optimize")
    optimization_config: Dict[str, Any] = Field(default_factory=dict, description="Optimization configuration")

class ContentSafetyRequest(BaseModel):
    content: str = Field(..., description="Content to check for safety")

class BiasDetectionRequest(BaseModel):
    text: str = Field(..., description="Text to check for bias")

class InjectionDetectionRequest(BaseModel):
    prompt: str = Field(..., description="Prompt to check for injection attacks")

class ComplianceCheckRequest(BaseModel):
    experiment_id: str = Field(..., description="Experiment ID to check for compliance")

class ABTestRequest(BaseModel):
    experiment_id: str = Field(..., description="Experiment ID to run A/B test on")
    sample_size: int = Field(default=100, description="Sample size for the test")

class SignificanceRequest(BaseModel):
    experiment_id: str = Field(..., description="Experiment ID")
    variant_a: str = Field(..., description="First variant name")
    variant_b: str = Field(..., description="Second variant name")

class APIResponse(BaseModel):
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Factory to create the FastAPI app with a config
def create_app(config: Optional[OptimizerConfig] = None):
    global optimizer
    
    if config is None:
        config = OptimizerConfig()
    
    optimizer = PromptOptimizer(config)
    
    app = FastAPI(
        title="LLM Prompt Optimizer API",
        description="""
        A comprehensive API for systematic A/B testing and optimization of LLM prompts.
        
        ## Features
        - **A/B Testing**: Create and run experiments with multiple prompt variants
        - **Prompt Optimization**: Use genetic algorithms to optimize prompts
        - **Analytics**: Get detailed analysis reports with statistical significance
        - **Multi-Provider Support**: Works with OpenAI, Anthropic, Google, and more
        - **Cost Tracking**: Monitor API costs and token usage
        - **Quality Scoring**: Automated quality assessment of responses
        
        ## Quick Start
        1. Create an experiment with your prompt variants
        2. Start the experiment to begin data collection
        3. Test prompts with your input data
        4. Analyze results to find the best performing variant
        5. Optimize prompts using genetic algorithms
        
        ## Authentication
        Set your API keys in the request headers or use the configuration endpoint.
        """,
        version="0.1.1",
        contact={
            "name": "Sherin Joseph Roy",
            "email": "sherin.joseph2217@gmail.com",
            "url": "https://github.com/Sherin-SEF-AI/prompt-optimizer.git",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", response_model=APIResponse)
    async def root():
        """Root endpoint with API information."""
        return APIResponse(
            success=True,
            data={
                "api_name": "LLM Prompt Optimizer API",
                "version": "0.1.1",
                "author": "Sherin Joseph Roy",
                "email": "sherin.joseph2217@gmail.com",
                "github": "https://github.com/Sherin-SEF-AI/prompt-optimizer.git",
                "pypi": "https://pypi.org/project/llm-prompt-optimizer/",
                "linkedin": "https://www.linkedin.com/in/sherin-roy-deepmost/",
                "docs": "/docs",
                "endpoints": {
                    "experiments": "/api/v1/experiments",
                    "optimization": "/api/v1/optimize",
                    "analytics": "/api/v1/analytics",
                    "health": "/health"
                }
            },
            message="LLM Prompt Optimizer API is running"
        )

    @app.get("/health", response_model=APIResponse)
    async def health_check():
        """Health check endpoint."""
        return APIResponse(
            success=True,
            data={"status": "healthy", "service": "llm-prompt-optimizer"},
            message="Service is healthy"
        )

    # Experiment Management Endpoints
    @app.post("/api/v1/experiments", response_model=APIResponse)
    async def create_experiment(request: CreateExperimentRequest):
        """Create a new A/B test experiment."""
        try:
            opt = get_optimizer()
            # Convert request to proper types
            variants = [PromptVariant(**variant) for variant in request.variants]
            config = ExperimentConfig(**request.config)
            
            experiment = await opt.create_experiment(
                name=request.name,
                variants=variants,
                config=config
            )
            
            return APIResponse(
                success=True,
                data={
                    "experiment_id": experiment.id,
                    "name": experiment.name,
                    "status": experiment.status,
                    "variants": [{"name": v.name, "template": v.template} for v in experiment.variants],
                    "created_at": experiment.created_at.isoformat()
                },
                message=f"Experiment '{request.name}' created successfully"
            )
        except Exception as e:
            logger.error(f"Error creating experiment: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/api/v1/experiments/{experiment_id}/start", response_model=APIResponse)
    async def start_experiment(experiment_id: str):
        """Start an experiment."""
        try:
            opt = get_optimizer()
            await opt.start_experiment(experiment_id)
            return APIResponse(
                success=True,
                data={"experiment_id": experiment_id, "status": "running"},
                message=f"Experiment {experiment_id} started successfully"
            )
        except Exception as e:
            logger.error(f"Error starting experiment: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/api/v1/experiments/{experiment_id}/stop", response_model=APIResponse)
    async def stop_experiment(experiment_id: str):
        """Stop an experiment."""
        try:
            opt = get_optimizer()
            await opt.stop_experiment(experiment_id)
            return APIResponse(
                success=True,
                data={"experiment_id": experiment_id, "status": "stopped"},
                message=f"Experiment {experiment_id} stopped successfully"
            )
        except Exception as e:
            logger.error(f"Error stopping experiment: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/experiments", response_model=APIResponse)
    async def list_experiments():
        """List all experiments."""
        try:
            opt = get_optimizer()
            experiments = await opt.list_experiments()
            return APIResponse(
                success=True,
                data={
                    "experiments": [
                        {
                            "id": exp.id,
                            "name": exp.name,
                            "status": exp.status,
                            "variants_count": len(exp.variants),
                            "created_at": exp.created_at.isoformat(),
                            "started_at": exp.started_at.isoformat() if exp.started_at else None
                        }
                        for exp in experiments
                    ]
                },
                message=f"Found {len(experiments)} experiments"
            )
        except Exception as e:
            logger.error(f"Error listing experiments: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/experiments/{experiment_id}", response_model=APIResponse)
    async def get_experiment(experiment_id: str):
        """Get experiment details."""
        try:
            opt = get_optimizer()
            experiments = await opt.list_experiments()
            experiment = next((exp for exp in experiments if exp.id == experiment_id), None)
            
            if not experiment:
                raise HTTPException(status_code=404, detail="Experiment not found")
            
            return APIResponse(
                success=True,
                data={
                    "id": experiment.id,
                    "name": experiment.name,
                    "description": experiment.description,
                    "status": experiment.status,
                    "variants": [
                        {
                            "name": v.name,
                            "template": v.template,
                            "parameters": v.parameters,
                            "version": v.version
                        }
                        for v in experiment.variants
                    ],
                    "config": experiment.config.dict(),
                    "created_at": experiment.created_at.isoformat(),
                    "started_at": experiment.started_at.isoformat() if experiment.started_at else None,
                    "completed_at": experiment.completed_at.isoformat() if experiment.completed_at else None
                },
                message=f"Experiment {experiment_id} details retrieved"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting experiment: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    # Testing Endpoints
    @app.post("/api/v1/test", response_model=APIResponse)
    async def test_prompt(request: TestPromptRequest):
        """Test a prompt for a specific experiment."""
        try:
            opt = get_optimizer()
            result = await opt.test_prompt(
                experiment_id=request.experiment_id,
                user_id=request.user_id,
                input_data=request.input_data
            )
            
            return APIResponse(
                success=True,
                data={
                    "experiment_id": result.experiment_id,
                    "variant_name": result.variant_name,
                    "user_id": result.user_id,
                    "response": result.response,
                    "quality_score": result.quality_score,
                    "latency_ms": result.latency_ms,
                    "cost_usd": result.cost_usd,
                    "tokens_used": result.tokens_used,
                    "timestamp": result.timestamp.isoformat()
                },
                message="Prompt test completed successfully"
            )
        except Exception as e:
            logger.error(f"Error testing prompt: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    # Analytics Endpoints
    @app.get("/api/v1/experiments/{experiment_id}/analyze", response_model=APIResponse)
    async def analyze_experiment(experiment_id: str):
        """Analyze an experiment and get results."""
        try:
            opt = get_optimizer()
            report = await opt.analyze_experiment(experiment_id)
            
            return APIResponse(
                success=True,
                data={
                    "experiment_id": report.experiment_id,
                    "status": report.status,
                    "best_variant": report.best_variant,
                    "confidence_level": report.confidence_level,
                    "total_samples": report.total_samples,
                    "duration_days": report.duration_days,
                    "significance_results": [
                        {
                            "variant_a": result.variant_a,
                            "variant_b": result.variant_b,
                            "is_significant": result.is_significant,
                            "p_value": result.p_value,
                            "effect_size": result.effect_size
                        }
                        for result in report.significance_results
                    ],
                    "metrics_summary": report.metrics_summary,
                    "recommendations": report.recommendations,
                    "created_at": report.created_at.isoformat()
                },
                message=f"Analysis completed for experiment {experiment_id}"
            )
        except Exception as e:
            logger.error(f"Error analyzing experiment: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/experiments/{experiment_id}/results", response_model=APIResponse)
    async def get_experiment_results(experiment_id: str):
        """Get all test results for an experiment."""
        try:
            opt = get_optimizer()
            results = await opt.get_experiment_results(experiment_id)
            
            return APIResponse(
                success=True,
                data={
                    "experiment_id": experiment_id,
                    "results": [
                        {
                            "variant_name": result.variant_name,
                            "user_id": result.user_id,
                            "response": result.response,
                            "quality_score": result.quality_score,
                            "latency_ms": result.latency_ms,
                            "cost_usd": result.cost_usd,
                            "tokens_used": result.tokens_used,
                            "timestamp": result.timestamp.isoformat()
                        }
                        for result in results
                    ],
                    "total_results": len(results)
                },
                message=f"Retrieved {len(results)} results for experiment {experiment_id}"
            )
        except Exception as e:
            logger.error(f"Error getting experiment results: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    # Optimization Endpoints
    @app.post("/api/v1/optimize", response_model=APIResponse)
    async def optimize_prompt(request: OptimizePromptRequest):
        """Optimize a prompt using genetic algorithms."""
        try:
            opt = get_optimizer()
            config = OptimizationConfig(**request.optimization_config)
            
            optimized = await opt.optimize_prompt(
                base_prompt=request.base_prompt,
                optimization_config=config
            )
            
            return APIResponse(
                success=True,
                data={
                    "original_prompt": optimized.original_prompt,
                    "optimized_prompt": optimized.optimized_prompt,
                    "improvement_score": optimized.improvement_score,
                    "metrics_improvement": optimized.metrics_improvement,
                    "optimization_history": optimized.optimization_history,
                    "created_at": optimized.created_at.isoformat()
                },
                message="Prompt optimization completed successfully"
            )
        except Exception as e:
            logger.error(f"Error optimizing prompt: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    # Export Endpoints
    @app.get("/api/v1/experiments/{experiment_id}/export")
    async def export_results(experiment_id: str, format: str = "csv"):
        """Export experiment results."""
        try:
            if format not in ["csv", "json"]:
                raise HTTPException(status_code=400, detail="Format must be 'csv' or 'json'")
            
            opt = get_optimizer()
            export_data = await opt.export_results(experiment_id, format)
            
            return JSONResponse(
                content={
                    "success": True,
                    "data": export_data,
                    "message": f"Results exported in {format.upper()} format",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error exporting results: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    # Configuration Endpoints
    @app.get("/api/v1/config", response_model=APIResponse)
    async def get_config():
        """Get current configuration."""
        try:
            opt = get_optimizer()
            return APIResponse(
                success=True,
                data={
                    "database_url": opt.config.database_url,
                    "default_provider": opt.config.default_provider,
                    "max_concurrent_tests": opt.config.max_concurrent_tests,
                    "cache_ttl": opt.config.cache_ttl,
                    "log_level": opt.config.log_level,
                    "providers": list(opt.providers.keys())
                },
                message="Configuration retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    # Monitoring Endpoints
    @app.get("/api/v1/monitoring/dashboard", response_model=APIResponse)
    async def get_dashboard_data():
        """Get real-time dashboard data."""
        try:
            opt = get_optimizer()
            # Import monitoring module
            from ..monitoring.real_time_dashboard import RealTimeDashboard
            
            dashboard = RealTimeDashboard(opt)
            data = await dashboard.get_dashboard_data()
            
            return APIResponse(
                success=True,
                data=data,
                message="Dashboard data retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/monitoring/metrics", response_model=APIResponse)
    async def get_system_metrics():
        """Get system performance metrics."""
        try:
            opt = get_optimizer()
            from ..analytics.performance import PerformanceAnalyzer
            
            analyzer = PerformanceAnalyzer(opt)
            metrics = await analyzer.get_system_metrics()
            
            return APIResponse(
                success=True,
                data=metrics,
                message="System metrics retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    # Analytics Endpoints
    @app.get("/api/v1/analytics/cost-summary", response_model=APIResponse)
    async def get_cost_summary():
        """Get cost tracking summary."""
        try:
            opt = get_optimizer()
            from ..analytics.cost_tracker import CostTracker
            
            tracker = CostTracker(opt)
            summary = await tracker.get_cost_summary()
            
            return APIResponse(
                success=True,
                data=summary,
                message="Cost summary retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error getting cost summary: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/analytics/quality-report", response_model=APIResponse)
    async def get_quality_report():
        """Get quality scoring report."""
        try:
            opt = get_optimizer()
            from ..analytics.quality_scorer import QualityScorer
            
            scorer = QualityScorer(opt)
            report = await scorer.generate_quality_report()
            
            return APIResponse(
                success=True,
                data=report,
                message="Quality report generated successfully"
            )
        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/analytics/generate-report", response_model=APIResponse)
    async def generate_analytics_report(experiment_id: str, report_type: str = "comprehensive"):
        """Generate a comprehensive analytics report."""
        try:
            opt = get_optimizer()
            from ..analytics.reports import ReportGenerator
            
            generator = ReportGenerator(opt)
            report = await generator.generate_report(experiment_id, report_type)
            
            return APIResponse(
                success=True,
                data=report,
                message=f"{report_type.capitalize()} report generated successfully"
            )
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    # Security Endpoints
    @app.post("/api/v1/security/check-content", response_model=APIResponse)
    async def check_content_safety(request: ContentSafetyRequest):
        """Check content for safety and compliance."""
        try:
            opt = get_optimizer()
            from ..security.content_moderator import ContentModerator
            
            moderator = ContentModerator(opt)
            result = await moderator.check_content(request.content)
            
            return APIResponse(
                success=True,
                data=result,
                message="Content safety check completed"
            )
        except Exception as e:
            logger.error(f"Error checking content safety: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/api/v1/security/detect-bias", response_model=APIResponse)
    async def detect_bias(request: BiasDetectionRequest):
        """Detect bias in text content."""
        try:
            opt = get_optimizer()
            from ..security.bias_detector import BiasDetector
            
            detector = BiasDetector(opt)
            result = await detector.detect_bias(request.text)
            
            return APIResponse(
                success=True,
                data=result,
                message="Bias detection completed"
            )
        except Exception as e:
            logger.error(f"Error detecting bias: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/api/v1/security/check-injection", response_model=APIResponse)
    async def check_injection_attack(request: InjectionDetectionRequest):
        """Check for prompt injection attacks."""
        try:
            opt = get_optimizer()
            from ..security.injection_detector import InjectionDetector
            
            detector = InjectionDetector(opt)
            result = await detector.detect_injection(request.prompt)
            
            return APIResponse(
                success=True,
                data=result,
                message="Injection attack check completed"
            )
        except Exception as e:
            logger.error(f"Error checking for injection attacks: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/security/audit-logs", response_model=APIResponse)
    async def get_audit_logs(limit: int = 100, offset: int = 0):
        """Get security audit logs."""
        try:
            opt = get_optimizer()
            from ..security.audit_logger import AuditLogger
            
            logger_instance = AuditLogger(opt)
            logs = await logger_instance.get_logs(limit=limit, offset=offset)
            
            return APIResponse(
                success=True,
                data={"logs": logs, "total": len(logs)},
                message="Audit logs retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/api/v1/security/compliance-check", response_model=APIResponse)
    async def check_compliance(request: ComplianceCheckRequest):
        """Check experiment compliance with security policies."""
        try:
            opt = get_optimizer()
            from ..security.compliance_checker import ComplianceChecker
            
            checker = ComplianceChecker(opt)
            result = await checker.check_experiment_compliance(request.experiment_id)
            
            return APIResponse(
                success=True,
                data=result,
                message="Compliance check completed"
            )
        except Exception as e:
            logger.error(f"Error checking compliance: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    # Advanced Analytics Endpoints
    @app.get("/api/v1/analytics/predictive", response_model=APIResponse)
    async def get_predictive_analytics(experiment_id: str):
        """Get predictive analytics for an experiment."""
        try:
            opt = get_optimizer()
            from ..analytics.advanced.predictive_analytics import PredictiveAnalytics
            
            analytics = PredictiveAnalytics(opt)
            predictions = await analytics.generate_predictions(experiment_id)
            
            return APIResponse(
                success=True,
                data=predictions,
                message="Predictive analytics generated successfully"
            )
        except Exception as e:
            logger.error(f"Error generating predictive analytics: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    # Testing Endpoints
    @app.post("/api/v1/testing/ab-test", response_model=APIResponse)
    async def run_ab_test(request: ABTestRequest):
        """Run A/B test with specified sample size."""
        try:
            opt = get_optimizer()
            from ..testing.ab_test import ABTestRunner
            
            runner = ABTestRunner(opt)
            results = await runner.run_test(request.experiment_id, request.sample_size)
            
            return APIResponse(
                success=True,
                data=results,
                message="A/B test completed successfully"
            )
        except Exception as e:
            logger.error(f"Error running A/B test: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/testing/significance", response_model=APIResponse)
    async def calculate_significance(experiment_id: str, variant_a: str, variant_b: str):
        """Calculate statistical significance between two variants."""
        try:
            opt = get_optimizer()
            from ..testing.significance import SignificanceCalculator
            
            calculator = SignificanceCalculator(opt)
            result = await calculator.calculate_significance(experiment_id, variant_a, variant_b)
            
            return APIResponse(
                success=True,
                data=result,
                message="Statistical significance calculated successfully"
            )
        except Exception as e:
            logger.error(f"Error calculating significance: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    # Error handlers
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error="Endpoint not found",
                timestamp=datetime.utcnow()
            ).dict()
        )

    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal server error",
                timestamp=datetime.utcnow()
            ).dict()
        )

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 