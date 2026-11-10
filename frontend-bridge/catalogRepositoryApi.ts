/**
 * HttpCatalogRepository — bản cài đặt THẬT của CatalogRepository, gọi API Python.
 *
 * VÌ SAO CẦN FILE NÀY
 * ===================
 * Trong gói bàn giao, `src/repositories/catalogRepository.ts` có lớp
 * `HttpCatalogRepository` nhưng mọi method đều gọi `this.no()` — ném lỗi
 * "API mode chưa có backend production". Nghĩa là đặt VITE_DATA_SOURCE=api
 * cũng không chạy được, vì chưa có code gọi API nào cả.
 *
 * File này là bản cài đặt đầy đủ: gọi `/compat/api/v1/...` của backend
 * skill_graph_db và trả về đúng các interface trong `src/types/catalog.ts`.
 *
 * CÁCH DÙNG — CHỈ SỬA 1 DÒNG TRONG FILE GỐC
 * ========================================
 * Trong `src/repositories/catalogRepository.ts`, thêm 1 import và đổi 1 chỗ:
 *
 *     import{HttpCatalogRepositoryApi}from'./catalogRepositoryApi';
 *     ...
 *     ? new HttpCatalogRepositoryApi()      // thay cho new HttpCatalogRepository()
 *     : new LocalCatalogRepository()
 *
 * Rồi tạo file `.env.local` ở thư mục gốc frontend:
 *
 *     VITE_DATA_SOURCE=api
 *     VITE_API_BASE_URL=http://127.0.0.1:8000/compat
 *
 * VÌ SAO CÓ `/compat` TRONG URL
 * ============================
 * Backend chính trả `/api/v1/careers` dạng `{items, total}`, còn giao diện
 * này cần mảng `Career[]`. Lớp tương thích nằm dưới `/compat/api/v1` để hai
 * hình dạng không giẫm lên nhau. Đổi lại: backend cũ giữ nguyên 100%.
 *
 * VÌ SAO DÙNG XMLHttpRequest ĐỒNG BỘ
 * ==================================
 * Interface `CatalogRepository` khai báo các getter trả về ĐỒNG BỘ (`Career[]`,
 * không phải `Promise<Career[]>`), trong khi gọi HTTP thì bất đồng bộ. Mà
 * `App.tsx` gọi `const repo = getCatalogRepository()` ngay ở cấp module rồi
 * render luôn — nếu để bất đồng bộ, khung hình đầu tiên sẽ thấy mảng rỗng và
 * giao diện trắng, không tự vẽ lại.
 *
 * Vì mục tiêu là "không sửa frontend", file này nạp dữ liệu bằng XHR đồng bộ
 * một lần rồi cache lại. Đánh đổi: khung hình đầu chậm hơn khoảng 100–300 ms.
 * Nếu được phép sửa thêm `main.tsx` thì nên nạp trước bằng `await ready()`
 * rồi mới `createRoot(...)` — sạch hơn về mặt kiến trúc.
 *
 * GIỚI HẠN CỦA BỘ DỮ LIỆU skill_graph_db
 * ======================================
 * Không có `skill_groups`, `esco_*`, `reports`. Các method liên quan trả về
 * rỗng RÕ RÀNG thay vì bịa dữ liệu. Giao diện sẽ hiện "không có dữ liệu" ở
 * những chỗ đó — đó là phản ánh trung thực, không phải lỗi.
 */

import type {
  CatalogPayload,
  Career,
  Course,
  Edge,
  Evidence,
  GraphData,
  Provider,
  Raw,
  Requirement,
  Skill,
  SkillGroup,
} from '../types/catalog';

import type { CatalogRepository } from './catalogRepository';

// ---------------------------------------------------------------------------
// Cấu hình
// ---------------------------------------------------------------------------
const RAW_BASE: string =
  (import.meta as any).env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000/compat';

const BASE = String(RAW_BASE).replace(/\/+$/, '');
const API = `${BASE}/api/v1`;

