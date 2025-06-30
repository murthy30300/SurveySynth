// Index.jsx
import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { toast } from "sonner";
import {
  BookOpen,
  BarChart3,
  Upload,
  Users,
  TrendingUp,
  FileText,
} from "lucide-react";

import UploadSection from "@/components/UploadSection";
import DashboardSection from "@/components/DashboardSection";
import InsightsSection from "@/components/InsightsSection";

const API_BASE =
  "https://mngp6096cl.execute-api.us-east-1.amazonaws.com/Prod";

const Index = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authMode, setAuthMode] = useState("login"); // "login" | "register"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [userId, setUserId] = useState(null);
  const [activeTab, setActiveTab] = useState("upload");
  const [userCount, setUserCount] = useState(null);
  const [userInfo, setUserInfo] = useState(null);

  /* -------- fetch public user‑count -------- */
  useEffect(() => {
    if (!isAuthenticated) {
      fetch(`${API_BASE}/users`)
        .then(async (res) => {
          if (!res.ok) {
            const text = await res.text();
            throw new Error(`User count fetch failed: ${res.status} ${text}`);
          }
          return res.json();
        })
        .then((data) => setUserCount(data.user_count))
        .catch((e) => {
          console.error("User count error:", e);
          setUserCount(0);
        });
    }
  }, [isAuthenticated]);

  /* -------- restore session -------- */
  useEffect(() => {
    const storedUserId = localStorage.getItem("user_id");
    const storedEmail = localStorage.getItem("email");
    if (storedUserId && storedEmail) {
      setUserId(storedUserId);
      setEmail(storedEmail);
      setIsAuthenticated(true);
    }
  }, []);

  /* -------- fetch user info when logged in -------- */
  useEffect(() => {
    if (isAuthenticated && email) {
      fetch(`${API_BASE}/users?email=${email}`)
        .then(async (res) => {
          if (!res.ok) {
            const text = await res.text();
            throw new Error(`User info fetch failed: ${res.status} ${text}`);
          }
          return res.json();
        })
        .then(setUserInfo)
        .catch((e) => console.error("User info error:", e));
    }
  }, [isAuthenticated, email]);

  /* -------- handle login / register -------- */
  const handleAuth = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error("Please fill in all fields");
      return;
    }

    try {
      const endpoint =
        authMode === "login" ? `${API_BASE}/login` : `${API_BASE}/register`;

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (authMode === "login" && data.message === "Login successful") {
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("email", email);
        setUserId(data.user_id);
        setIsAuthenticated(true);
        toast.success("Welcome back!");
      } else if (authMode === "register" && response.ok) {
        toast.success("Account created successfully! Please login.");
        setAuthMode("login");
      } else {
        toast.error(data.message || "Authentication failed");
      }
    } catch (err) {
      console.error("Auth error:", err);
      toast.error("Authentication failed. Please try again.");
    }
  };

  /* -------- logout -------- */
  const handleLogout = () => {
    localStorage.removeItem("user_id");
    localStorage.removeItem("email");
    setUserId(null);
    setIsAuthenticated(false);
    setEmail("");
    setPassword("");
    setUserInfo(null);
    toast.success("Logged out successfully");
  };

  /* ========== UNAUTHENTICATED VIEW ========== */
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
        <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-8 items-center">
          {/* ----- Hero ----- */}
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-600 rounded-xl">
                <BookOpen className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">SurveySynth</h1>
                <p className="font-medium text-blue-600">
                  Intelligent Feedback Analyzer
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <h2 className="text-4xl font-bold leading-tight text-gray-900">
                Transform Student Feedback into
                <span className="text-blue-600"> Actionable Insights</span>
              </h2>
              <p className="text-xl leading-relaxed text-gray-600">
                Designed for course coordinators managing large student
                populations. Upload survey data and receive AI‑powered
                summaries, sentiment analysis, and recommendations.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-3 p-4 bg-white rounded-lg shadow-sm">
                <BarChart3 className="h-6 w-6 text-green-600" />
                <div>
                  <p className="font-semibold text-gray-900">Smart Analysis</p>
                  <p className="text-sm text-gray-600">AI‑powered insights</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-4 bg-white rounded-lg shadow-sm">
                <Users className="h-6 w-6 text-purple-600" />
                <div>
                  <p className="font-semibold text-gray-900">Batch Processing</p>
                  <p className="text-sm text-gray-600">Handle 3400+ responses</p>
                </div>
              </div>
            </div>

            {userCount !== null && (
              <div className="p-4 bg-white rounded-lg shadow-sm">
                <p className="text-sm text-gray-600">Platform Users</p>
                <p className="text-2xl font-bold text-blue-600">{userCount}</p>
              </div>
            )}
          </div>

          {/* ----- Auth Card ----- */}
          <Card className="w-full max-w-md mx-auto shadow-xl border-0">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl">
                {authMode === "login" ? "Welcome Back" : "Get Started"}
              </CardTitle>
              <CardDescription>
                {authMode === "login"
                  ? "Sign in to your SurveySynth account"
                  : "Create your SurveySynth account"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAuth} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="coordinator@university.edu"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  {authMode === "login" ? "Sign In" : "Create Account"}
                </Button>
              </form>

              <div className="mt-6 text-center">
                <button
                  onClick={() =>
                    setAuthMode(authMode === "login" ? "register" : "login")
                  }
                  className="text-sm font-medium text-blue-600 hover:text-blue-700"
                >
                  {authMode === "login"
                    ? "Don't have an account? Sign up"
                    : "Already have an account? Sign in"}
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  /* ========== AUTHENTICATED VIEW ========== */
  return (
    <div className="min-h-screen bg-gray-50">
      {/* ----- Header ----- */}
      <header className="border-b bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-blue-600 p-2">
                <BookOpen className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">SurveySynth</h1>
                <p className="text-xs text-gray-500">Course Feedback Analyzer</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{email}</p>
                <p className="text-xs text-gray-500">Course Coordinator</p>
                {userInfo && (
                  <p className="text-xs text-gray-400">ID: {userId}</p>
                )}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-900"
              >
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* ----- Main ----- */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="space-y-6"
        >
          <TabsList className="grid w-full grid-cols-3 lg:w-96">
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <Upload className="h-4 w-4" />
              Upload
            </TabsTrigger>
            <TabsTrigger value="dashboard" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="insights" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Insights
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload">
            <UploadSection userId={userId} email={email} />
          </TabsContent>

          <TabsContent value="dashboard">
            <DashboardSection userId={userId} />
          </TabsContent>

          <TabsContent value="insights">
            <InsightsSection userId={userId} />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Index;
