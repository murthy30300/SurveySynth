// ChartViewer.jsx
import React, { useState, useEffect } from 'react';

const ChartViewer = ({ userId, uploadId }) => {
  const [charts, setCharts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCharts();
  }, [userId, uploadId]);

  const fetchCharts = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/charts/${userId}?upload_id=${uploadId}`);
      const data = await response.json();
      setCharts(data.charts || []);
    } catch (error) {
      console.error('Error fetching charts:', error);
    } finally {
      setLoading(false);
    }
  };

  const refreshCharts = () => {
    fetchCharts();
  };

  if (loading) {
    return (
      <div className="chart-loader">
        <div className="spinner"></div>
        <p>Generating visualizations...</p>
      </div>
    );
  }

  return (
    <div className="chart-viewer">
      <div className="chart-header">
        <h2>Survey Analytics</h2>
        <button onClick={refreshCharts} className="refresh-btn">
          🔄 Refresh Charts
        </button>
      </div>
      
      <div className="chart-grid">
        {charts.map((chart, index) => (
          <div key={index} className="chart-card">
            <h3>{formatChartTitle(chart.type)}</h3>
            <div className="chart-container">
              <img 
                src={chart.url} 
                alt={chart.type}
                onLoad={() => console.log('Chart loaded')}
                onError={(e) => {
                  console.error('Chart failed to load');
                  e.target.src = '/placeholder-chart.png';
                }}
                style={{ width: '100%', height: 'auto' }}
              />
            </div>
            <p className="chart-date">
              Generated: {new Date(chart.created_at).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>
      
      {charts.length === 0 && (
        <div className="no-charts">
          <p>No visualizations available yet.</p>
          <p>Charts will appear here once your survey is analyzed.</p>
        </div>
      )}
    </div>
  );
};

const formatChartTitle = (type) => {
  const titles = {
    'sentiment_pie': 'Sentiment Distribution',
    'pain_points': 'Top Pain Points',
    'insights': 'Actionable Insights',
    'response_analytics': 'Response Analytics',
    'sentiment_trend': 'Sentiment Trends',
    'feedback_quality': 'Feedback Quality'
  };
  return titles[type] || type;
};

export default ChartViewer;