// ---------------------------------------------------------------------------
// Nạp dữ liệu
// ---------------------------------------------------------------------------
/** Nạp đồng bộ — dùng cho lần render đầu tiên. */
function getSync<T>(path: string): T {
  const xhr = new XMLHttpRequest();
  xhr.open('GET', `${API}${path}`, false); // false = đồng bộ
  xhr.setRequestHeader('Accept', 'application/json');
  xhr.send(null);
  if (xhr.status < 200 || xhr.status >= 300) {
    let detail = '';
    try {
      detail = JSON.parse(xhr.responseText)?.error?.message ?? '';
    } catch {
      /* bỏ qua */
    }
    throw new Error(`API ${xhr.status} ${path}${detail ? ` — ${detail}` : ''}`);
  }
  return JSON.parse(xhr.responseText) as T;
}

/** Bọc lỗi để một endpoint hỏng không làm sập cả giao diện. */
function safeSync<T>(path: string, fallback: T): T {
  try {
    return getSync<T>(path);
  } catch (err) {
    console.warn(`[HttpCatalogRepositoryApi] ${path} lỗi:`, err);
    return fallback;
  }
}

// ---------------------------------------------------------------------------
// Chuẩn hoá
// ---------------------------------------------------------------------------
function toId(kind: string, value: string): string {
  const text = String(value ?? '');
  return text.includes('/') ? text : `${kind}/${text}`;
}

function toKey(value: string): string {
  const text = String(value ?? '');
  return text.includes('/') ? text.split('/').slice(1).join('/') : text;
}

function withRaw(obj: any, fallbackKey: string): Raw {
  const raw = (obj?.raw && typeof obj.raw === 'object' ? obj.raw : obj) ?? {};
  return { ...raw, _key: String(raw._key ?? obj?.key ?? fallbackKey) } as Raw;
}

function asCareer(x: any): Career {
  const key = String(x?.key ?? toKey(x?.id ?? ''));
  return {
    key,
    id: x?.id ? String(x.id) : `careers/${key}`,
    name: String(x?.name ?? ''),
    description: String(x?.description ?? ''),
    careerGroup: String(x?.careerGroup ?? ''),
    iscoGroup: String(x?.iscoGroup ?? ''),
    escoUri: String(x?.escoUri ?? ''),
  };
}

function asSkill(x: any): Skill {
  const key = String(x?.key ?? toKey(x?.id ?? ''));
  return {
    key,
    id: x?.id ? String(x.id) : `skills/${key}`,
    name: String(x?.name ?? ''),
    description: String(x?.description ?? ''),
    skillType: String(x?.skillType ?? ''),
    escoUri: String(x?.escoUri ?? ''),
    reuseLevel: x?.reuseLevel != null ? String(x.reuseLevel) : null,
  };
}

function asCourse(x: any): Course {
  const key = String(x?.key ?? toKey(x?.id ?? ''));
  return {
    key,
    id: x?.id ? String(x.id) : `courses/${key}`,
    title: String(x?.title ?? ''),
    canonicalUrl: String(x?.canonicalUrl ?? ''),
    providerName: String(x?.providerName ?? ''),
    resourceType: String(x?.resourceType ?? 'course'),
    language: String(x?.language ?? 'en'),
    level: x?.level != null ? String(x.level) : null,
    certificateAvailable:
      typeof x?.certificateAvailable === 'boolean'
        ? x.certificateAvailable
        : null,
    verifiedOutcomeProficiency:
      x?.verifiedOutcomeProficiency != null
        ? String(x.verifiedOutcomeProficiency)
        : null,
    raw: withRaw(x, key),
  };
}

function asProvider(x: any): Provider {
  const key = String(x?.key ?? toKey(x?.id ?? ''));
  return {
    key,
    id: x?.id ? String(x.id) : `providers/${key}`,
    name: String(x?.name ?? ''),
    officialWebsite:
      x?.officialWebsite != null ? String(x.officialWebsite) : null,
  };
}

function asEdge(x: any): Edge {
  return {
    key: String(x?.key ?? x?.id ?? ''),
    id: String(x?.id ?? x?.key ?? ''),
    from: String(x?.from ?? ''),
    to: String(x?.to ?? ''),
    raw: withRaw(x, String(x?.key ?? '')),
  };
}

