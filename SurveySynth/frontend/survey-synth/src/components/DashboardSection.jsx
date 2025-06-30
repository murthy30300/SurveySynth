// Enhanced DashboardSection.jsx with improved chart visualization
import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  BarChart3,
  TrendingUp,
  Users,
  FileText,
  Clock,
  CheckCircle,
  Eye,
  Download,
  Maximize2,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

const API_BASE = "https://mngp6096cl.execute-api.us-east-1.amazonaws.com/Prod";
const fetchChartUrls = async (userId, uploadId) => {
  try {
    const res = await fetch(
      `${API_BASE}/chart-urls?user_id=${userId}&upload_id=${uploadId}`,
      { method: "OPTIONS" }
    );
    if (!res.ok) return [];
    const data = await res.json();
    return data.chart_urls || [];
  } catch {
    return [];
  }
};

const DashboardSection = ({ userId }) => {
  const [surveyHistory, setSurveyHistory] = useState([]);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [chartUrlsMap, setChartUrlsMap] = useState({});
  const [expandedCharts, setExpandedCharts] = useState(new Set());
  const [selectedChart, setSelectedChart] = useState(null);

  const [stats, setStats] = useState({
    totalSurveys: 0,
    totalResponses: 0,
    completedAnalyses: 0,
    averageSatisfaction: 0,
  });

  useEffect(() => {
    if (userId) fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const fetchData = async () => {
    try {
      setLoading(true);

      // 1️⃣ Survey history
      const surveyRes = await fetch(`${API_BASE}/surveys?user_id=${userId}`);
      if (!surveyRes.ok) throw new Error("Survey fetch failed");
      const surveyJson = await surveyRes.json();
      const surveys = surveyJson.surveys || [];
      setSurveyHistory(surveys);

      // 2️⃣ Insights
      const insightsRes = await fetch(`${API_BASE}/insights?user_id=${userId}`);
      if (!insightsRes.ok) throw new Error("Insights fetch failed");
      const insightsJson = await insightsRes.json();
      const insightsArr = insightsJson.insights || [];
      setInsights(insightsArr);
      const chartUrlsObj = {};
      for (const insight of insightsArr) {
        chartUrlsObj[insight.upload_id] = await fetchChartUrls(
          userId,
          insight.upload_id
        );
      }
      setChartUrlsMap(chartUrlsObj);
      // 3️⃣ Stats
      const totalResponses = insightsArr.reduce(
        (sum, i) => sum + (i.response_count || 0),
        0
      );
      const totalSatisfaction = insightsArr.reduce(
        (sum, i) => sum + (i.avg_satisfaction || 0),
        0
      );
      const avgSatisfaction =
        insightsArr.length > 0
          ? Number((totalSatisfaction / insightsArr.length).toFixed(1))
          : 0;
      const completedAnalyses = insightsArr.filter(
        (i) => i.avg_satisfaction > 0
      ).length;

      setStats({
        totalSurveys: surveys.length,
        totalResponses,
        completedAnalyses,
        averageSatisfaction: avgSatisfaction,
      });
    } catch (err) {
      /* eslint-disable no-console */
      console.error("Error fetching dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  // ---------- helpers ----------
  const getStatusColor = (status) => {
    switch (status) {
      case "completed":
      case "analyzed":
        return "bg-green-100 text-green-800";
      case "processing":
        return "bg-blue-100 text-blue-800";
      case "raw":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getSentimentColor = (sentiment) => {
    switch ((sentiment || "").toLowerCase()) {
      case "positive":
        return "text-green-600";
      case "mixed":
      case "neutral":
        return "text-yellow-600";
      case "negative":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  const getTrendIcon = (sentiment) => {
    switch ((sentiment || "").toLowerCase()) {
      case "positive":
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case "negative":
        return <TrendingUp className="h-4 w-4 text-red-500 rotate-180" />;
      default:
        return <div className="h-4 w-4 bg-gray-300 rounded-full" />;
    }
  };

  const toggleChartExpansion = (uploadId) => {
    const newExpanded = new Set(expandedCharts);
    if (newExpanded.has(uploadId)) {
      newExpanded.delete(uploadId);
    } else {
      newExpanded.add(uploadId);
    }
    setExpandedCharts(newExpanded);
  };

  const openChartModal = (url, title) => {
    setSelectedChart({ url, title });
  };

  const closeChartModal = () => {
    setSelectedChart(null);
  };

  // ---------- render ----------
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="py-8 text-center">
          <Clock className="mx-auto h-8 w-8 animate-spin text-blue-500" />
          <p className="mt-2 text-gray-600">Loading dashboard data&hellip;</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* 🔑 Metrics */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        {/* Total Surveys */}
        <Card className="hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Total Surveys
                </p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats.totalSurveys}
                </p>
              </div>
              <div className="rounded-full bg-blue-100 p-3">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Total Responses */}
        <Card className="hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Total Responses
                </p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats.totalResponses.toLocaleString()}
                </p>
              </div>
              <div className="rounded-full bg-green-100 p-3">
                <Users className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
       
        {/* Completed Analyses */}
        <Card className="hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Completed Analyses
                </p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats.completedAnalyses}
                </p>
              </div>
              <div className="rounded-full bg-purple-100 p-3">
                <BarChart3 className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Average Satisfaction */}
        <Card className="hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Avg. Satisfaction
                </p>
                <p className="text-3xl font-bold text-gray-900">
                  {stats.averageSatisfaction}
                </p>
                <p className="text-sm text-gray-500">out of 5.0</p>
              </div>
              <div className="rounded-full bg-yellow-100 p-3">
                <TrendingUp className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* 📜 Recent Activity */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest survey processing updates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {surveyHistory.length === 0 ? (
                <p className="py-4 text-center text-gray-500">
                  No surveys uploaded yet
                </p>
              ) : (
                surveyHistory.slice(0, 4).map((survey) => (
                  <div
                    key={survey.upload_id}
                    className="flex items-center justify-between rounded-lg border p-3 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      {survey.status === "analyzed" ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : survey.status === "processing" ? (
                        <Clock className="h-5 w-5 text-blue-500" />
                      ) : (
                        <FileText className="h-5 w-5 text-gray-500" />
                      )}
                      <div>
                        <p className="font-medium text-gray-900">
                          Survey {survey.upload_id}
                        </p>
                        <p className="text-sm text-gray-500">
                          Uploaded {survey.timestamp}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge
                        variant="secondary"
                        className={getStatusColor(survey.status)}
                      >
                        {survey.status}
                      </Badge>
                      <p className="mt-1 text-xs text-gray-500">
                        {survey.analyzed_at
                          ? `Analyzed ${survey.analyzed_at}`
                          : "Processing..."}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* 🔍 Survey Insights */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Survey Performance</CardTitle>
            <CardDescription>
              Satisfaction scores and sentiment analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {insights.length === 0 ? (
                <p className="py-4 text-center text-gray-500">
                  No insights available yet
                </p>
              ) : (
                insights.slice(0, 4).map((insight) => (
                  <div key={insight.upload_id} className="space-y-2 p-4 rounded-lg border hover:shadow-md transition-shadow">
                    {/* row 1 */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900">
                          Survey {insight.upload_id}
                        </span>
                        {getTrendIcon(insight.overall_sentiment)}
                      </div>
                      <div className="text-right">
                        <span className="font-bold text-gray-900">
                          {insight.avg_satisfaction?.toFixed(1) ?? "N/A"}
                        </span>
                        <span className="text-sm text-gray-500">/5.0</span>
                      </div>
                    </div>
                    {/* row 2 */}
                    <div className="flex items-center justify-between text-sm">
                      <span
                        className={`capitalize ${getSentimentColor(
                          insight.overall_sentiment
                        )}`}
                      >
                        {insight.overall_sentiment || "Unknown"} sentiment
                      </span>
                      <span className="text-gray-500">
                        {insight.response_count || 0} responses
                      </span>
                    </div>
                    {/* bar */}
                    <Progress
                      value={(insight.avg_satisfaction / 5) * 100}
                      className="h-2"
                    />
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 📊 Enhanced Charts Dashboard */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Survey Analytics Dashboard</h2>
            <p className="text-gray-600">Interactive visual insights from your survey data</p>
          </div>
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-500" />
            <span className="text-sm text-gray-500">
              {Object.values(chartUrlsMap).flat().length} charts available
            </span>
          </div>
        </div>

        {insights.length === 0 ? (
          <Card className="border-2 border-dashed border-gray-200">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <BarChart3 className="h-16 w-16 text-gray-300 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Survey Data Available</h3>
              <p className="text-gray-500 text-center max-w-md">
                Upload and analyze your first survey to see beautiful data visualizations here.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-8">
            {insights.map((insight) => {
              const charts = chartUrlsMap[insight.upload_id] || [];
              const isExpanded = expandedCharts.has(insight.upload_id);
              const visibleCharts = isExpanded ? charts : charts.slice(0, 2);

              return (
                <div
                  key={insight.upload_id}
                  className="bg-gradient-to-br from-white to-gray-50 rounded-xl border border-gray-200 shadow-sm hover:shadow-lg transition-all duration-300"
                >
                  {/* Survey Header */}
                  <div className="p-6 border-b border-gray-100">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                          <BarChart3 className="h-6 w-6 text-white" />
                        </div>
                        <div>
                          <h3 className="text-xl font-bold text-gray-900">
                            Survey {insight.upload_id}
                          </h3>
                          <div className="flex items-center gap-4 mt-1">
                            <div className="flex items-center gap-1">
                              <Users className="h-4 w-4 text-gray-500" />
                              <span className="text-sm text-gray-600">
                                {insight.response_count || 0} responses
                              </span>
                            </div>
                            <div className="flex items-center gap-1">
                              {getTrendIcon(insight.overall_sentiment)}
                              <span className={`text-sm capitalize ${getSentimentColor(insight.overall_sentiment)}`}>
                                {insight.overall_sentiment || "Unknown"} sentiment
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-bold text-gray-900">
                          {insight.avg_satisfaction?.toFixed(1) ?? "N/A"}
                        </div>
                        <div className="text-sm text-gray-500">Satisfaction Score</div>
                        <Progress
                          value={(insight.avg_satisfaction / 5) * 100}
                          className="h-2 w-24 mt-2"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Charts Grid */}
                  {charts.length > 0 ? (
                    <div className="p-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                        {visibleCharts.map((url, idx) => (
                          <div
                            key={idx}
                            className="group relative bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-all duration-300"
                          >
                            <div className="aspect-square relative">
                              <img
                                src={url}
                                alt={`Chart ${idx + 1} for Survey ${insight.upload_id}`}
                                className="w-full h-full object-contain p-4"
                              />
                              
                              {/* Overlay Actions */}
                              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300 flex items-center justify-center opacity-0 group-hover:opacity-100">
                                <div className="flex gap-2">
                                  <button
                                    onClick={() => openChartModal(url, `Survey ${insight.upload_id} - Chart ${idx + 1}`)}
                                    className="p-2 bg-white rounded-full shadow-lg hover:bg-gray-50 transition-colors"
                                    title="View full size"
                                  >
                                    <Maximize2 className="h-4 w-4 text-gray-700" />
                                  </button>
                                  <button
                                    onClick={() => window.open(url, '_blank')}
                                    className="p-2 bg-white rounded-full shadow-lg hover:bg-gray-50 transition-colors"
                                    title="Open in new tab"
                                  >
                                    <Eye className="h-4 w-4 text-gray-700" />
                                  </button>
                                </div>
                              </div>
                            </div>
                            
                            {/* Chart Info */}
                            <div className="p-3 border-t border-gray-100 bg-gray-50">
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium text-gray-700">
                                  Chart {idx + 1}
                                </span>
                                <span className="text-xs text-gray-500">
                                  Click to expand
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Show More/Less Button */}
                      {charts.length > 2 && (
                        <div className="mt-6 text-center">
                          <button
                            onClick={() => toggleChartExpansion(insight.upload_id)}
                            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                          >
                            {isExpanded ? (
                              <>
                                <ChevronUp className="h-4 w-4" />
                                Show Less Charts
                              </>
                            ) : (
                              <>
                                <ChevronDown className="h-4 w-4" />
                                Show {charts.length - 2} More Charts
                              </>
                            )}
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="p-12 text-center">
                      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <BarChart3 className="h-8 w-8 text-gray-400" />
                      </div>
                      <h4 className="text-lg font-medium text-gray-900 mb-2">No Charts Available</h4>
                      <p className="text-gray-500">Charts are being generated for this survey.</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Chart Modal */}
      {selectedChart && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] w-full flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold text-gray-900">
                {selectedChart.title}
              </h3>
              <button
                onClick={closeChartModal}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <span className="sr-only">Close</span>
                <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
            <div className="flex-1 p-4 overflow-auto">
              <img
                src={selectedChart.url}
                alt={selectedChart.title}
                className="w-full h-auto max-h-full object-contain"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

DashboardSection.propTypes = {
  userId: PropTypes.string,
};

export default DashboardSection;