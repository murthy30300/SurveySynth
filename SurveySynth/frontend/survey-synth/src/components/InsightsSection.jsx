// InsightsSection.jsx
import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  FileText,
  Download,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Lightbulb,
  ThumbsUp,
  MessageSquare,
  BarChart3,
  Clock,
} from "lucide-react";

const API_BASE = "https://mngp6096cl.execute-api.us-east-1.amazonaws.com/Prod";

const InsightsSection = ({ userId }) => {
  const [surveyHistory, setSurveyHistory] = useState([]);
  const [insights, setInsights] = useState([]);
  const [selectedSurvey, setSelectedSurvey] = useState(null);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(false);

  /* ------------------- data fetch ------------------- */
  useEffect(() => {
    if (userId) fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  /* poll status until survey analyzed */
  useEffect(() => {
    if (polling && selectedSurvey && userId) {
      const id = setInterval(() => {
        fetchData();
        const survey = surveyHistory.find((s) => s.upload_id === selectedSurvey);
        if (survey?.status === "analyzed") setPolling(false);
      }, 5000);
      return () => clearInterval(id);
    }
  }, [polling, selectedSurvey, userId, surveyHistory]);

  const fetchData = async () => {
    try {
      setLoading(true);

      /* survey list */
      const surveyRes = await fetch(`${API_BASE}/surveys?user_id=${userId}`);
      if (surveyRes.ok) {
        const json = await surveyRes.json();
        setSurveyHistory(json.surveys || []);
      }

      /* insight list */
      const insightRes = await fetch(`${API_BASE}/insights?user_id=${userId}`);
      if (insightRes.ok) {
        const json = await insightRes.json();
        setInsights(json.insights || []);
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("Error fetching insights data:", err);
    } finally {
      setLoading(false);
    }
  };

  /* ------------------- helpers ------------------- */
  const handleSurveySelect = (uploadId) => {
    setSelectedSurvey(uploadId);
    const survey = surveyHistory.find((s) => s.upload_id === uploadId);
    if (survey && survey.status !== "analyzed") setPolling(true);
  };

  const getCurrentInsight = () =>
    selectedSurvey
      ? insights.find((i) => i.upload_id === selectedSurvey) || null
      : null;

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

  /* ------------------- render ------------------- */
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="py-8 text-center">
          <Clock className="mx-auto h-8 w-8 animate-spin text-blue-500" />
          <p className="mt-2 text-gray-600">Loading insights…</p>
        </div>
      </div>
    );
  }

  const currentInsight = getCurrentInsight();
  const currentSurvey = surveyHistory.find((s) => s.upload_id === selectedSurvey);

  return (
    <div className="space-y-6">
      {/* ---------- survey selector ---------- */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Survey Analysis Results
          </CardTitle>
          <CardDescription>
            Select a survey to view detailed insights and recommendations
          </CardDescription>
        </CardHeader>
        <CardContent>
          {surveyHistory.length === 0 ? (
            <p className="py-4 text-center text-gray-500">
              No surveys uploaded yet
            </p>
          ) : (
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
              {surveyHistory.map((survey) => (
                <button
                  key={survey.upload_id}
                  onClick={() => handleSurveySelect(survey.upload_id)}
                  className={`transition-colors rounded-lg border p-4 text-left ${
                    selectedSurvey === survey.upload_id
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium text-gray-900">
                        Survey {survey.upload_id}
                      </h3>
                      <Badge
                        variant="secondary"
                        className={
                          survey.status === "analyzed"
                            ? "bg-green-100 text-green-800"
                            : "bg-blue-100 text-blue-800"
                        }
                      >
                        {survey.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-500">{survey.timestamp}</p>
                    {polling && selectedSurvey === survey.upload_id && (
                      <p className="text-xs text-blue-600">Checking status…</p>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* ---------- details ---------- */}
      {selectedSurvey && currentSurvey && (
        <div className="space-y-6">
          {/* overview */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Survey {selectedSurvey} Analysis</CardTitle>
                  <CardDescription>
                    {currentSurvey.status === "analyzed"
                      ? "Analysis completed"
                      : "Processing in progress"}{" "}
                    • Uploaded on {currentSurvey.timestamp}
                  </CardDescription>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={!currentInsight}
                  title="Export coming soon"
                >
                  <Download className="mr-2 h-4 w-4" />
                  Export Report
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {currentInsight ? (
                <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                  {/* satisfaction */}
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">
                      {currentInsight.avg_satisfaction?.toFixed(1) ?? "N/A"}
                    </div>
                    <div className="text-sm text-gray-600">
                      Overall Satisfaction
                    </div>
                    <div className="text-xs text-gray-500">out of 5.0</div>
                  </div>
                  {/* responses */}
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">
                      {currentInsight.response_count}
                    </div>
                    <div className="text-sm text-gray-600">Total Responses</div>
                  </div>
                  {/* sentiment */}
                  <div className="text-center">
                    <div
                      className={`text-3xl font-bold capitalize ${getSentimentColor(
                        currentInsight.overall_sentiment
                      )}`}
                    >
                      {currentInsight.overall_sentiment || "Unknown"}
                    </div>
                    <div className="text-sm text-gray-600">
                      Overall Sentiment
                    </div>
                    <div className="text-xs text-gray-500">
                      AI‑powered analysis
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-8 text-center">
                  <Clock className="mx-auto h-8 w-8 animate-spin text-blue-500" />
                  <p className="mt-2 text-gray-600">
                    {currentSurvey.status === "analyzed"
                      ? "Loading insights…"
                      : "Analysis in progress…"}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* tabs only when we have insight */}
          {currentInsight && (
            <Tabs defaultValue="summary" className="space-y-4">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="summary">Summary</TabsTrigger>
                <TabsTrigger value="pain-points">Pain Points</TabsTrigger>
                <TabsTrigger value="positive">Positive Aspects</TabsTrigger>
                <TabsTrigger value="actions">Action Items</TabsTrigger>
              </TabsList>

              {/* ---- summary ---- */}
              <TabsContent value="summary" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MessageSquare className="h-5 w-5" />
                      Analysis Overview
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <h4 className="mb-2 font-semibold">Key Metrics</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          Average Satisfaction:{" "}
                          {currentInsight.avg_satisfaction?.toFixed(1)}/5.0
                        </div>
                        <div>Response Count: {currentInsight.response_count}</div>
                        <div>
                          Overall Sentiment: {currentInsight.overall_sentiment}
                        </div>
                        <div>
                          Completed Analyses:{" "}
                          {currentInsight.completed_analyses}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* topic performance */}
                {currentInsight.topic_sentiment_map && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Topic Performance</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {Object.entries(
                          currentInsight.topic_sentiment_map
                        ).map(([topic, perf]) => (
                          <div
                            key={topic}
                            className="flex items-center justify-between rounded-lg border p-3"
                          >
                            <div>
                              <p className="font-medium text-gray-900">
                                {topic}
                              </p>
                              <p className="text-sm text-gray-500">
                                +{perf.positive_count} positive,&nbsp;-
                                {perf.negative_count} negative
                              </p>
                            </div>
                            <div className="text-right">
                              <p
                                className={`text-lg font-bold ${getSentimentColor(
                                  perf.avg_rating >= 3.5
                                    ? "positive"
                                    : perf.avg_rating >= 2.5
                                    ? "mixed"
                                    : "negative"
                                )}`}
                              >
                                {perf.avg_rating?.toFixed(1)}
                              </p>
                              <p className="text-sm text-gray-500">
                                avg rating
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {/* ---- pain points ---- */}
              <TabsContent value="pain-points">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="h-5 w-5 text-red-500" />
                      Areas for Improvement
                    </CardTitle>
                    <CardDescription>
                      Key challenges identified from student feedback
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-96">
                      <div className="space-y-3">
                        {currentInsight.pain_points?.length ? (
                          currentInsight.pain_points.map((point, idx) => (
                            <div
                              key={idx}
                              className="flex items-start gap-3 rounded-r-lg border-l-4 border-red-200 bg-red-50 p-4"
                            >
                              <AlertTriangle className="h-5 w-5 flex-shrink-0 text-red-500" />
                              <p className="text-gray-700">{point}</p>
                            </div>
                          ))
                        ) : (
                          <p className="py-4 text-center text-gray-500">
                            No specific pain points identified
                          </p>
                        )}
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* ---- positive ---- */}
              <TabsContent value="positive">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <ThumbsUp className="h-5 w-5 text-green-500" />
                      What's Working Well
                    </CardTitle>
                    <CardDescription>
                      Strengths highlighted by students
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-96">
                      <div className="space-y-3">
                        {currentInsight.positive_aspects?.length ? (
                          currentInsight.positive_aspects.map((a, idx) => (
                            <div
                              key={idx}
                              className="flex items-start gap-3 rounded-r-lg border-l-4 border-green-200 bg-green-50 p-4"
                            >
                              <CheckCircle className="h-5 w-5 flex-shrink-0 text-green-500" />
                              <p className="text-gray-700">{a}</p>
                            </div>
                          ))
                        ) : (
                          <p className="py-4 text-center text-gray-500">
                            No specific positive aspects identified
                          </p>
                        )}
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* ---- actions ---- */}
              <TabsContent value="actions">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Lightbulb className="h-5 w-5 text-blue-500" />
                      Recommended Actions
                    </CardTitle>
                    <CardDescription>
                      AI‑generated recommendations based on feedback analysis
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-96">
                      <div className="space-y-3">
                        {currentInsight.top_insights?.length ? (
                          currentInsight.top_insights.map((ins, idx) => (
                            <div
                              key={idx}
                              className="flex items-start gap-3 rounded-r-lg border-l-4 border-blue-200 bg-blue-50 p-4"
                            >
                              <Lightbulb className="h-5 w-5 flex-shrink-0 text-blue-500" />
                              <div className="flex-1">
                                <p className="text-gray-700">{ins}</p>
                                <div className="mt-2 flex gap-2">
                                  <Badge
                                    variant="outline"
                                    className="text-xs"
                                  >
                                    AI Insight
                                  </Badge>
                                </div>
                              </div>
                            </div>
                          ))
                        ) : (
                          <p className="py-4 text-center text-gray-500">
                            No specific insights available
                          </p>
                        )}
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          )}
        </div>
      )}
    </div>
  );
};

InsightsSection.propTypes = {
  userId: PropTypes.string,
};

export default InsightsSection;
