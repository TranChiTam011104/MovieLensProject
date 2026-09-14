# MovieLens Recommendation API - Use Cases

## 📋 Tổng quan

API cung cấp các endpoint dựa trên **SVD (Singular Value Decomposition)** để gợi ý phim cho người dùng MovieLens 100K dataset.

---

## 🎯 ML-Based Endpoints

### 1. `GET /v1/recommend/users/{user_id}`

**Mục đích:** Gợi ý phim cá nhân hóa cho 1 user

**Use cases:**
- Trang chủ app → "Phim dành cho bạn hôm nay"
- Push notification → "Mình nghĩ bạn sẽ thích phim này!"
- User mới đăng nhập → Landing page với gợi ý phim

**Parameters:**
| Parameter | Type | Default | Mô tả |
|-----------|------|---------|-------|
| `n` | int | 10 | Số lượng gợi ý |
| `exclude_watched` | bool | true | Loại bỏ phim đã xem |
| `min_rating` | float | 0 | Ngưỡng rating tối thiểu |

**Output mẫu:**
```json
{
  "user_id": 42,
  "n_recommendations": 10,
  "recommendations": [
    {"movie_id": 318, "title": "Shawshank Redemption", "predicted_rating": 4.82}
  ]
}
```

---

### 2. `GET /v1/predict/users/{user_id}/movies/{movie_id}`

**Mục đích:** Dự đoán rating cho 1 user - 1 phim cụ thể

**Use cases:**
- Trang chi tiết phim → "Dự đoán bạn sẽ cho 4.5 sao"
- Decision engine → "Có nên hiển thị phim này cho user?"
- A/B testing → So sánh predicted vs actual rating

**Parameters:**
| Parameter | Type | Mô tả |
|-----------|------|-------|
| `user_id` | int | User ID (1-943) |
| `movie_id` | int | Movie ID (1-1682) |

**Output mẫu:**
```json
{
  "user_id": 42,
  "movie_id": 318,
  "predicted_rating": 4.82,
  "confidence": 0.95,
  "actual_rating": null
}
```

---

### 3. `GET /v1/movies/{movie_id}/similar` ⭐ NEW

**Mục đích:** Tìm phim tương tự dựa trên **Item-based Collaborative Filtering**

**Use cases:**
- Trang chi tiết phim → "Phim tương tự bạn có thể thích"
- Section "Xem thêm như phim này"
- Cross-selling → "Khách xem Shawshank cũng thích..."
- Genre expansion → Gợi ý phim cùng "hương vị"

**Parameters:**
| Parameter | Type | Default | Mô tả |
|-----------|------|---------|-------|
| `n` | int | 10 | Số phim tương tự |
| `min_similarity` | float | 0 | Ngưỡng similarity (0-1) |

**Output mẫu:**
```json
{
  "movie_id": 318,
  "title": "Shawshank Redemption",
  "similar_movies": [
    {"movie_id": 279, "title": "Green Mile", "similarity_score": 0.92}
  ]
}
```

**ML Logic:**
```
movie_vector = SVD.movie_factors[movie_id]
similarity = cosine_similarity(movie_vector, all_other_movies)
return top-N by similarity
```

---

### 4. `GET /v1/users/{user_id}/similar` ⭐ NEW

**Mục đích:** Tìm users có sở thích tương tự dựa trên **User-based Collaborative Filtering**

**Use cases:**
- Admin dashboard → Phân tích user segments/clusters
- Community insights → "Bạn có sở thích giống 89% user khác"
- Social features → "Kết bạn với người cùng gu"
- Cold-start → Gợi ý dựa trên similar users
- Data analysis → Nghiên cứu behavior patterns

**Parameters:**
| Parameter | Type | Default | Mô tả |
|-----------|------|---------|-------|
| `n` | int | 10 | Số users tương tự |
| `min_similarity` | float | 0 | Ngưỡng similarity (0-1) |

**Output mẫu:**
```json
{
  "user_id": 42,
  "similar_users": [
    {"user_id": 156, "similarity_score": 0.89, "common_ratings": 145}
  ]
}
```

**ML Logic:**
```
user_vector = SVD.user_factors[user_id]
similarity = cosine_similarity(user_vector, all_other_users)
return top-N by similarity
```

---

## 📦 Non-ML Endpoints

### 5. `GET /v1/movies/{movie_id}`

**Mục đích:** Lấy thông tin chi tiết 1 phim (từ database)

**Use cases:**
- Hiển thị trang chi tiết phim
- Populate movie info cho UI
- Metadata lookup

**Output mẫu:**
```json
{
  "movie_id": 318,
  "title": "Shawshank Redemption, The (1994)",
  "genres": ["Crime", "Drama"],
  "release_year": 1994,
  "avg_rating": 4.53,
  "n_ratings": 452
}
```

---

### 6. `GET /health`

**Mục đích:** Health check cho monitoring/deployment

**Use cases:**
- Kubernetes/Load balancer health check
- CI/CD deployment verification
- Uptime monitoring

---

## 🔗 Cách kết hợp các endpoints

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  USER FLOWS THƯỜNG DÙNG:                                                  │
│                                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  🎬 TRANG CHI TIẾT PHIM                                                    │
│     ├── /v1/movies/{id}          → Thông tin phim                          │
│     ├── /v1/movies/{id}/similar  → "Phim tương tự"                         │
│     ├── /v1/predict/users/{uid}/movies/{mid} → "Bạn sẽ thích bao nhiêu?"               │
│                                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  🏠 TRANG CHỦ / DASHBOARD                                                  │
│     ├── /v1/recommend/users/{uid}  → "Phim dành cho bạn"                       │
│     └── /v1/users/{uid}/similar → "Users cùng gu với bạn"                 │
│                                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  📧 EMAIL MARKETING (batch - future)                                      │
│     └── /v1/recommend/batch     → Gửi hàng loạt recommendations          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Quick Reference

| Endpoint | Method | ML Model | Main Use Case |
|----------|--------|----------|---------------|
| `/v1/recommend/users/{user_id}` | GET | SVD | Personalized recommendations |
| `/v1/predict/users/{uid}/movies/{mid}` | GET | SVD | Single rating prediction |
| `/v1/movies/{mid}/similar` | GET | SVD (Item CF) | "You might also like..." |
| `/v1/users/{uid}/similar` | GET | SVD (User CF) | User segmentation |
| `/v1/movies/{mid}` | GET | None | Movie metadata |
| `/health` | GET | None | Health check |
