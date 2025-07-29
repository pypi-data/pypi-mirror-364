"""
Streamlit integration for interactive prompt optimization interface.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

# Import prompt optimizer components
from prompt_optimizer import PromptOptimizer
from prompt_optimizer.types import OptimizerConfig, ExperimentConfig, ProviderType, PromptVariant
from prompt_optimizer.security import ContentModerator, BiasDetector, InjectionDetector
from prompt_optimizer.analytics.advanced import PredictiveAnalytics
from prompt_optimizer.monitoring import RealTimeDashboard


class StreamlitApp:
    """Streamlit application for prompt optimization."""
    
    def __init__(self):
        self.optimizer = None
        self.dashboard = None
        self.predictive_analytics = None
        self.security_tools = {}
        
    def run(self):
        """Run the Streamlit application."""
        st.set_page_config(
            page_title="LLM Prompt Optimizer",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize components
        self._initialize_components()
        
        # Sidebar navigation
        page = st.sidebar.selectbox(
            "Navigation",
            ["Dashboard", "Experiments", "Prompt Testing", "Security Analysis", "Optimization", "Analytics"]
        )
        
        # Page routing
        if page == "Dashboard":
            self._show_dashboard()
        elif page == "Experiments":
            self._show_experiments()
        elif page == "Prompt Testing":
            self._show_prompt_testing()
        elif page == "Security Analysis":
            self._show_security_analysis()
        elif page == "Optimization":
            self._show_optimization()
        elif page == "Analytics":
            self._show_analytics()
            
    def _initialize_components(self):
        """Initialize optimizer and other components."""
        if 'optimizer' not in st.session_state:
            config = OptimizerConfig(
                database_url="sqlite:///prompt_optimizer.db",
                default_provider=ProviderType.OPENAI
            )
            st.session_state.optimizer = PromptOptimizer(config)
            
        if 'dashboard' not in st.session_state:
            st.session_state.dashboard = RealTimeDashboard()
            
        if 'predictive_analytics' not in st.session_state:
            st.session_state.predictive_analytics = PredictiveAnalytics()
            
        if 'security_tools' not in st.session_state:
            st.session_state.security_tools = {
                'content_moderator': ContentModerator(),
                'bias_detector': BiasDetector(),
                'injection_detector': InjectionDetector()
            }
            
        self.optimizer = st.session_state.optimizer
        self.dashboard = st.session_state.dashboard
        self.predictive_analytics = st.session_state.predictive_analytics
        self.security_tools = st.session_state.security_tools
        
    def _show_dashboard(self):
        """Show the main dashboard."""
        st.title("🚀 LLM Prompt Optimizer Dashboard")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Active Experiments",
                value=len(self._get_active_experiments()),
                delta="+2"
            )
            
        with col2:
            st.metric(
                label="Total Tests",
                value=self._get_total_tests(),
                delta="+15"
            )
            
        with col3:
            st.metric(
                label="Avg Quality Score",
                value=f"{self._get_avg_quality_score():.2f}",
                delta="+0.05"
            )
            
        with col4:
            st.metric(
                label="Total Cost",
                value=f"${self._get_total_cost():.2f}",
                delta="-$2.50"
            )
            
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Quality Score Trends")
            quality_data = self._get_quality_trend_data()
            if quality_data:
                fig = px.line(quality_data, x='date', y='quality_score', title='Quality Score Over Time')
                st.plotly_chart(fig, use_container_width=True)
                
        with col2:
            st.subheader("Cost Analysis")
            cost_data = self._get_cost_data()
            if cost_data:
                fig = px.bar(cost_data, x='experiment', y='cost', title='Cost by Experiment')
                st.plotly_chart(fig, use_container_width=True)
                
        # Recent activity
        st.subheader("Recent Activity")
        activity_data = self._get_recent_activity()
        if activity_data:
            st.dataframe(activity_data, use_container_width=True)
            
    def _show_experiments(self):
        """Show experiments management."""
        st.title("🧪 Experiments Management")
        
        # Create new experiment
        with st.expander("Create New Experiment", expanded=False):
            self._show_create_experiment_form()
            
        # List experiments
        st.subheader("Active Experiments")
        experiments = self._get_experiments()
        
        for exp in experiments:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"**{exp['name']}**")
                    st.write(exp['description'])
                    
                with col2:
                    st.write(f"Status: {exp['status']}")
                    
                with col3:
                    st.write(f"Tests: {exp['total_tests']}")
                    
                with col4:
                    if st.button(f"View {exp['id']}", key=exp['id']):
                        self._show_experiment_details(exp['id'])
                        
                st.divider()
                
    def _show_prompt_testing(self):
        """Show prompt testing interface."""
        st.title("🧪 Prompt Testing")
        
        # Test single prompt
        st.subheader("Test Single Prompt")
        
        prompt = st.text_area("Enter your prompt:", height=100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            provider = st.selectbox("Provider", ["OpenAI", "Anthropic", "Google", "HuggingFace"])
            model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet", "gemini-pro"])
            
        with col2:
            temperature = st.slider("Temperature", 0.0, 2.0, 0.7)
            max_tokens = st.number_input("Max Tokens", 1, 4000, 1000)
            
        if st.button("Test Prompt"):
            if prompt:
                with st.spinner("Testing prompt..."):
                    result = self._test_prompt(prompt, provider, model, temperature, max_tokens)
                    self._show_test_results(result)
                    
        # Batch testing
        st.subheader("Batch Testing")
        
        uploaded_file = st.file_uploader("Upload CSV with prompts", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:", df.head())
            
            if st.button("Run Batch Test"):
                with st.spinner("Running batch tests..."):
                    results = self._run_batch_tests(df)
                    self._show_batch_results(results)
                    
    def _show_security_analysis(self):
        """Show security analysis interface."""
        st.title("🔒 Security Analysis")
        
        # Content moderation
        st.subheader("Content Moderation")
        
        text_to_analyze = st.text_area("Enter text to analyze:", height=150)
        
        if st.button("Analyze Security"):
            if text_to_analyze:
                with st.spinner("Analyzing..."):
                    self._show_security_results(text_to_analyze)
                    
        # Security dashboard
        st.subheader("Security Dashboard")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Flagged Content", "12", delta="+3")
            
        with col2:
            st.metric("Injection Attempts", "2", delta="-1")
            
        with col3:
            st.metric("Bias Detected", "8", delta="+2")
            
        # Security trends
        st.subheader("Security Trends")
        security_data = self._get_security_trends()
        if security_data:
            fig = px.line(security_data, x='date', y='flagged_count', title='Security Issues Over Time')
            st.plotly_chart(fig, use_container_width=True)
            
    def _show_optimization(self):
        """Show optimization interface."""
        st.title("⚡ Prompt Optimization")
        
        # Single prompt optimization
        st.subheader("Optimize Single Prompt")
        
        original_prompt = st.text_area("Original Prompt:", height=100)
        
        optimization_goals = st.multiselect(
            "Optimization Goals",
            ["Quality", "Cost", "Latency", "Clarity", "Specificity"]
        )
        
        if st.button("Optimize Prompt"):
            if original_prompt and optimization_goals:
                with st.spinner("Optimizing..."):
                    result = self._optimize_prompt(original_prompt, optimization_goals)
                    self._show_optimization_results(result)
                    
        # A/B testing
        st.subheader("A/B Testing")
        
        variant_a = st.text_area("Variant A:", height=100)
        variant_b = st.text_area("Variant B:", height=100)
        
        traffic_split = st.slider("Traffic Split (A:B)", 0.1, 0.9, 0.5)
        
        if st.button("Start A/B Test"):
            if variant_a and variant_b:
                with st.spinner("Starting A/B test..."):
                    experiment_id = self._start_ab_test(variant_a, variant_b, traffic_split)
                    st.success(f"A/B test started with ID: {experiment_id}")
                    
    def _show_analytics(self):
        """Show analytics interface."""
        st.title("📊 Advanced Analytics")
        
        # Predictive analytics
        st.subheader("Predictive Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Quality Score Prediction**")
            prompt_features = st.text_area("Prompt Features (JSON):", height=100)
            
            if st.button("Predict Quality"):
                if prompt_features:
                    try:
                        features = json.loads(prompt_features)
                        prediction = self._predict_quality(features)
                        self._show_prediction_results(prediction)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format")
                        
        with col2:
            st.write("**Cost Prediction**")
            historical_data = st.text_area("Historical Data (JSON):", height=100)
            
            if st.button("Predict Cost"):
                if historical_data:
                    try:
                        data = json.loads(historical_data)
                        predictions = self._predict_cost_trend(data)
                        self._show_cost_predictions(predictions)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format")
                        
        # Clustering analysis
        st.subheader("Prompt Clustering")
        
        uploaded_file = st.file_uploader("Upload prompts for clustering", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:", df.head())
            
            if st.button("Perform Clustering"):
                with st.spinner("Clustering prompts..."):
                    clusters = self._cluster_prompts(df)
                    self._show_clustering_results(clusters)
                    
    def _show_create_experiment_form(self):
        """Show form to create new experiment."""
        name = st.text_input("Experiment Name")
        description = st.text_area("Description")
        
        col1, col2 = st.columns(2)
        
        with col1:
            provider = st.selectbox("Provider", ["OpenAI", "Anthropic", "Google", "HuggingFace"])
            model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet", "gemini-pro"])
            
        with col2:
            min_sample_size = st.number_input("Min Sample Size", 10, 10000, 100)
            significance_level = st.selectbox("Significance Level", [0.01, 0.05, 0.10])
            
        variants = st.text_area("Prompt Variants (one per line)")
        
        if st.button("Create Experiment"):
            if name and variants:
                variant_strings = [v.strip() for v in variants.split('\n') if v.strip()]
                
                # Convert strings to PromptVariant objects
                variant_list = [
                    PromptVariant(
                        name=f"variant_{i}",
                        template=variant_string
                    )
                    for i, variant_string in enumerate(variant_strings)
                ]
                
                config = ExperimentConfig(
                    name=name,
                    description=description,
                    traffic_split={f"variant_{i}": 1.0/len(variant_list) for i in range(len(variant_list))},
                    min_sample_size=min_sample_size,
                    significance_level=significance_level,
                    provider=ProviderType(provider.lower()),
                    model=model
                )
                
                experiment = self.optimizer.create_experiment(
                    name=name,
                    variants=variant_list,
                    config=config
                )
                
                st.success(f"Experiment created with ID: {experiment.id}")
                
    # Helper methods (placeholders for now)
    def _get_active_experiments(self):
        return []
        
    def _get_total_tests(self):
        return 0
        
    def _get_avg_quality_score(self):
        return 0.75
        
    def _get_total_cost(self):
        return 25.50
        
    def _get_quality_trend_data(self):
        return None
        
    def _get_cost_data(self):
        return None
        
    def _get_recent_activity(self):
        return None
        
    def _get_experiments(self):
        return []
        
    def _test_prompt(self, prompt, provider, model, temperature, max_tokens):
        return {}
        
    def _show_test_results(self, result):
        st.write("Test Results:", result)
        
    def _run_batch_tests(self, df):
        return []
        
    def _show_batch_results(self, results):
        st.write("Batch Results:", results)
        
    def _show_security_results(self, text):
        # Content moderation
        moderation_result = self.security_tools['content_moderator'].moderate_text(text)
        
        # Bias detection
        bias_result = self.security_tools['bias_detector'].detect_bias(text)
        
        # Injection detection
        injection_result = self.security_tools['injection_detector'].detect_injection(text)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Content Moderation**")
            st.write(f"Flagged: {moderation_result.is_flagged}")
            st.write(f"Risk Score: {moderation_result.risk_score:.2f}")
            
        with col2:
            st.write("**Bias Detection**")
            st.write(f"Has Bias: {bias_result.has_bias}")
            st.write(f"Bias Score: {bias_result.bias_score:.2f}")
            
        with col3:
            st.write("**Injection Detection**")
            st.write(f"Is Injection: {injection_result.is_injection}")
            st.write(f"Risk Level: {injection_result.risk_level}")
            
    def _get_security_trends(self):
        return None
        
    def _optimize_prompt(self, prompt, goals):
        return {}
        
    def _show_optimization_results(self, result):
        st.write("Optimization Results:", result)
        
    def _start_ab_test(self, variant_a, variant_b, traffic_split):
        return "exp_123"
        
    def _predict_quality(self, features):
        return {}
        
    def _show_prediction_results(self, prediction):
        st.write("Prediction Results:", prediction)
        
    def _predict_cost_trend(self, data):
        return []
        
    def _show_cost_predictions(self, predictions):
        st.write("Cost Predictions:", predictions)
        
    def _cluster_prompts(self, df):
        return []
        
    def _show_clustering_results(self, clusters):
        st.write("Clustering Results:", clusters)
        
    def _show_experiment_details(self, experiment_id):
        st.write(f"Experiment Details for {experiment_id}")


def main():
    """Main function to run the Streamlit app."""
    app = StreamlitApp()
    app.run()


if __name__ == "__main__":
    main() 