import { useEffect, useMemo, useState } from "react";
import { Link, NavLink, Route, Routes, useParams } from "react-router-dom";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { Background, Controls, MiniMap, ReactFlow } from "@xyflow/react";
import {
  ArrowLeft,
  ArrowRight,
  BarChart3,
  BookmarkCheck,
  BookmarkPlus,
  BookOpen,
  BrainCircuit,
  BriefcaseBusiness,
  Building2,
  Check,
  Database,
  ExternalLink,
  Layers3,
  Menu,
  Moon,
  Network,
  Search,
  Sun,
  X,
} from "lucide-react";
import { getCatalogRepository } from "./repositories/catalogRepository";
import { calculateEssentialSelfDeclaration } from "./features/skillGap/skillGapModel";
import { useUserStore } from "./stores/userStore";
import type { Career, Course, Skill } from "./types/catalog";
import { validExternalHttpUrl } from "./utils/externalUrl";
import GraphExplorer from "./features/graph/GraphExplorer";
import StatisticsDashboard from "./features/statistics/StatisticsDashboard";
import MyLearningPage from "./features/learning/MyLearningPage";
const repo = getCatalogRepository(),
  PAGE = 18;
const pretty = (s: string) =>
  s.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase());
function App() {
  const [dark, setDark] = useState(
      () => localStorage.getItem("theme") === "dark",
    ),
    [menu, setMenu] = useState(false);
  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);
  const nav = [
    ["/dashboard", "Tổng quan"],
    ["/careers", "Nghề nghiệp"],
    ["/skills", "Kỹ năng"],
    ["/skill-taxonomy", "ESCO Taxonomy"],
    ["/resources", "Học liệu"],
    ["/providers", "Nhà cung cấp"],
    ["/graph", "Skill Graph"],
    ["/statistics", "Thống kê"],
    ["/data-quality", "Chất lượng dữ liệu"],
  ];
  return (
    <div className="app">
      <header className="site-header">
        <Link className="brand" to="/" aria-label="SkillGraph - Trang chủ">
          <span className="brand-mark">
            <Network />
          </span>
          <span>
            Skill<span>Graph</span>
          </span>
        </Link>
        <nav className="desktop-nav" aria-label="Điều hướng chính">
          {nav.map(([to, n]) => (
            <NavLink key={to} to={to} onClick={() => setMenu(false)}>
              {n}
            </NavLink>
          ))}
        </nav>
        <span className="version">v3.55 · S92</span>
        <Link className="header-cta" to="/careers">
          Khám phá nghề
        </Link>
        <button
          className="icon-btn mobile"
          onClick={() => setMenu(!menu)}
          aria-label={menu ? "Đóng menu" : "Mở menu"}
          aria-expanded={menu}
        >
          {menu ? <X /> : <Menu />}
        </button>
        <button
          className="icon-btn"
          onClick={() => setDark(!dark)}
          aria-label={dark ? "Bật giao diện sáng" : "Bật giao diện tối"}
        >
          {dark ? <Sun /> : <Moon />}
        </button>
      </header>
      <AnimatePresence>
        {menu && (
          <>
            <motion.button
              className="drawer-backdrop"
              aria-label="Đóng menu"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMenu(false)}
            />
            <motion.aside
              className="mobile-drawer"
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 30, stiffness: 320 }}
            >
              <div className="drawer-head">
                <span>Điều hướng</span>
                <button className="icon-btn" onClick={() => setMenu(false)}>
                  <X />
                </button>
              </div>
              {nav.map(([to, n]) => (
                <NavLink key={to} to={to} onClick={() => setMenu(false)}>
                  {n} <ArrowRight />
                </NavLink>
              ))}
              <Link
                className="btn primary"
                to="/career-goal"
                onClick={() => setMenu(false)}
              >
                Bắt đầu lộ trình mô phỏng
              </Link>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/careers" element={<Careers />} />
          <Route path="/careers/:id" element={<CareerDetail />} />
          <Route path="/skills" element={<Skills />} />
          <Route path="/skills/:id" element={<SkillDetail />} />
          <Route path="/skill-taxonomy" element={<Taxonomy />} />
          <Route path="/resources" element={<Resources />} />
          <Route path="/resources/:id" element={<ResourceDetail />} />
          <Route path="/providers" element={<Providers />} />
          <Route path="/graph" element={<GraphExplorer />} />
          <Route path="/career-goal" element={<CareerGoal />} />
          <Route path="/my-skills" element={<MySkills />} />
          <Route path="/skill-gap" element={<SkillGap />} />
          <Route path="/learning-path" element={<LearningPath />} />
          <Route path="/my-learning" element={<MyLearning />} />
          <Route path="/statistics" element={<Statistics />} />
          <Route path="/data-quality" element={<DataQuality />} />
          <Route path="/about" element={<About />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <footer>
        <div className="brand">
          <span className="brand-mark">
            <Network />
          </span>
          SkillGraph
        </div>
        <p>React Frontend → Local v3.55 Adapter</p>
        <Link to="/about">Giới thiệu & giới hạn dữ liệu</Link>
      </footer>
    </div>
  );
}
const Head = ({
  tag,
  title,
  text,
}: {
  tag: string;
  title: string;
  text: string;
}) => (
  <motion.div
    className="page-head"
    initial={{ opacity: 0, y: 18 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.45 }}
  >
    <div className="eyebrow">{tag}</div>
    <h1>{title}</h1>
    <p>{text}</p>
  </motion.div>
);
const SearchBox = ({
  value,
  set,
  placeholder,
}: {
  value: string;
  set: (v: string) => void;
  placeholder: string;
}) => (
  <label className="search">
    <Search />
    <input
      value={value}
      onChange={(e) => set(e.target.value)}
      placeholder={placeholder}
    />
  </label>
);
const Empty = () => (
  <div className="empty">
    <Search />
    <h3>Không tìm thấy kết quả</h3>
    <p>Hãy thử từ khóa hoặc bộ lọc khác.</p>
  </div>
);
function Pager({
  page,
  total,
  set,
}: {
  page: number;
  total: number;
  set: (n: number) => void;
}) {
  const n = Math.ceil(total / PAGE);
  return n > 1 ? (
    <div className="pagination">
      <button disabled={page === 1} onClick={() => set(page - 1)}>
        Trước
      </button>
      <span>
        {page} / {n}
      </span>
      <button disabled={page === n} onClick={() => set(page + 1)}>
        Sau
      </button>
    </div>
  ) : null;
}
function Home() {
  const m = repo.getRaw().manifest as any;
  const cards = [
    [repo.getCareers().length, "Nghề nghiệp", BriefcaseBusiness],
    [repo.getSkills().length, "Kỹ năng", BrainCircuit],
    [repo.getCourses().length, "Học liệu", BookOpen],
    [repo.getSkillGroups().length, "Nhóm ESCO", Layers3],
    [repo.getProviders().length, "Nhà cung cấp", Building2],
  ] as const;
  const reduceMotion = useReducedMotion();
  return (
    <>
      <section className="hero">
        <motion.div
          className="hero-copy"
          initial={reduceMotion ? false : { opacity: 0, x: -32 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="eyebrow">
            <span /> ARANGODB · TEAM PREVIEW
          </div>
          <h1>
            Khám phá kỹ năng —<br />
            <em>Kiến tạo hành trình nghề nghiệp</em>
          </h1>
          <p>
            Khám phá mối quan hệ giữa nghề nghiệp, kỹ năng và học liệu thông qua
            Skill Graph sử dụng ArangoDB.
          </p>
          <div className="actions">
            <Link className="btn primary" to="/careers">
              Khám phá nghề nghiệp <ArrowRight />
            </Link>
            <Link className="btn secondary" to="/graph">
              Xem Skill Graph <Network />
            </Link>
            <Link className="btn secondary" to="/career-goal">
              Lộ trình mô phỏng
            </Link>
          </div>
          <small className="notice">
            v3.55/Sprint 92 · Team preview, chưa data freeze
          </small>
        </motion.div>
        <motion.div
          className="graph-art"
          initial={reduceMotion ? false : { opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.65, delay: 0.1 }}
        >
          <div className="glow" />
          <svg className="graph-links" viewBox="0 0 600 500" aria-hidden="true">
            <path d="M300 250 L120 105 M300 250 L485 105 M300 250 L115 390 M300 250 L480 390 M300 250 L300 54" />
          </svg>
          <div className="node center">
            <Network />
            <b>Skill Graph</b>
          </div>
          <div className="node n1">
            <BriefcaseBusiness />
            <b>Career</b>
          </div>
          <div className="node n2">
            <BrainCircuit />
            <b>Skill</b>
          </div>
          <div className="node n3">
            <BookOpen />
            <b>Resource</b>
          </div>
          <div className="node n4">
            <Layers3 />
            <b>ESCO Group</b>
          </div>
          <div className="node n5">
            <Building2 />
            <b>Provider</b>
          </div>
          <span className="relation-label rl1">requires_skill</span>
          <span className="relation-label rl2">teaches</span>
          <span className="relation-label rl3">offered_by</span>
        </motion.div>
      </section>
      <section className="stats">
        {cards.map(([v, n, I], index) => (
          <motion.div
            className="stat"
            key={n}
            initial={reduceMotion ? false : { opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.35 }}
            transition={{ delay: index * 0.06 }}
            whileHover={reduceMotion ? undefined : { y: -6 }}
          >
            <div className="stat-icon">
              <I />
            </div>
            <div>
              <strong>{v}</strong>
              <span>{n}</span>
            </div>
          </motion.div>
        ))}
      </section>
      <section className="section">
        <div className="section-heading">
          <div>
            <div className="eyebrow">DỮ LIỆU ĐỒ THỊ</div>
            <h2>
              {m.essential_direct}/{m.essential_total} yêu cầu Essential có
              direct_topic
            </h2>
          </div>
          <Link className="text-link" to="/statistics">
            Xem thống kê <ArrowRight />
          </Link>
        </div>
        <div className="steps">
          <Info
            n="01"
            t="Chọn nghề"
            x="Khám phá yêu cầu Essential và Optional."
          />
          <Info
            n="02"
            t="Khai báo kỹ năng"
            x="Lưu trạng thái mô phỏng trên trình duyệt."
          />
          <Info
            n="03"
            t="Khám phá học liệu"
            x="Xem bằng chứng chủ đề và giới hạn ánh xạ."
          />
        </div>
      </section>
    </>
  );
}
const Info = ({ n, t, x }: { n: string; t: string; x: string }) => (
  <motion.div
    className="step"
    initial={{ opacity: 0, y: 18 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, amount: 0.4 }}
    whileHover={{ y: -6 }}
  >
    <span className="step-number">{n}</span>
    <h3>{t}</h3>
    <p>{x}</p>
  </motion.div>
);
function Dashboard() {
  const st = useUserStore(),
    car = st.selectedCareerId ? repo.getCareerById(st.selectedCareerId) : null,
    req = car
      ? repo
          .getCareerRequirements(car.id)
          .filter((x) => x.requirementType === "essential")
      : [],
    done = req.filter((x) => st.declaredSkillIds.includes(x.skill.id)).length;
  return (
    <div className="container">
      <Head
        tag="DASHBOARD MÔ PHỎNG"
        title="Tổng quan hành trình"
        text="Trạng thái cá nhân được lưu cục bộ, chưa đồng bộ máy chủ."
      />
      <div className="stat-summary">
        <Metric v={car?.name || "Chưa chọn"} l="Nghề mục tiêu" />
        <Metric v={`${done}/${req.length}`} l="Essential đã tự khai báo" />
        <Metric v={st.savedResourceIds.length} l="Học liệu đã lưu" />
      </div>
      <div className="actions">
        <Link className="btn primary" to={car ? "/my-skills" : "/career-goal"}>
          {car ? "Cập nhật kỹ năng" : "Chọn nghề mục tiêu"}
        </Link>
        <Link className="btn secondary" to="/graph">
          Mở Skill Graph
        </Link>
      </div>
    </div>
  );
}
const Metric = ({ v, l }: { v: string | number; l: string }) => (
  <div>
    <strong>{v}</strong>
    <span>{l}</span>
  </div>
);
function Careers() {
  const [q, setQ] = useState(""),
    [g, setG] = useState("");
  const all = repo.getCareers(),
    groups = [...new Set(all.map((x) => x.careerGroup))],
    f = all.filter(
      (x) =>
        (x.name + x.description).toLowerCase().includes(q.toLowerCase()) &&
        (!g || x.careerGroup === g),
    );
  return (
    <div className="container">
      <Head
        tag="CAREER EXPLORER"
        title="Khám phá 12 nghề nghiệp"
        text="Dữ liệu nghề và quan hệ kỹ năng từ ESCO."
      />
      <div className="toolbar">
        <SearchBox value={q} set={setQ} placeholder="Tìm nghề..." />
        <select value={g} onChange={(e) => setG(e.target.value)}>
          <option value="">Tất cả nhóm</option>
          {groups.map((x) => (
            <option key={x}>{x}</option>
          ))}
        </select>
      </div>
      <div className="catalog-grid">
        {f.map((x) => (
          <CareerCard key={x.id} x={x} />
        ))}
      </div>
    </div>
  );
}
function CareerCard({ x }: { x: Career }) {
  const r = repo.getCareerRequirements(x.id),
    setCareer = useUserStore((s) => s.setCareer);
  return (
    <article className="catalog-card">
      <div className="card-top">
        <span className="card-icon">
          <BriefcaseBusiness />
        </span>
        <span className="pill">ISCO {x.iscoGroup}</span>
      </div>
      <h3>{x.name}</h3>
      <p className="muted">{x.careerGroup}</p>
      <p className="clamp">{x.description}</p>
      <div className="counts">
        <span>
          <b>{r.filter((y) => y.requirementType === "essential").length}</b>{" "}
          Essential
        </span>
        <span>
          <b>{r.filter((y) => y.requirementType === "optional").length}</b>{" "}
          Optional
        </span>
      </div>
      <div className="card-actions">
        <Link className="card-link" to={`/careers/${x.key}`}>
          Chi tiết <ArrowRight />
        </Link>
        <button onClick={() => setCareer(x.id)}>Chọn mục tiêu</button>
      </div>
    </article>
  );
}
function CareerDetail() {
  const { id = "" } = useParams(),
    x = repo.getCareerById(id),
    [tab, setTab] = useState("essential"),
    [q, setQ] = useState("");
  const setCareer = useUserStore((s) => s.setCareer);
  if (!x) return <NotFound />;
  const all = repo.getCareerRequirements(x.id),
    rows = all.filter(
      (r) =>
        r.requirementType === tab &&
        r.skill.name.toLowerCase().includes(q.toLowerCase()),
    );
  const cov = repo.getCoverageReport().find((r) => r.career === x.name);
  return (
    <div className="container">
      <Link className="back" to="/careers">
        <ArrowLeft /> Nghề nghiệp
      </Link>
      <section className="detail-hero">
        <div>
          <span className="pill">{x.careerGroup}</span>
          <h1>{x.name}</h1>
          <p>{x.description}</p>
          <a href={x.escoUri} target="_blank" rel="noreferrer">
            ESCO <ExternalLink />
          </a>
          <button className="btn primary" onClick={() => setCareer(x.id)}>
            Chọn làm mục tiêu
          </button>
        </div>
        <div className="metric-card">
          <strong>{all.length}</strong>
          <span>Yêu cầu kỹ năng</span>
          <div>
            {all.filter((r) => r.requirementType === "essential").length}{" "}
            Essential ·{" "}
            {all.filter((r) => r.requirementType === "optional").length}{" "}
            Optional
          </div>
        </div>
      </section>
      {cov && <Coverage value={cov.covered} total={cov.essential} />}
      <div className="content-section">
        <div className="tabs">
          <button
            className={tab === "essential" ? "active" : ""}
            onClick={() => setTab("essential")}
          >
            Essential
          </button>
          <button
            className={tab === "optional" ? "active" : ""}
            onClick={() => setTab("optional")}
          >
            Optional
          </button>
        </div>
        <SearchBox value={q} set={setQ} placeholder="Tìm kỹ năng..." />
        <div className="list">
          {rows.map((r) => (
            <Link className="list-row" key={r.id} to={`/skills/${r.skill.key}`}>
              <span className="skill-dot" />
              <div>
                <h3>{r.skill.name}</h3>
                <p>{r.skill.description}</p>
              </div>
              <span className="resource-count">{r.resourceCount} học liệu</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
const Coverage = ({ value, total }: { value: number; total: number }) => (
  <div className="coverage">
    <b>
      {value}/{total}
    </b>
    <span>Mức bao phủ học liệu trực tiếp theo yêu cầu Essential</span>
    <div className="bar">
      <i style={{ width: `${(value / total) * 100}%` }} />
    </div>
    <small>direct_topic không chứng minh mức độ thành thạo.</small>
  </div>
);
const SelfDeclaredEssentialProgress = ({
  value,
  total,
  percentage,
}: {
  value: number;
  total: number;
  percentage: number;
}) => {
  const formattedPercentage = new Intl.NumberFormat("vi-VN", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(percentage);
  return (
    <div className="coverage">
      <b>
        {value}/{total} · {formattedPercentage}%
      </b>
      <span>Kỹ năng Essential đã tự khai báo</span>
      <div
        className="bar"
        role="progressbar"
        aria-label="Kỹ năng Essential đã tự khai báo"
        aria-valuemin={0}
        aria-valuemax={total}
        aria-valuenow={value}
        aria-valuetext={`${value}/${total}, ${formattedPercentage}%`}
      >
        <i style={{ width: `${percentage}%` }} />
      </div>
      <small>
        Kết quả dựa trên kỹ năng người dùng tự khai báo, không chứng minh mức độ
        thành thạo.
      </small>
    </div>
  );
};
function Skills() {
  const [q, setQ] = useState(""),
    [type, setType] = useState(""),
    [page, setPage] = useState(1),
    all = repo.getSkills(),
    types = [...new Set(all.map((x) => x.skillType))],
    f = all.filter(
      (x) =>
        (x.name + x.description).toLowerCase().includes(q.toLowerCase()) &&
        (!type || x.skillType === type),
    );
  return (
    <div className="container">
      <Head
        tag="SKILL EXPLORER"
        title="420 kỹ năng ESCO"
        text="Tìm kiếm kỹ năng và khám phá các liên kết nghề nghiệp, học liệu."
      />
      <div className="toolbar">
        <SearchBox
          value={q}
          set={(v) => {
            setQ(v);
            setPage(1);
          }}
          placeholder="Tìm kỹ năng..."
        />
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="">Tất cả loại</option>
          {types.map((x) => (
            <option key={x}>{pretty(x)}</option>
          ))}
        </select>
      </div>
      <div className="list cards">
        {f.slice((page - 1) * PAGE, page * PAGE).map((x) => (
          <SkillRow key={x.id} x={x} />
        ))}
      </div>
      {!f.length && <Empty />}
      <Pager page={page} total={f.length} set={setPage} />
    </div>
  );
}
const SkillRow = ({ x }: { x: Skill }) => (
  <Link className="list-row" to={`/skills/${x.key}`}>
    <span className="card-icon">
      <BrainCircuit />
    </span>
    <div>
      <span className="pill">{pretty(x.skillType)}</span>
      <h3>{x.name}</h3>
      <p>{x.description}</p>
    </div>
    <ArrowRight className="row-arrow" />
  </Link>
);
function SkillDetail() {
  const { id = "" } = useParams(),
    x = repo.getSkillById(id);
  if (!x) return <NotFound />;
  const careers = repo.getCareersForSkill(x.id),
    resources = repo.getCoursesForSkill(x.id);
  return (
    <div className="container">
      <Link className="back" to="/skills">
        <ArrowLeft /> Kỹ năng
      </Link>
      <section className="detail-hero">
        <div>
          <span className="pill">{pretty(x.skillType)}</span>
          <h1>{x.name}</h1>
          <p>{x.description}</p>
          <a href={x.escoUri} target="_blank" rel="noreferrer">
            ESCO <ExternalLink />
          </a>
        </div>
        <div className="metric-card">
          <strong>{careers.length}</strong>
          <span>Nghề yêu cầu</span>
          <div>{resources.length} học liệu liên quan</div>
        </div>
      </section>
      <div className="content-section">
        <h2>Nghề nghiệp liên quan</h2>
        <div className="chip-list">
          {careers.map((y) => (
            <Link key={y.career.id} to={`/careers/${y.career.key}`}>
              <span>{y.career.name}</span>
              <small>{pretty(y.type)}</small>
            </Link>
          ))}
        </div>
      </div>
      <div className="content-section">
        <h2>Học liệu và bằng chứng</h2>
        <div className="catalog-grid resources">
          {resources.map((y) => (
            <ResourceCard
              key={y.course.id}
              x={y.course}
              scopes={y.evidence.map((e) => e.evidenceScope)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
function Taxonomy() {
  const [q, setQ] = useState(""),
    [selected, setSelected] = useState("");
  const groups = repo
      .getSkillGroups()
      .filter((x) => (x.name + x.code).toLowerCase().includes(q.toLowerCase())),
    skills = selected ? repo.getSkillsInGroup(selected) : [];
  return (
    <div className="container">
      <Head
        tag="ESCO TAXONOMY"
        title="149 nhóm kỹ năng"
        text="Quan hệ phân loại ESCO; không phải thứ tự học hay prerequisite."
      />
      <SearchBox value={q} set={setQ} placeholder="Tìm nhóm kỹ năng..." />
      <div className="taxonomy">
        <div className="group-list">
          {groups.map((g) => (
            <button
              className={selected === g.id ? "active" : ""}
              onClick={() => setSelected(g.id)}
              key={g.id}
            >
              <b>{g.code}</b>
              <span>{g.name}</span>
            </button>
          ))}
        </div>
        <div className="taxonomy-detail">
          {selected ? (
            <>
              <h2>
                {repo.getSkillGroups().find((g) => g.id === selected)?.name}
              </h2>
              {skills.map((s) => (
                <SkillRow key={s.id} x={s} />
              ))}
            </>
          ) : (
            <Empty />
          )}
        </div>
      </div>
    </div>
  );
}
function Resources() {
  const [q, setQ] = useState(""),
    [type, setType] = useState(""),
    [page, setPage] = useState(1),
    all = repo.getCourses(),
    types = [...new Set(all.map((x) => x.resourceType))].sort(),
    f = all.filter(
      (x) =>
        (x.title + x.providerName).toLowerCase().includes(q.toLowerCase()) &&
        (!type || x.resourceType === type),
    );
  return (
    <div className="container">
      <Head
        tag="RESOURCE CATALOG"
        title="504 học liệu"
        text="Tài liệu, tutorial, course và các loại tài nguyên khác theo metadata gốc."
      />
      <div className="toolbar">
        <SearchBox
          value={q}
          set={setQ}
          placeholder="Tìm học liệu hoặc nhà cung cấp..."
        />
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="">Tất cả định dạng</option>
          {types.map((x) => (
            <option key={x} value={x}>
              {pretty(x)}
            </option>
          ))}
        </select>
      </div>
      <div className="catalog-grid resources">
        {f.slice((page - 1) * PAGE, page * PAGE).map((x) => (
          <ResourceCard key={x.id} x={x} />
        ))}
      </div>
      <Pager page={page} total={f.length} set={setPage} />
    </div>
  );
}
function ResourceCard({ x, scopes = [] }: { x: Course; scopes?: string[] }) {
  const save = useUserStore((s) => s.toggleSaved),
    saved = useUserStore((s) => s.savedResourceIds.includes(x.id));
  return (
    <article className="catalog-card resource">
      <div className="card-top">
        <span className="card-icon">
          <BookOpen />
        </span>
        <span className="pill">{x.language.toUpperCase()}</span>
      </div>
      <h3>{x.title}</h3>
      <p className="muted">{x.providerName}</p>
      <div className="tags">
        <span>{pretty(x.resourceType)}</span>
        {x.level && <span>{pretty(x.level)}</span>}
        {[...new Set(scopes)].map((s) => (
          <span className={s === "direct_topic" ? "direct" : ""} key={s}>
            {pretty(s)}
          </span>
        ))}
      </div>
      <div className="card-actions resource-card-footer">
        <Link className="card-link" to={`/resources/${x.key}`}>
          Chi tiết <ArrowRight />
        </Link>
        <button
          className={`resource-save-btn ${saved ? "is-saved" : ""}`}
          type="button"
          aria-pressed={saved}
          aria-label={saved ? `Bỏ lưu ${x.title}` : `Lưu học liệu ${x.title}`}
          title={saved ? "Nhấn để bỏ lưu học liệu" : "Lưu học liệu"}
          onClick={() => save(x.id)}
        >
          {saved ? (
            <>
              <BookmarkCheck aria-hidden="true" /> Đã lưu
            </>
          ) : (
            <>
              <BookmarkPlus aria-hidden="true" /> Lưu học liệu
            </>
          )}
        </button>
      </div>
    </article>
  );
}
function ResourceDetail() {
  const { id = "" } = useParams(),
    x = repo.getCourseById(id);
  if (!x) return <NotFound />;
  const skills = repo.getSkillsForCourse(x.id),
    sourceUrl = validExternalHttpUrl(x.canonicalUrl);
  return (
    <div className="container">
      <Link className="back" to="/resources">
        <ArrowLeft /> Học liệu
      </Link>
      <section className="detail-hero">
        <div>
          <span className="pill">{pretty(x.resourceType)}</span>
          <h1>{x.title}</h1>
          <p>{x.providerName}</p>
          {sourceUrl ? (
            <a
              className="btn primary resource-source-btn"
              href={sourceUrl}
              target="_blank"
              rel="noreferrer"
            >
              Mở nguồn <ExternalLink aria-hidden="true" />
            </a>
          ) : (
            <span className="resource-source-unavailable">
              <button
                className="btn resource-source-btn"
                type="button"
                disabled
                aria-describedby="resource-source-reason"
              >
                Chưa có liên kết <ExternalLink aria-hidden="true" />
              </button>
              <small id="resource-source-reason">
                Học liệu này chưa có URL nguồn HTTP/HTTPS hợp lệ.
              </small>
            </span>
          )}
        </div>
        <div className="metric-card resource-meta">
          <span>
            Ngôn ngữ <b>{x.language.toUpperCase()}</b>
          </span>
          <span>
            Trình độ <b>{x.level || "Chưa xác minh"}</b>
          </span>
          <span>
            Chứng chỉ{" "}
            <b>
              {x.certificateAvailable === null
                ? "Chưa xác minh"
                : x.certificateAvailable
                  ? "Có"
                  : "Không"}
            </b>
          </span>
          <span>
            Kết quả thành thạo{" "}
            <b>{x.verifiedOutcomeProficiency || "Chưa xác minh"}</b>
          </span>
        </div>
      </section>
      <div className="content-section">
        <h2>Kỹ năng liên quan</h2>
        <div className="list">
          {skills.map((s) => (
            <Link
              className="list-row"
              key={s.skill.id}
              to={`/skills/${s.skill.key}`}
            >
              <span className="skill-dot" />
              <div>
                <h3>{s.skill.name}</h3>
                {s.evidence.map((e) => (
                  <p key={e.edge.id}>
                    <b>{pretty(e.evidenceScope)}</b>
                    {e.evidenceLimit && ` — ${e.evidenceLimit}`}
                  </p>
                ))}
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
function Providers() {
  const [q, setQ] = useState(""),
    all = repo.getProviders(),
    f = all.filter((x) => x.name.toLowerCase().includes(q.toLowerCase()));
  return (
    <div className="container">
      <Head
        tag="PROVIDERS"
        title="179 nhà cung cấp"
        text="Nhà xuất bản và tổ chức cung cấp học liệu trong release."
      />
      <SearchBox value={q} set={setQ} placeholder="Tìm nhà cung cấp..." />
      <div className="catalog-grid">
        {f.map((x) => {
          const n = repo.getCoursesByProvider(x.id).length;
          return (
            <article className="catalog-card" key={x.id}>
              <span className="card-icon">
                <Database />
              </span>
              <h3>{x.name}</h3>
              <p>{n} học liệu</p>
              {x.officialWebsite && (
                <a href={x.officialWebsite} target="_blank" rel="noreferrer">
                  Website <ExternalLink />
                </a>
              )}
            </article>
          );
        })}
      </div>
    </div>
  );
}
function GraphPage() {
  const [first] = repo.getCareers(),
    [career, setCareer] = useState(first.id);
  const data = repo.getGraphForCareer(career),
    nodes = data.nodes.slice(0, 80).map((n, i) => ({
      id: n.id,
      data: { label: n.label },
      position: { x: (i % 8) * 180, y: Math.floor(i / 8) * 100 },
      style: {
        background: n.type === "career" ? "#4f46e5" : "#06b6d4",
        color: "#fff",
        border: 0,
        borderRadius: 12,
        width: 150,
      },
    })),
    edges = data.edges
      .filter((e) => nodes.some((n) => n.id === e.target))
      .map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        label: "requires_skill",
      }));
  return (
    <div className="container graph-page">
      <Head
        tag="INTERACTIVE GRAPH"
        title="Skill Graph tập trung"
        text="Chỉ tải subgraph của một nghề; hướng cạnh Career → Skill."
      />
      <select value={career} onChange={(e) => setCareer(e.target.value)}>
        {repo.getCareers().map((x) => (
          <option value={x.id} key={x.id}>
            {x.name}
          </option>
        ))}
      </select>
      <div className="graph-canvas">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background />
          <MiniMap />
          <Controls />
        </ReactFlow>
      </div>
      <p className="notice">
        Đang giới hạn tối đa 80 node để bảo đảm hiệu năng. Không tự sinh
        prerequisite.
      </p>
    </div>
  );
}
function CareerGoal() {
  const setCareer = useUserStore((s) => s.setCareer),
    current = useUserStore((s) => s.selectedCareerId);
  return (
    <div className="container">
      <Head
        tag="CHẾ ĐỘ MÔ PHỎNG"
        title="Chọn nghề mục tiêu"
        text="Mục tiêu được lưu cục bộ trên trình duyệt, chưa đồng bộ máy chủ."
      />
      <div className="catalog-grid">
        {repo.getCareers().map((x) => (
          <button
            className={`goal-card ${current === x.id ? "active" : ""}`}
            key={x.id}
            onClick={() => setCareer(x.id)}
          >
            <BriefcaseBusiness />
            <b>{x.name}</b>
            <span>{x.careerGroup}</span>
          </button>
        ))}
      </div>
      {current && (
        <Link className="btn primary" to="/my-skills">
          Tiếp tục khai báo kỹ năng <ArrowRight />
        </Link>
      )}
    </div>
  );
}
function MySkills() {
  const st = useUserStore(),
    car = st.selectedCareerId ? repo.getCareerById(st.selectedCareerId) : null,
    [q, setQ] = useState("");
  if (!car) return <NeedGoal />;
  const req = repo
    .getCareerRequirements(car.id)
    .filter((x) => x.skill.name.toLowerCase().includes(q.toLowerCase()));
  return (
    <div className="container">
      <Head
        tag="TỰ KHAI BÁO · MÔ PHỎNG"
        title={`Kỹ năng cho ${car.name}`}
        text="Việc đánh dấu không xác nhận mức độ thành thạo."
      />
      <SearchBox value={q} set={setQ} placeholder="Tìm kỹ năng..." />
      <div className="selection-list">
        {req.map((r) => (
          <label key={r.id}>
            <input
              type="checkbox"
              checked={st.declaredSkillIds.includes(r.skill.id)}
              onChange={() => st.toggleSkill(r.skill.id)}
            />
            <span>
              <b>{r.skill.name}</b>
              <small>{pretty(r.requirementType)}</small>
            </span>
          </label>
        ))}
      </div>
      <Link className="btn primary" to="/skill-gap">
        Xem phân tích mô phỏng
      </Link>
    </div>
  );
}
function SkillGap() {
  const st = useUserStore(),
    car = st.selectedCareerId ? repo.getCareerById(st.selectedCareerId) : null;
  if (!car) return <NeedGoal />;
  const requirements = repo.getCareerRequirements(car.id),
    analysis = calculateEssentialSelfDeclaration(
      requirements,
      st.declaredSkillIds,
    ),
    essentialById = new Map(
      requirements
        .filter((item) => item.requirementType === "essential")
        .map((item) => [item.skill.id, item]),
    ),
    req = analysis.essentialSkillIds.map((id) => essentialById.get(id)!),
    done = analysis.declaredEssentialSkillIds,
    missing = analysis.missingEssentialSkillIds.map((id) =>
      essentialById.get(id)!,
    );
  return (
    <div className="container">
      <Head
        tag="PHÂN TÍCH MÔ PHỎNG"
        title="Khoảng trống kỹ năng tự khai báo"
        text="So sánh ID kỹ năng Essential với danh sách người dùng tự đánh dấu."
      />
      <div className="stat-summary">
        <Metric v={req.length} l="Essential" />
        <Metric v={done.length} l="Đã tự khai báo" />
        <Metric v={missing.length} l="Chưa khai báo" />
      </div>
      <SelfDeclaredEssentialProgress
        value={done.length}
        total={req.length}
        percentage={analysis.percentage}
      />
      <div className="content-section">
        <h2>Kỹ năng chưa khai báo</h2>
        {missing.map((x) => (
          <SkillRow key={x.skill.id} x={x.skill} />
        ))}
      </div>
      <Link className="btn primary" to="/learning-path">
        Xem lộ trình minh họa
      </Link>
    </div>
  );
}
function LearningPath() {
  const st = useUserStore(),
    car = st.selectedCareerId ? repo.getCareerById(st.selectedCareerId) : null;
  if (!car) return <NeedGoal />;
  const missing = repo
    .getCareerRequirements(car.id)
    .filter(
      (x) =>
        x.requirementType === "essential" &&
        !st.declaredSkillIds.includes(x.skill.id),
    );
  return (
    <div className="container">
      <Head
        tag="LỘ TRÌNH MÔ PHỎNG"
        title={car.name}
        text="Thứ tự hiển thị ổn định, không phải thứ tự tiên quyết đã xác minh."
      />
      <div className="warning">
        Lộ trình này chỉ minh họa cách khám phá học liệu theo kỹ năng. Học liệu
        chưa được tự động phê duyệt để khuyến nghị, và thứ tự học chưa được xác
        minh.
      </div>
      <div className="timeline">
        {missing.map((r, i) => (
          <section key={r.id}>
            <i>{i + 1}</i>
            <div>
              <h3>{r.skill.name}</h3>
              <div className="catalog-grid resources">
                {repo
                  .getCoursesForSkill(r.skill.id)
                  .slice(0, 3)
                  .map((x) => (
                    <ResourceCard
                      key={x.course.id}
                      x={x.course}
                      scopes={x.evidence.map((e) => e.evidenceScope)}
                    />
                  ))}
              </div>
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
function MyLearning() {
  return <MyLearningPage />;
}
function Statistics() {
  return <StatisticsDashboard />;
}
function DataQuality() {
  const p = repo.getRaw(),
    m = p.manifest as any;
  return (
    <div className="container">
      <Head
        tag="DATA QUALITY"
        title="Minh bạch chất lượng dữ liệu"
        text="Kết quả validation offline, không phải xác minh database live."
      />
      <div className="stat-summary">
        <Metric v={m.version} l="Release" />
        <Metric v={m.records} l="Records" />
        <Metric
          v={m.external_arangodb_verified ? "Có" : "Chưa"}
          l="Live DB verified"
        />
      </div>
      <div className="warning">
        Team preview · chưa DATA FREEZE · 68 ánh xạ tài liệu cũ cần kiểm duyệt
        sâu · 9 trường hợp thiếu ghi chú giới hạn phạm vi · 0 prerequisite edge
        · 0 automatic recommendation approval.
      </div>
      <h2>20 Essential gaps còn lại</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Nghề</th>
              <th>Kỹ năng</th>
              <th>Trạng thái</th>
            </tr>
          </thead>
          <tbody>
            {repo.getRemainingEssentialGaps().map((x, i) => (
              <tr key={i}>
                <td>{x[0]}</td>
                <td>{x[1]}</td>
                <td>{x[4]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
function About() {
  return (
    <div className="container">
      <Head
        tag="ABOUT"
        title="SkillGraph — Career & Learning Explorer"
        text="Đồ án NoSQL trực quan hóa mô hình Career–Skill–Course–Provider trên ArangoDB."
      />
      <div className="steps">
        <Info
          n="HIỆN TẠI"
          t="React → Local v3.55 Adapter"
          x="Demo đọc dữ liệu build-time, không kết nối trực tiếp database."
        />
        <Info
          n="TƯƠNG LAI"
          t="React → Python REST API → ArangoDB"
          x="API production chưa được cung cấp trong release."
        />
        <Info
          n="NGUỒN"
          t="ESCO 1.2.1"
          x="Quan hệ taxonomy không phải prerequisite học tập."
        />
      </div>
    </div>
  );
}
const NeedGoal = () => (
  <div className="container">
    <Head
      tag="CẦN THIẾT LẬP"
      title="Chưa chọn nghề mục tiêu"
      text="Hãy chọn một nghề để tiếp tục luồng mô phỏng."
    />
    <Link className="btn primary" to="/career-goal">
      Chọn nghề
    </Link>
  </div>
);
const NotFound = () => (
  <div className="container">
    <Head
      tag="404"
      title="Không tìm thấy trang"
      text="Đường dẫn hoặc ID không tồn tại trong release v3.55."
    />
    <Link className="btn primary" to="/">
      Về trang chủ
    </Link>
  </div>
);
export default App;