function asEvidence(x: any): Evidence {
  return {
    edge: asEdge(x?.edge ?? {}),
    evidenceScope: x?.evidenceScope === 'partial' ? 'partial' : 'direct_topic',
    evidenceLimit: x?.evidenceLimit != null ? String(x.evidenceLimit) : null,
  };
}

// ---------------------------------------------------------------------------
// Lớp chính
// ---------------------------------------------------------------------------
export class HttpCatalogRepositoryApi implements CatalogRepository {
  private release: CatalogPayload['release'] = {
    version: 'skill_graph_db',
    sprint: 0,
    records: 0,
  };
  private careers: Career[] = [];
  private skills: Skill[] = [];
  private courses: Course[] = [];
  private providers: Provider[] = [];
  private coverage: Array<{
    career: string;
    essential: number;
    covered: number;
    missing: number;
    pct: number;
  }> = [];

  private careerMap = new Map<string, Career>();
  private skillMap = new Map<string, Skill>();
  private courseMap = new Map<string, Course>();

  private careerReq = new Map<string, Requirement[]>();
  private skillRes = new Map<
    string,
    Array<{ course: Course; evidence: Evidence[] }>
  >();
  private courseSkills = new Map<
    string,
    Array<{ skill: Skill; evidence: Evidence[] }>
  >();
  private byProvider = new Map<string, Course[]>();
  private graphCache = new Map<string, GraphData>();
  private careerOfSkill = new Map<
    string,
    Array<{ career: Career; type: string }>
  >();
  private allRequirementsLoaded = false;

  constructor() {
    // Nạp ngay trong constructor bằng XHR đồng bộ: khi App.tsx render lần đầu,
    // cache đã có sẵn dữ liệu nên giao diện không bị trắng.
    this.preload();
  }

  /** Nạp toàn bộ dữ liệu nền. Chạy đúng một lần. */
  preload(): void {
    const release = safeSync<any>('/meta/release', null);
    if (release) {
      this.release = {
        version: String(release?.version ?? 'skill_graph_db'),
        sprint: Number(release?.sprint ?? 0),
        records: Number(release?.records ?? 0),
      };
    }

    this.careers = safeSync<any[]>('/careers', []).map(asCareer);
    this.skills = safeSync<any[]>('/skills', []).map(asSkill);
    this.courses = safeSync<any[]>('/resources', []).map(asCourse);
    this.providers = safeSync<any[]>('/providers', []).map(asProvider);

    for (const c of this.careers) this.careerMap.set(c.id, c);
    for (const s of this.skills) this.skillMap.set(s.id, s);
    for (const c of this.courses) this.courseMap.set(c.id, c);

    const cov = safeSync<any>('/statistics/coverage', { items: [] });
    this.coverage = (cov?.items ?? []).map((r: any) => ({
      career: String(r?.career ?? ''),
      essential: Number(r?.essential ?? 0),
      covered: Number(r?.covered ?? 0),
      missing: Number(r?.missing ?? 0),
      pct: Number(r?.pct ?? 0),
    }));
  }

  /** Giữ tương thích nếu nơi khác muốn await. Đã nạp sẵn ở constructor. */
  async ready(): Promise<void> {
    /* không cần làm gì — đã nạp đồng bộ */
  }

  // -- release / raw ----------------------------------------------------
  getReleaseInfo(): CatalogPayload['release'] {
    return this.release;
  }

