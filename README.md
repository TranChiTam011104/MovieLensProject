# TRACK MLE — MovieLens 100K

## Checkpoint 1 (Tuần 1-2): Model cơ bản (không optimize) + API Spec

**Mục tiêu:** Có model đơn giản chạy được, và API contract rõ ràng — ưu tiên tốc độ, không tối ưu accuracy.


| Tuần       | Task                                                                                                                                                                                                                                                          |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tuần 1** | - Setup repo, môi trường, terraform - Load MovieLens 100K, build model recommendation cơ bản collaborative filtering hoặc content-based đơn giản - Train nhanh, không cần tuning, chỉ cần chạy được và predict top-N cho user                                 |
| **Tuần 2** | - Định nghĩa API spec (OpenAPI/Swagger): endpoint `/recommend/{user_id}`, input/output schema, error handling, versioning trong URL (`/v1/recommend`) - Viết doc spec đầy đủ (request/response example, status code) - Review spec cùng mentor trước khi code |


**Tech dùng:** `surprise` / `implicit` / `lightfm`, FastAPI (để định nghĩa spec dễ tự sinh Swagger docs), OpenAPI

**Deliverable checkpoint 1:**

- Model baseline chạy predict được (không cần tối ưu)
- File OpenAPI spec (`.yaml`) hoàn chỉnh, review được
- Repo có cấu trúc rõ ràng (model/, api/, tests/)

---



## Checkpoint 2 (Tuần 3-4): Deploy Model + Versioning + Deploy Strategy

**Mục tiêu:** Model chạy như service thật trên AWS, có version control và hiểu 3 chiến lược deploy.


| Tuần       | Task                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tuần 3** | - Implement API theo spec đã định nghĩa bằng FastAPI - Đóng gói bằng Docker - Deploy lên AWS free tier: EC2 (t2.micro) hoặc Lambda + API Gateway (nếu model nhẹ) - Setup model versioning: MLflow Model Registry hoặc đơn giản là naming convention + S3 (model-v1, model-v2)                                                                                                                                                         |
| **Tuần 4** | - Học và mô phỏng 3 chiến lược deploy: - Shadow: traffic gửi đến cả model cũ + mới, chỉ log kết quả model mới, không trả về user - Canary: route % nhỏ traffic (vd 10%) sang model mới - Blue-green: 2 environment riêng, switch traffic toàn bộ khi model mới pass test - Implement được ít nhất 1 trong 3 (khuyến nghị Canary vì dễ mô phỏng với API Gateway/ALB weighted routing hoặc đơn giản là random routing logic trong code) |


**Tech dùng:** Docker, FastAPI, MLflow, AWS EC2/Lambda/API Gateway, GitLab CI/CD hoặc Github Actions cho CI/CD pipeline deploy.

**Deliverable checkpoint 2:**

- API đang chạy thật trên AWS, có thể gọi qua public/internal endpoint
- Có ít nhất 2 version model, quản lý qua registry
- Demo được 1 deploy strategy (canary/shadow/blue-green) hoạt động thực tế, kèm giải thích 3 chiến lược (điểm khác biệt, khi nào dùng)

---



## Checkpoint 3 (Tuần 5-6): Serving Strategy + Monitoring/Drift/Latency

**Mục tiêu:** Hiểu sync/async serving, và có hệ thống giám sát model trong production.


| Tuần       | Task                                                                                                                                                                                                                                                                                                                 |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tuần 5** | - So sánh Sync (request-response trực tiếp, dùng cho real-time recommend) vs Async (queue-based, dùng SQS + worker, phù hợp batch recommend hoặc heavy compute) - Implement thử 1 flow async đơn giản (request → SQS → lambda/worker xử lý → lưu kết quả → client poll hoặc callback) - Đo latency của cả 2 approach |
| **Tuần 6** | - Setup monitoring: log request/response, latency (p50/p95/p99), error rate - Setup drift detection cơ bản (so sánh distribution input features theo thời gian) - Dashboard: CloudWatch (AWS free tier) hoặc Grafana + Prometheus nếu tự host - Tổng kết + demo toàn bộ hệ thống                                     |


**Tech dùng:** AWS SQS, CloudWatch, Prometheus/Grafana (nếu muốn tự host, docker compose).

**Deliverable checkpoint 3 (cuối track):**

- So sánh sync vs async có số liệu latency thực tế
- Dashboard monitoring hiển thị latency + basic drift alert
- Demo end-to-end: từ request → model serving → log → monitor, kèm slide tổng kết toàn bộ 6 tuần (API spec → deploy → serving → monitoring)

