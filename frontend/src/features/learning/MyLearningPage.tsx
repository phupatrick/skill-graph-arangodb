import { useState } from "react";
import { Link } from "react-router-dom";
import { BookOpen, Eye, Save, Trash2 } from "lucide-react";
import { getCatalogRepository } from "../../repositories/catalogRepository";
import { useUserStore } from "../../stores/userStore";
const repo = getCatalogRepository();
type Filter = "all" | "saved" | "planned" | "viewed";
export default function MyLearningPage() {
  const st = useUserStore(),
    [filter, setFilter] = useState<Filter>("all");
  const ids = new Set([
      ...st.savedResourceIds,
      ...st.plannedResourceIds,
      ...st.viewedResourceIds,
    ]),
    items = repo
      .getCourses()
      .filter(
        (x) =>
          ids.has(x.id) &&
          (filter === "all" ||
            (filter === "saved" && st.savedResourceIds.includes(x.id)) ||
            (filter === "planned" && st.plannedResourceIds.includes(x.id)) ||
            (filter === "viewed" && st.viewedResourceIds.includes(x.id))),
      );
  return (
    <div className="container">
      <div className="page-head">
        <div className="eyebrow">DỮ LIỆU CỤC BỘ · MÔ PHỎNG</div>
        <h1>Học liệu của tôi</h1>
        <p>
          “Đã xem” chỉ ghi nhận thao tác cục bộ, không phải hoàn thành học liệu
          hay xác nhận kỹ năng.
        </p>
      </div>
      <div className="tabs">
        {(["all", "saved", "planned", "viewed"] as Filter[]).map((x) => (
          <button
            className={filter === x ? "active" : ""}
            onClick={() => setFilter(x)}
            key={x}
          >
            {x === "all"
              ? "Tất cả"
              : x === "saved"
                ? "Đã lưu"
                : x === "planned"
                  ? "Dự định xem"
                  : "Đã xem"}
          </button>
        ))}
      </div>
      {items.length ? (
        <div className="learning-list">
          {items.map((x) => (
            <article key={x.id}>
              <span className="card-icon">
                <BookOpen />
              </span>
              <div>
                <Link to={`/resources/${x.key}`}>
                  <h3>{x.title}</h3>
                </Link>
                <p>{x.providerName}</p>
                <div className="learning-actions">
                  <button
                    onClick={() => st.toggleSaved(x.id)}
                    className={
                      st.savedResourceIds.includes(x.id) ? "active" : ""
                    }
                  >
                    <Save /> Lưu
                  </button>
                  <button
                    onClick={() => st.setStatus(x.id, "planned")}
                    className={
                      st.plannedResourceIds.includes(x.id) ? "active" : ""
                    }
                  >
                    Dự định xem
                  </button>
                  <button
                    onClick={() => st.setStatus(x.id, "viewed")}
                    className={
                      st.viewedResourceIds.includes(x.id) ? "active" : ""
                    }
                  >
                    <Eye /> Đã xem
                  </button>
                </div>
                <textarea
                  aria-label={`Ghi chú cho ${x.title}`}
                  value={st.notes[x.id] || ""}
                  onChange={(e) => st.setNote(x.id, e.target.value)}
                  placeholder="Ghi chú cá nhân trên thiết bị..."
                />
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="empty">
          <BookOpen />
          <h3>Chưa có học liệu trong mục này</h3>
          <Link className="btn primary" to="/resources">
            Khám phá học liệu
          </Link>
        </div>
      )}
      <button
        className="btn danger"
        onClick={() =>
          confirm("Xóa toàn bộ dữ liệu mô phỏng trên thiết bị?") && st.reset()
        }
      >
        <Trash2 /> Reset dữ liệu mô phỏng
      </button>
    </div>
  );
}
