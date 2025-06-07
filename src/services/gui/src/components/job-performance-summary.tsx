import { useTreeData } from "@/hooks/use-tree-data";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PHASE_COLORS } from "@/lib/utils";
import {
  Download,
  Activity,
  Layers,
  Target,
  Brain,
  PieChart as PieChartIcon,
  BarChart3,
  ListOrdered,
} from "lucide-react";
import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"];

interface JobPerformanceSummaryProps {
  sessionId: string;
}

export function JobPerformanceSummary({
  sessionId,
}: JobPerformanceSummaryProps) {
  const { data, stats, loading, error } = useTreeData(sessionId, {
    enablePolling: false,
  });

  // Prepare data for charts
  const phaseData = stats
    ? Object.entries(stats.phaseDistribution).map(([phase, count]) => ({
        phase: `Phase ${phase}`,
        count,
        color:
          PHASE_COLORS[parseInt(phase) as keyof typeof PHASE_COLORS] ||
          "#8884d8",
      }))
    : [];
  const conceptData = stats
    ? Object.entries(stats.conceptDistribution)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([concept, count]) => ({
          concept:
            concept.length > 15 ? concept.substring(0, 15) + "..." : concept,
          count,
        }))
    : [];
  const difficultyData = stats
    ? Object.entries(stats.difficultyDistribution).map(
        ([difficulty, count]) => ({
          difficulty,
          count,
        })
      )
    : [];

  const exportData = (format: "json" | "csv") => {
    if (!data) return;
    if (format === "json") {
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `tree-data-${sessionId}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } else if (format === "csv") {
      const csvHeaders = [
        "Node ID",
        "Phase",
        "Depth",
        "Concepts",
        "Difficulty",
        "Value",
        "Visits",
        "Successes",
        "Failures",
        "Challenge Description",
      ];
      const csvRows = data.nodes.map((node) => [
        node.id,
        node.phase,
        node.depth,
        node.concepts.join("; "),
        node.difficulty,
        node.value,
        node.visits,
        node.successes,
        node.failures,
        node.challenge_description.replace(/"/g, '""').replace(/\n/g, " "),
      ]);
      const csvContent = [
        csvHeaders.join(","),
        ...csvRows.map((row) => row.map((cell) => `"${cell}"`).join(",")),
      ].join("\n");
      const blob = new Blob([csvContent], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `tree-data-${sessionId}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2"></div>
            </CardHeader>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return <div className="text-destructive">{error}</div>;
  }

  if (!stats) {
    return <div className="text-muted-foreground">No data available</div>;
  }

  return (
    <div className="space-y-6">
      {/* Export Buttons */}
      <div className="flex gap-2 mb-2">
        <Button
          variant="outline"
          onClick={() => exportData("json")}
          disabled={!data}
        >
          <Download className="h-4 w-4 mr-2" />
          JSON
        </Button>
        <Button
          variant="outline"
          onClick={() => exportData("csv")}
          disabled={!data}
        >
          <Download className="h-4 w-4 mr-2" />
          CSV
        </Button>
      </div>
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Nodes</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalNodes}</div>
            <p className="text-xs text-muted-foreground">
              Nodes in search tree
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Max Depth</CardTitle>
            <Layers className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.maxDepth}</div>
            <p className="text-xs text-muted-foreground">Maximum tree depth</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Avg Node Value
            </CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.avgNodeValue.toFixed(3)}
            </div>
            <p className="text-xs text-muted-foreground">
              Average performance score
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Concepts Explored
            </CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.keys(stats.conceptDistribution).length}
            </div>
            <p className="text-xs text-muted-foreground">Unique concepts</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Combinations</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.keys(stats.conceptCombinations).length}
            </div>
            <p className="text-xs text-muted-foreground">Unique combinations</p>
          </CardContent>
        </Card>
      </div>
      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Phase Distribution */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Phase Distribution</CardTitle>
            <PieChartIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={phaseData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ phase, count, percent }) =>
                      `${phase}: ${(percent * 100).toFixed(0)}%`
                    }
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {phaseData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value, name) => [value, "Nodes"]} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
        {/* Difficulty Distribution */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Difficulty Distribution</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={difficultyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="difficulty"
                    angle={-45}
                    textAnchor="end"
                    height={60}
                    fontSize={12}
                  />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
        {/* Top Concepts */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Top Explored Concepts</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={conceptData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis
                    dataKey="concept"
                    type="category"
                    width={120}
                    fontSize={12}
                  />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
      {/* Phase Statistics Detail */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Phase Statistics</CardTitle>
          <ListOrdered className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(stats.phaseDistribution).map(([phase, count]) => {
              const percentage = ((count / stats.totalNodes) * 100).toFixed(1);
              const color =
                PHASE_COLORS[parseInt(phase) as keyof typeof PHASE_COLORS];

              return (
                <div key={phase} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Badge style={{ backgroundColor: color, color: "white" }}>
                      Phase {phase}
                    </Badge>
                    <span className="text-sm font-medium">{count} nodes</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full"
                      style={{
                        width: `${percentage}%`,
                        backgroundColor: color,
                      }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {percentage}% of total nodes
                  </p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
      {/* Concept Distribution Detail */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>All Concepts</CardTitle>
          <Brain className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {Object.entries(stats.conceptDistribution)
              .sort((a, b) => b[1] - a[1])
              .map(([concept, count]) => (
                <Badge
                  key={concept}
                  variant="secondary"
                  className="flex items-center gap-1"
                >
                  {concept}
                  <span className="bg-primary/20 text-primary px-1 rounded text-xs">
                    {count}
                  </span>
                </Badge>
              ))}
          </div>
        </CardContent>
      </Card>
      {/* Concept Combinations Detail */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>All Concept Combinations</CardTitle>
          <Brain className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {Object.entries(stats.conceptCombinations)
              .sort((a, b) => b[1] - a[1])
              .map(([combination, count]) => (
                <Badge
                  key={combination}
                  variant="outline"
                  className="flex items-center gap-1"
                >
                  {combination}
                  <span className="bg-secondary/20 text-secondary-foreground px-1 rounded text-xs">
                    {count}
                  </span>
                </Badge>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
