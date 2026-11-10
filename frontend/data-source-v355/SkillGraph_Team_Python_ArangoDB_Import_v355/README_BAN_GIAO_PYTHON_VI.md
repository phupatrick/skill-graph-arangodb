# Bàn giao Skill Graph — Python + ArangoDB + Docker (v3.55 TEAM PREVIEW)

**Dành cho:** thành viên lập trình web Python, đã cài Docker và ArangoDB.  
**Trạng thái:** v3.55/Sprint 92, **đã xác minh OFFLINE**, **CHƯA có kết quả import LIVE trên máy thành viên**, **CHƯA DATA FREEZE**.  
**Mục đích:** chạy bản dữ liệu thật trên máy riêng để phát triển/kiểm tra web, **không ghi đè dữ liệu sẵn có**.

## A. Chuẩn bị

1. Giải nén ZIP thành thư mục bình thường, **không mở mã nguồn trực tiếp trong ZIP**.
2. Mở **PowerShell ngay tại thư mục chứa `CURRENT_RELEASE.json` và thư mục `tools`**.
3. Dùng Python 3.11+; các script trong gói chỉ dùng thư viện chuẩn, không cần `pip install` cho việc import.
4. Mở Docker Desktop và bảo đảm ArangoDB container đang chạy. Gõ `docker ps`; xác nhận cổng ArangoDB được công bố trên máy, ví dụ `0.0.0.0:8529->8529/tcp`.
5. Mở `http://127.0.0.1:8529` trong trình duyệt. Nếu ánh xạ cổng khác (ví dụ 8530:8529), dùng `--host http://127.0.0.1:8530` cho tất cả lệnh bên dưới. Dùng `https://` khi kết nối từ xa; không mở cổng DB ra Internet.

## B. Kiểm tra trước khi import — KHÔNG kết nối, KHÔNG ghi

```powershell
python tools\validate_release.py
python tools\prepare_arangodb.py --database skill_graph_team_preview_v355
```

Kỳ vọng: `PASS`, **24 collections**, **5.718 records**, SHA-256 hợp lệ.

## C. Import vào database MỚI (chỉ làm 1 lần)

```powershell
python tools\prepare_arangodb.py --apply --acknowledge-new-database --database skill_graph_team_preview_v355
```

- Script hỏi **mật khẩu ArangoDB cục bộ**, nhập trong PowerShell (ký tự không hiển thị). **KHÔNG gửi mật khẩu lên Zalo/GitHub**, không nhúng mật khẩu vào frontend.
- Script tạo **database mới** `skill_graph_team_preview_v355`, tạo 24 collections, import 5.718 bản ghi, đăng ký named graph `skill_graph`.
- **Nếu database đã tồn tại, script sẽ từ chối**, không xoá/không ghi đè. Nếu đã import rồi thì bỏ qua bước C và chuyển sang bước D. Nếu import dở dang, chọn tên database mới sau khi kiểm tra thủ công; không tự chạy lệnh xoá.
- Nếu cổng không phải 8529, thêm `--host http://127.0.0.1:<CONG>` và dùng thống nhất khi verify.

## D. Kiểm tra dữ liệu thật sau import

```powershell
python tools\verify_arangodb.py --database skill_graph_team_preview_v355
python examples\check_catalog_readonly.py --database skill_graph_team_preview_v355
```

Kỳ vọng `LIVE VERIFIED: 24 collections, 5718 records, named graph skill_graph` và `READ-ONLY CATALOG PASS`.

**Gửi lại cho nhóm:** toàn bộ đoạn kết quả từ lệnh validate, import và verify **nhưng xóa mật khẩu/token nếu vô tình xuất hiện**; ảnh `docker ps` có thể giúp kiểm tra ánh xạ cổng.

## E. Làm web Python