  /**
   * Payload thô cho trang Thống kê.
   *
   * QUAN TRỌNG: `StatisticsDashboard.tsx` đọc thẳng
   * `p.collections[name].length` cho 7 tên collection (trong đó có 4 collection
   * ESCO). Nếu một key không tồn tại, `.length` sẽ ném
   * "Cannot read properties of undefined" và cả trang trắng.
   * Vì vậy phải LUÔN trả đủ key — collection không có trong skill_graph_db thì
   * trả mảng rỗng, đúng với sự thật dữ liệu.
   */
  getRaw(): CatalogPayload {
    return {
      release: this.release,
      handoff: {
        project: 'Skill Graph and personalized learning with ArangoDB',
        data_source: 'skill_graph_db',
        note: 'Xem /compat/api/v1/meta/release để biết chi tiết.',
      },
      manifest: {
        version: this.release.version,
        records: this.release.records,
        // Ba trường dưới đây được StatisticsDashboard.tsx đọc trực tiếp.
        // Tính từ dữ liệu thật: essential_total = tổng kỹ năng bắt buộc của
        // mọi nghề; essential_direct = số kỹ năng đó có ít nhất 1 khoá dạy.
        essential_total: this.coverage.reduce((s, r) => s + r.essential, 0),
        essential_direct: this.coverage.reduce((s, r) => s + r.covered, 0),
        essential_missing: this.coverage.reduce((s, r) => s + r.missing, 0),
        note:
          'skill_graph_db không có manifest ESCO; các collection esco_* và ' +
          'skill_groups không tồn tại nên được trả về mảng rỗng.',
      } as any,
      collections: {
        // Có trong skill_graph_db
        careers: this.careers as any,
        skills: this.skills as any,
        courses: this.courses as any,
        providers: this.providers as any,
        // Có cạnh nhưng không phơi ra dạng mảng thô (đã tổng hợp ở nơi khác)
        requires_skill: this.getRemainingEssentialGaps().slice(1) as any,
        teaches: [] as any,
        offered_by: [] as any,
        // KHÔNG có trong skill_graph_db — trả mảng rỗng để UI không sập
        esco_skill_group: [] as any,
        esco_skill_broader: [] as any,
        esco_group_broader: [] as any,
        esco_skill_knowledge: [] as any,
        skill_groups: [] as any,
      },
      reports: { coverage: '', gaps: '', legacyAudit: '' },
    };
  }

  // -- careers ----------------------------------------------------------
  getCareers(): Career[] {
    return this.careers;
  }

  getCareerById(v: string): Career | undefined {
    return this.careerMap.get(toId('careers', v));
  }

  getCareerRequirements(v: string): Requirement[] {
    const cid = toId('careers', v);
    const cached = this.careerReq.get(cid);
    if (cached) return cached;
    const body = safeSync<any>(
      `/careers/${encodeURIComponent(toKey(cid))}/skills`,
      { items: [] }
    );
    const rows: Requirement[] = (body?.items ?? []).map((x: any) => ({
      ...asEdge(x),
      requirementType:
        x?.requirementType === 'essential' ? 'essential' : 'optional',
      requiredLevel: null,
      skill: asSkill(x?.skill ?? {}),
      resourceCount: Number(x?.resourceCount ?? 0),
    }));
    rows.sort((a, b) => {
      const ea = a.requirementType === 'essential' ? 0 : 1;
      const eb = b.requirementType === 'essential' ? 0 : 1;
      return ea - eb || a.skill.name.localeCompare(b.skill.name);
    });
    this.careerReq.set(cid, rows);
    return rows;
  }

  // -- skills -----------------------------------------------------------
  getSkills(): Skill[] {
    return this.skills;
  }

  getSkillById(v: string): Skill | undefined {
    return this.skillMap.get(toId('skills', v));
  }

  /** skill_graph_db không có collection skill_groups. */
  getSkillGroups(): SkillGroup[] {
    return [];
  }

  getSkillsInGroup(_v: string): Skill[] {
    return [];
  }

  // -- courses ----------------------------------------------------------
  getCourses(): Course[] {
    return this.courses;
  }

  getCourseById(v: string): Course | undefined {
    return this.courseMap.get(toId('courses', v));
  }

  getProviders(): Provider[] {
    return this.providers;
  }

  getCoursesByProvider(v: string): Course[] {
    const pid = toId('providers', v);
    const cached = this.byProvider.get(pid);
    if (cached) return cached;
    const body = safeSync<any>(
      `/providers/${encodeURIComponent(toKey(pid))}/resources`,
      { items: [] }
    );
    const rows = (body?.items ?? []).map(asCourse);
    this.byProvider.set(pid, rows);
    for (const c of rows) this.courseMap.set(c.id, c);
    return rows;
  }

