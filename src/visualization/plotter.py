from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class MemeVisualizer:
    def __init__(self):
        # Common color schemes
        self.colors = {
            'primary': '#FF6B6B',
            'secondary': '#4ECDC4',
            'accent': '#45B7D1',
            'background': '#1A1A1A',
            'text': '#FFFFFF'
        }
        
        # Default layout settings
        self.layout_defaults = {
            'template': 'plotly_dark',
            'paper_bgcolor': self.colors['background'],
            'plot_bgcolor': self.colors['background'],
            'font': {'color': self.colors['text']}
        }

    async def create_sentiment_timeline(self, 
                                     analyses: List[Dict[str, Any]], 
                                     timeframe_hours: int = 24) -> go.Figure:
        """Create sentiment analysis timeline plot"""
        df = pd.DataFrame(analyses)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Calculate rolling averages
        df['positive_ma'] = df['sentiment'].apply(lambda x: x['positive']).rolling(5).mean()
        df['negative_ma'] = df['sentiment'].apply(lambda x: x['negative']).rolling(5).mean()
        df['neutral_ma'] = df['sentiment'].apply(lambda x: x['neutral']).rolling(5).mean()
        
        fig = go.Figure()
        
        # Add sentiment lines
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['positive_ma'],
            name='Positive',
            line={'color': self.colors['primary']},
            fill='tonexty'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['negative_ma'],
            name='Negative',
            line={'color': self.colors['secondary']},
            fill='tonexty'
        ))
        
        fig.update_layout(
            title='Meme Sentiment Timeline',
            xaxis_title='Time',
            yaxis_title='Sentiment Score',
            **self.layout_defaults
        )
        
        return fig

    async def create_virality_heatmap(self,
                                    analyses: List[Dict[str, Any]],
                                    platform_filter: Optional[str] = None) -> go.Figure:
        """Create virality score heatmap by hour and platform"""
        df = pd.DataFrame(analyses)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        
        if platform_filter:
            df = df[df['source'] == platform_filter]
        
        # Pivot data for heatmap
        pivot = df.pivot_table(
            values='virality_score',
            index='hour',
            columns='source',
            aggfunc='mean'
        ).fillna(0)
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale='Viridis',
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Virality Score Heatmap by Platform and Hour',
            xaxis_title='Platform',
            yaxis_title='Hour of Day',
            **self.layout_defaults
        )
        
        return fig

    async def create_memecoin_impact(self,
                                   coin_analyses: List[Dict[str, Any]]) -> go.Figure:
        """Create memecoin impact visualization"""
        df = pd.DataFrame(coin_analyses)
        
        # Create subplot with shared x-axis
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Price Impact', 'Volume Prediction')
        )
        
        # Add price impact trace
        fig.add_trace(
            go.Bar(
                x=df['symbol'],
                y=df['price_impact'],
                name='Price Impact %',
                marker_color=self.colors['primary']
            ),
            row=1, col=1
        )
        
        # Add volume prediction trace
        fig.add_trace(
            go.Bar(
                x=df['symbol'],
                y=df['volume_prediction'],
                name='Volume Change %',
                marker_color=self.colors['secondary']
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title='Memecoin Market Impact Analysis',
            showlegend=True,
            height=800,
            **self.layout_defaults
        )
        
        return fig

    async def create_trend_network(self,
                                 analyses: List[Dict[str, Any]]) -> go.Figure:
        """Create network graph of trending topics and their relationships"""
        # Extract trending topics and their connections
        topics = {}
        connections = []
        
        for analysis in analyses:
            trends = analysis.get('trend_indicators', {}).get('trending_topics', [])
            for i, topic in enumerate(trends):
                if topic not in topics:
                    topics[topic] = len(topics)
                for other_topic in trends[i+1:]:
                    if other_topic not in topics:
                        topics[other_topic] = len(topics)
                    connections.append((topics[topic], topics[other_topic]))
        
        # Create network layout using Fruchterman-Reingold algorithm
        pos = self._network_layout(len(topics), connections)
        
        # Create scatter plot for nodes
        node_trace = go.Scatter(
            x=pos[:, 0],
            y=pos[:, 1],
            mode='markers+text',
            marker=dict(
                size=20,
                color=self.colors['accent']
            ),
            text=list(topics.keys()),
            textposition='top center'
        )
        
        # Create lines for connections
        edge_traces = []
        for start, end in connections:
            edge_traces.append(go.Scatter(
                x=[pos[start, 0], pos[end, 0]],
                y=[pos[start, 1], pos[end, 1]],
                mode='lines',
                line=dict(color=self.colors['text'], width=1),
                hoverinfo='none'
            ))
        
        # Combine all traces
        fig = go.Figure(data=[*edge_traces, node_trace])
        
        fig.update_layout(
            title='Trend Topic Network',
            showlegend=False,
            **self.layout_defaults
        )
        
        return fig

    def _network_layout(self, n_nodes: int, edges: List[tuple]) -> np.ndarray:
        """Simple force-directed layout algorithm"""
        pos = np.random.rand(n_nodes, 2)
        k = np.sqrt(1.0 / n_nodes)
        
        # Simple implementation of Fruchterman-Reingold
        for _ in range(50):
            disp = np.zeros((n_nodes, 2))
            
            # Calculate repulsive forces
            for i in range(n_nodes):
                for j in range(n_nodes):
                    if i != j:
                        delta = pos[i] - pos[j]
                        dist = max(0.01, np.linalg.norm(delta))
                        disp[i] += delta * k * k / dist
            
            # Calculate attractive forces
            for i, j in edges:
                delta = pos[i] - pos[j]
                dist = max(0.01, np.linalg.norm(delta))
                disp[i] -= delta * dist / k
                disp[j] += delta * dist / k
            
            # Update positions
            length = np.linalg.norm(disp, axis=1)
            length = np.where(length < 0.01, 0.1, length)
            pos += disp * k / length[:, np.newaxis]
            
            # Keep within bounds
            pos = np.clip(pos, -1, 1)
        
        return pos

    async def save_plot(self, fig: go.Figure, path: str) -> None:
        """Save plot as static image"""
        fig.write_image(path) 