- Có thể dùng **Flask + HTML/CSS/JS**, hoặc framework Python khác nếu nhóm đã thống nhất.
- Python web **gọi ArangoDB ở tầng server/backend**; không để trình duyệt kết nối trực tiếp vào database và không đưa tài khoản `root` lên mã nguồn/public repo.
- `examples/check_catalog_readonly.py` minh họa truy vấn danh mục nghề và số học liệu bằng Python chuẩn. **Đây không phải backend/API production**.
- Ban đầu màn hình: danh sách nghề → yêu cầu kỹ năng → danh sách học liệu, hiển thị cảnh báo đây là **ứng viên theo chủ đề**, không tự nhận người học có kỹ năng hoặc đã được chấp nhận học liệu.
- Đừng lưu dữ liệu người dùng/đánh giá cá nhân bằng các tài khoản demo root. Khi triển khai ứng dụng, tạo tài khoản có **quyền tối thiểu** do quản trị viên cấu hình; không chia sẻ thông tin đăng nhập qua chat.
- Frontend handoff v0.2 đang chứa **mock snapshot v3.49**, có thể dùng để dựng UI nhưng khi hiển thị dữ liệu v3.55 phải lấy **database mới/endpoint Python** làm nguồn, tránh trộn hai phiên bản.

## F. Phạm vi và giới hạn trung thực

- 12 nghề, 420 kỹ năng, 504 học liệu/tài liệu, 179 nhà cung cấp.
- **323/343** yêu cầu Essential có ánh xạ `direct_topic` (**94,17% độ bao phủ chủ đề**); còn **20** yêu cầu chưa có học liệu trực tiếp.
- `direct_topic` là **liên quan về nội dung**, KHÔNG chứng minh mức độ thành thạo, đủ chương trình, quyền truy cập, giá tiền hay trình tự tiên quyết.
- **Không có học liệu được phê duyệt tự động đề xuất**; `prerequisite` có 0 cạnh. Không hiển thị thứ tự review như thứ tự học đã được kiểm chứng.
- 7 collections cố ý trống ở release (ví dụ `users`, `learning_plans`, `has_skill`...), dành cho phát triển ứng dụng sau này.
- 68 ánh xạ tài liệu tham khảo cũ cần kiểm duyệt sâu; 9 còn thiếu ghi chú giới hạn phạm vi (metadata audit). Các vấn đề này là **tồn đọng thật**, không được tự ý sửa bằng dữ liệu suy diễn.
- Dữ liệu đang được hoàn thiện song song. Khi chốt DATA FREEZE sẽ phát hành **database mới** hoặc quy trình nâng cấp được kiểm thử riêng; không ghi đè bản preview hiện tại.

## G. Xử lý lỗi thông dụng

| Hiện tượng | Cách xử lý |
|---|---|
| `ModuleNotFoundError` hoặc `FileNotFoundError` | Xác nhận PowerShell đang mở **đúng thư mục giải nén**, có `CURRENT_RELEASE.json` ở thư mục hiện tại. |
| `Connection refused` / `Cannot connect` | `docker ps`, kiểm tra container và cổng publish; thử truy cập UI ArangoDB. |
| `HTTP 401` | Sai tài khoản/mật khẩu ArangoDB; nhập lại **trên máy cá nhân**, không gửi password. |
| `HTTP 403` | Tài khoản không đủ quyền tạo database; dùng tài khoản quản trị cục bộ để import. |
| `REFUSED: database ... already exists` | Dữ liệu có thể đã nhập; chạy bước verify, **không import lại**. |
| `LIVE VERIFICATION FAILED` | Chụp/copy toàn bộ thông báo lỗi **không chứa mật khẩu**, kiểm tra database và host được truyền có khớp. |

## H. Các file quan trọng

- `release/vertices`, `release/edges`, `release/documents`: 24 JSONL thật.
- `CURRENT_RELEASE.json`, `MANIFEST_V355_SPRINT92.json`: version và checksum; `MANIFEST_V354_SPRINT91.json` để kiểm tra tính kế thừa.
- `tools/validate_release.py`, `tools/prepare_arangodb.py`, `tools/verify_arangodb.py`: kiểm tra và import an toàn.
- `examples/check_catalog_readonly.py`: ví dụ kết nối/đọc bằng Python.
- `reports/SPRINT92_REMAINING_ESSENTIAL_GAPS.csv`: danh sách 20 yêu cầu Essential còn thiếu.
- `reports/SPRINT92_LEGACY_68_FORMAT_METADATA_AUDIT.csv`: danh sách cần kiểm duyệt sâu.
