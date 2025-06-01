import * as React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { cn } from "../../lib/utils";

// Chart Container
const ChartContainer = React.forwardRef(
  ({ className, children, ...props }, ref) => (
    <div ref={ref} className={cn("w-full h-[350px]", className)} {...props}>
      <ResponsiveContainer width="100%" height="100%">
        {children}
      </ResponsiveContainer>
    </div>
  )
);
ChartContainer.displayName = "ChartContainer";

// Custom Tooltip
const ChartTooltip = ({ active, payload, label, className, ...props }) => {
  if (active && payload && payload.length) {
    return (
      <div
        className={cn(
          "rounded-lg border bg-background p-2 shadow-sm",
          className
        )}
        {...props}
      >
        <div className="grid grid-cols-2 gap-2">
          <div className="flex flex-col">
            <span className="text-[0.70rem] uppercase text-muted-foreground">
              {label}
            </span>
            <span className="font-bold text-muted-foreground">
              {payload[0].payload[label]}
            </span>
          </div>
        </div>
      </div>
    );
  }
  return null;
};

// Line Chart Component
const SimpleLineChart = ({
  data,
  dataKey,
  xKey = "name",
  color = "#8884d8",
  ...props
}) => (
  <LineChart data={data} {...props}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey={xKey} />
    <YAxis />
    <Tooltip content={<ChartTooltip />} />
    <Line
      type="monotone"
      dataKey={dataKey}
      stroke={color}
      strokeWidth={2}
      dot={{ fill: color }}
    />
  </LineChart>
);

// Area Chart Component
const SimpleAreaChart = ({
  data,
  dataKey,
  xKey = "name",
  color = "#8884d8",
  ...props
}) => (
  <AreaChart data={data} {...props}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey={xKey} />
    <YAxis />
    <Tooltip content={<ChartTooltip />} />
    <Area
      type="monotone"
      dataKey={dataKey}
      stroke={color}
      fill={color}
      fillOpacity={0.3}
    />
  </AreaChart>
);

// Bar Chart Component
const SimpleBarChart = ({
  data,
  dataKey,
  xKey = "name",
  color = "#8884d8",
  ...props
}) => (
  <BarChart data={data} {...props}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey={xKey} />
    <YAxis />
    <Tooltip content={<ChartTooltip />} />
    <Bar dataKey={dataKey} fill={color} />
  </BarChart>
);

// Pie Chart Component
const SimplePieChart = ({
  data,
  dataKey,
  nameKey = "name",
  colors = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"],
  ...props
}) => (
  <PieChart {...props}>
    <Pie
      data={data}
      cx="50%"
      cy="50%"
      labelLine={false}
      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
      outerRadius={80}
      fill="#8884d8"
      dataKey={dataKey}
    >
      {data.map((entry, index) => (
        <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
      ))}
    </Pie>
    <Tooltip />
  </PieChart>
);

export {
  ChartContainer,
  ChartTooltip,
  SimpleLineChart,
  SimpleAreaChart,
  SimpleBarChart,
  SimplePieChart,
  // Re-export recharts components for advanced usage
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
};