  getCoursesForSkill(
    v: string
  ): Array<{ course: Course; evidence: Evidence[] }> {
    const sid = toId('skills', v);
    const cached = this.skillRes.get(sid);
    if (cached) return cached;
    const body = safeSync<any>(
      `/skills/${encodeURIComponent(toKey(sid))}/resources`,
      { items: [] }
    );
    const rows = (body?.items ?? []).map((x: any) => ({
      course: asCourse(x?.course ?? {}),
      evidence: (x?.evidence ?? []).map(asEvidence),
    }));
    this.skillRes.set(sid, rows);
    for (const r of rows) this.courseMap.set(r.course.id, r.course);
    return rows;
  }

  getSkillsForCourse(v: string): Array<{ skill: Skill; evidence: Evidence[] }> {
    const rid = toId('courses', v);
    const cached = this.courseSkills.get(rid);
    if (cached) return cached;
    const body = safeSync<any>(
      `/resources/${encodeURIComponent(toKey(rid))}/skills`,
      { items: [] }
    );
    const rows = (body?.items ?? []).map((x: any) => ({
      skill: asSkill(x?.skill ?? {}),
      evidence: (x?.evidence ?? []).map(asEvidence),
    }));
    this.courseSkills.set(rid, rows);
    for (const r of rows) this.skillMap.set(r.skill.id, r.skill);
    return rows;
  }

  /**
   * Nghề nào yêu cầu kỹ năng này. Không có endpoint riêng, nên duyệt toàn bộ
   * nghề một lần rồi cache (29 nghề × 1 request, chạy 1 lần duy nhất).
   */
  getCareersForSkill(v: string): Array<{ career: Career; type: string }> {
    if (!this.allRequirementsLoaded) {
      for (const c of this.careers) this.getCareerRequirements(c.id);
      for (const [cid, reqs] of this.careerReq) {
        const career = this.careerMap.get(cid);
        if (!career) continue;
        for (const r of reqs) {
          const list = this.careerOfSkill.get(r.skill.id) ?? [];
          list.push({ career, type: r.requirementType });
          this.careerOfSkill.set(r.skill.id, list);
        }
      }
      this.allRequirementsLoaded = true;
    }
    return this.careerOfSkill.get(toId('skills', v)) ?? [];
  }

  // -- báo cáo ----------------------------------------------------------
  getCoverageReport(): Array<{
    career: string;
    essential: number;
    covered: number;
    missing: number;
    pct: number;
  }> {
    return this.coverage;
  }

  getRemainingEssentialGaps(): string[][] {
    return [
      ['career', 'essential', 'covered', 'missing', 'pct'],
      ...this.coverage.map((r) => [
        r.career,
        String(r.essential),
        String(r.covered),
        String(r.missing),
        String(r.pct),
      ]),
    ];
  }

  // -- đồ thị -----------------------------------------------------------
  private graph(focusId: string, mode: string): GraphData {
    const key = focusId;
    const cached = this.graphCache.get(key);
    if (cached) return cached;
    const body = safeSync<any>(
      `/graph/neighborhood?focusId=${encodeURIComponent(
        focusId
      )}&mode=${mode}&limit=120`,
      { nodes: [], edges: [] }
    );
    const g: GraphData = {
      nodes: (body?.nodes ?? []).map((n: any) => ({
        id: String(n?.id ?? ''),
        type: String(n?.type ?? ''),
        label: String(n?.label ?? ''),
      })),
      edges: (body?.edges ?? []).map((e: any) => ({
        id: String(e?.id ?? ''),
        source: String(e?.source ?? ''),
        target: String(e?.target ?? ''),
        type: String(e?.type ?? ''),
        data: e?.data,
      })),
    };
    this.graphCache.set(key, g);
    return g;
  }

  getGraphForCareer(v: string): GraphData {
    return this.graph(toId('careers', v), 'career');
  }

  getGraphForSkill(v: string): GraphData {
    return this.graph(toId('skills', v), 'skill');
  }

  getGraphForCourse(v: string): GraphData {
    return this.graph(toId('courses', v), 'course');
  }

  /** Phân loại ESCO không có trong skill_graph_db — trả rỗng, không bịa. */
  getTaxonomyGraph(_v: string): GraphData {
    return { nodes: [], edges: [] };
  }
}

export default HttpCatalogRepositoryApi;
