type SeriesPoint = {
  day: number;
  value: number;
};

type DualSeriesPoint = {
  day: number;
  primary: number;
  secondary: number;
};

type LineChartProps = {
  data: SeriesPoint[];
  title: string;
  tone?: "blue" | "green" | "red" | "amber";
  formatValue?: (value: number) => string;
};

type BarChartProps = {
  data: SeriesPoint[];
  title: string;
  formatValue?: (value: number) => string;
};

type DualLineChartProps = {
  data: DualSeriesPoint[];
  title: string;
  primaryLabel: string;
  secondaryLabel: string;
  formatValue?: (value: number) => string;
};

const chartWidth = 720;
const chartHeight = 260;
const padding = {
  top: 18,
  right: 24,
  bottom: 32,
  left: 58,
};

const tones = {
  blue: "#2563eb",
  green: "#059669",
  red: "#dc2626",
  amber: "#d97706",
};

function getRange(values: number[]): { min: number; max: number } {
  if (values.length === 0) {
    return { min: 0, max: 1 };
  }

  const min = Math.min(...values);
  const max = Math.max(...values);

  if (min === max) {
    return { min: min - 1, max: max + 1 };
  }

  const paddingValue = (max - min) * 0.08;
  return {
    min: min - paddingValue,
    max: max + paddingValue,
  };
}

function xFor(index: number, length: number): number {
  const innerWidth = chartWidth - padding.left - padding.right;
  return padding.left + (innerWidth * index) / Math.max(length - 1, 1);
}

function yFor(value: number, min: number, max: number): number {
  const innerHeight = chartHeight - padding.top - padding.bottom;
  return padding.top + ((max - value) / (max - min)) * innerHeight;
}

function linePath(data: SeriesPoint[], min: number, max: number): string {
  return data
    .map((point, index) => {
      const command = index === 0 ? "M" : "L";
      return `${command} ${xFor(index, data.length).toFixed(2)} ${yFor(point.value, min, max).toFixed(2)}`;
    })
    .join(" ");
}

function areaPath(data: SeriesPoint[], min: number, max: number): string {
  if (data.length === 0) {
    return "";
  }

  const baseline = yFor(Math.max(0, min), min, max);
  const path = linePath(data, min, max);
  const lastX = xFor(data.length - 1, data.length);
  const firstX = xFor(0, data.length);
  return `${path} L ${lastX.toFixed(2)} ${baseline.toFixed(2)} L ${firstX.toFixed(2)} ${baseline.toFixed(2)} Z`;
}

function AxisLabels({
  min,
  max,
  formatValue,
}: {
  min: number;
  max: number;
  formatValue: (value: number) => string;
}) {
  return (
    <>
      <text className="chart-axis-label" x={padding.left - 10} y={padding.top + 8}>
        {formatValue(max)}
      </text>
      <text className="chart-axis-label" x={padding.left - 10} y={chartHeight - padding.bottom}>
        {formatValue(min)}
      </text>
    </>
  );
}

function ChartFrame({
  children,
  title,
  legend,
}: {
  children: React.ReactNode;
  title: string;
  legend?: React.ReactNode;
}) {
  return (
    <section className="chart-panel" aria-label={title}>
      <div className="chart-panel-header">
        <h2>{title}</h2>
        {legend}
      </div>
      <svg className="chart-svg" viewBox={`0 0 ${chartWidth} ${chartHeight}`} role="img">
        <line
          className="chart-grid-line"
          x1={padding.left}
          x2={chartWidth - padding.right}
          y1={padding.top}
          y2={padding.top}
        />
        <line
          className="chart-grid-line"
          x1={padding.left}
          x2={chartWidth - padding.right}
          y1={(chartHeight - padding.bottom + padding.top) / 2}
          y2={(chartHeight - padding.bottom + padding.top) / 2}
        />
        <line
          className="chart-grid-line"
          x1={padding.left}
          x2={chartWidth - padding.right}
          y1={chartHeight - padding.bottom}
          y2={chartHeight - padding.bottom}
        />
        <line
          className="chart-axis"
          x1={padding.left}
          x2={padding.left}
          y1={padding.top}
          y2={chartHeight - padding.bottom}
        />
        <line
          className="chart-axis"
          x1={padding.left}
          x2={chartWidth - padding.right}
          y1={chartHeight - padding.bottom}
          y2={chartHeight - padding.bottom}
        />
        {children}
      </svg>
    </section>
  );
}

