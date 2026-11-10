import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getCatalogRepository } from "../../repositories/catalogRepository";
const repo = getCatalogRepository(),
  colors = ["#4f46e5", "#06b6d4", "#7c3aed", "#10b981", "#f59e0b", "#f43f5e"];
const count = (xs: string[]) =>
  [
    ...xs.reduce(
      (m, x) => m.set(x, (m.get(x) || 0) + 1),
      new Map<string, number>(),
    ),
  ]
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);
export default function StatisticsDashboard() {
  const p = repo.getRaw(),
    m = p.manifest as any,
    rows = repo.getCoverageReport(),
    resourceTypes = count(repo.getCourses().map((x) => x.resourceType)).slice(
      0,
      8,
    ),
    skillTypes = count(repo.getSkills().map((x) => x.skillType)),
    relations = [
      "requires_skill",
      "teaches",
      "offered_by",
      "esco_skill_group",
      "esco_skill_broader",
      "esco_group_broader",
      "esco_skill_knowledge",
    ].map((name) => ({ name, value: p.collections[name].length }));
  return (
    <div className="container">
      <div className="page-head">
        <div className="eyebrow">V3.55 DATA DASHBOARD</div>
        <h1>Thống kê dữ liệu</h1>
        <p>
          Coverage phản ánh liên kết direct_topic, không phải career fit score
          hay mức thành thạo.
        </p>
      </div>
      <div className="stat-summary">
        <div>
          <strong>5.718</strong>
          <span>Tổng bản ghi</span>
        </div>
        <div>
          <strong>
            {m.essential_direct}/{m.essential_total}
          </strong>
          <span>Essential direct_topic</span>
        </div>
        <div>
          <strong>{m.essential_missing}</strong>
          <span>Essential chưa có direct_topic</span>
        </div>
      </div>
      <div className="chart-grid">
        <Chart title="Coverage Essential theo nghề">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={rows} margin={{ left: 0, right: 8, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="career"
                interval={0}
                angle={-35}
                textAnchor="end"
                fontSize={9}
              />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar
                dataKey="covered"
                name="Có direct_topic"
                stackId="a"
                fill="#4f46e5"
              />
              <Bar
                dataKey="missing"
                name="Còn thiếu"
                stackId="a"
                fill="#f59e0b"
              />
            </BarChart>
          </ResponsiveContainer>
        </Chart>
        <Chart title="Loại kỹ năng">
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie
                data={skillTypes}
                dataKey="value"
                nameKey="name"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={3}
              >
                {skillTypes.map((_, i) => (
                  <Cell key={i} fill={colors[i % colors.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Chart>
        <Chart title="Định dạng học liệu phổ biến">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart
              data={resourceTypes}
              layout="vertical"
              margin={{ left: 120 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis type="category" dataKey="name" fontSize={9} width={115} />
              <Tooltip />
              <Bar
                dataKey="value"
                name="Học liệu"
                fill="#06b6d4"
                radius={[0, 6, 6, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </Chart>
        <Chart title="Phân bố quan hệ đồ thị">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={relations} layout="vertical" margin={{ left: 100 }}>
              <XAxis type="number" />
              <YAxis type="category" dataKey="name" width={100} fontSize={9} />
              <Tooltip />
              <Bar dataKey="value" fill="#7c3aed" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Chart>
      </div>
      <section className="content-section">
        <h2>Chi tiết coverage theo nghề</h2>
        <div className="coverage-list">
          {rows.map((x) => (
            <div key={x.career}>
              <div>
                <b>{x.career}</b>
                <span>
                  {x.covered}/{x.essential} · thiếu {x.missing}
                </span>
              </div>
              <div className="bar">
                <i style={{ width: `${x.pct}%` }} />
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
const Chart = ({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) => (
  <section className="chart-card">
    <h3>{title}</h3>
    {children}
  </section>
);