export function LineChart({
  data,
  title,
  tone = "blue",
  formatValue = String,
}: LineChartProps) {
  const { min, max } = getRange(data.map((point) => point.value));

  return (
    <ChartFrame title={title}>
      <AxisLabels min={min} max={max} formatValue={formatValue} />
      <path className="chart-area" d={areaPath(data, min, max)} fill={tones[tone]} />
      <path className="chart-line" d={linePath(data, min, max)} stroke={tones[tone]} />
      <text className="chart-x-label" x={padding.left} y={chartHeight - 10}>
        Day {data[0]?.day ?? 0}
      </text>
      <text className="chart-x-label chart-x-label-end" x={chartWidth - padding.right} y={chartHeight - 10}>
        Day {data[data.length - 1]?.day ?? 0}
      </text>
    </ChartFrame>
  );
}

export function BarChart({ data, title, formatValue = String }: BarChartProps) {
  const { min, max } = getRange(data.map((point) => point.value));
  const baseline = yFor(Math.max(0, min), min, max);
  const innerWidth = chartWidth - padding.left - padding.right;
  const slotWidth = innerWidth / Math.max(data.length, 1);
  const barWidth = Math.max(Math.min(slotWidth * 0.72, 18), 1);

  return (
    <ChartFrame title={title}>
      <AxisLabels min={min} max={max} formatValue={formatValue} />
      {data.map((point, index) => {
        const x = padding.left + slotWidth * index + (slotWidth - barWidth) / 2;
        const y = yFor(point.value, min, max);
        const height = Math.max(Math.abs(baseline - y), 1);
        const isPositive = point.value >= 0;
        return (
          <rect
            className="chart-bar"
            key={point.day}
            x={x}
            y={isPositive ? y : baseline}
            width={barWidth}
            height={height}
            fill={isPositive ? "#059669" : "#dc2626"}
          />
        );
      })}
      <text className="chart-x-label" x={padding.left} y={chartHeight - 10}>
        Day {data[0]?.day ?? 0}
      </text>
      <text className="chart-x-label chart-x-label-end" x={chartWidth - padding.right} y={chartHeight - 10}>
        Day {data[data.length - 1]?.day ?? 0}
      </text>
    </ChartFrame>
  );
}

export function DualLineChart({
  data,
  title,
  primaryLabel,
  secondaryLabel,
  formatValue = String,
}: DualLineChartProps) {
  const primaryData = data.map((point) => ({
    day: point.day,
    value: point.primary,
  }));
  const secondaryData = data.map((point) => ({
    day: point.day,
    value: point.secondary,
  }));
  const { min, max } = getRange(data.flatMap((point) => [point.primary, point.secondary]));

  return (
    <ChartFrame
      title={title}
      legend={
        <div className="chart-legend-row" aria-label={`${primaryLabel} and ${secondaryLabel} legend`}>
          <span>
            <i style={{ backgroundColor: "#7c3aed" }} />
            {primaryLabel}
          </span>
          <span>
            <i style={{ backgroundColor: "#ea580c" }} />
            {secondaryLabel}
          </span>
        </div>
      }
    >
      <AxisLabels min={min} max={max} formatValue={formatValue} />
      <path className="chart-line" d={linePath(primaryData, min, max)} stroke="#7c3aed" />
      <path className="chart-line chart-line-soft" d={linePath(secondaryData, min, max)} stroke="#ea580c" />
    </ChartFrame>
  );
}
