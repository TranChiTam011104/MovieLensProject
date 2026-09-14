# Postman Collections for MovieLens API

## 📁 Files Created

| File | Description |
|------|-------------|
| `movielens-api.postman_collection.json` | API endpoints collection với test cases |
| `movielens-api.postman_environment.json` | Environment variables |

---

## 🚀 Cách Import vào Postman

### 1. Import Collection
1. Mở Postman
2. Click **Import** (nút ở góc trái trên)
3. Kéo thả file `movielens-api.postman_collection.json` hoặc browse file
4. Click **Import**

### 2. Import Environment
1. Click **Environments** (biểu tượng bánh răng ⚙️ ở góc phải trên)
2. Click **Import**
3. Kéo thả file `movielens-api.postman_environment.json`
4. Click **Import**

### 3. Chọn Environment
1. Click dropdown environment ở góc phải trên
2. Chọn **"MovieLens API - Local"**

---

## 📋 Collection Structure

```
📁 MovieLens Recommendation API
├── 📁 1. Health & Info
│   ├── Health Check
│   └── Root Info
│
├── 📁 2. Personalized Recommendations
│   ├── Get Recommendations - Default Params
│   ├── Get Recommendations - Custom N (Top 5)
│   ├── Get Recommendations - Include Watched
│   ├── Get Recommendations - With Min Rating Filter
│   ├── Get Recommendations - Different Users
│   ├── Get Recommendations - Max N (50)
│   ├── Get Recommendations - Invalid User (404)
│   ├── Get Recommendations - Invalid User (0)
│   └── Get Recommendations - N exceeds limit (422)
│
├── 📁 3. Rating Prediction
│   ├── Predict Rating - Normal Case
│   ├── Predict Rating - User 1 and Movie 1
│   ├── Predict Rating - Invalid User (404)
│   ├── Predict Rating - User 0 (422)
│   └── Predict Rating - Movie 0 (422)
│
├── 📁 4. Similar Movies (Item-based CF)
│   ├── Similar Movies - Shawshank Redemption (318)
│   ├── Similar Movies - Top 5
│   ├── Similar Movies - High Similarity Threshold
│   ├── Similar Movies - Different Movie (Toy Story)
│   └── Similar Movies - Invalid Movie (9999)
│
├── 📁 5. Similar Users (User-based CF)
│   ├── Similar Users - User 42
│   ├── Similar Users - Top 5
│   ├── Similar Users - High Similarity Threshold
│   ├── Similar Users - User 1
│   ├── Similar Users - Invalid User (404)
│   └── Similar Users - User 0 (422)
│
├── 📁 6. Movie Information
│   ├── Get Movie Details - Shawshank (318)
│   ├── Get Movie Details - Toy Story (1)
│   ├── Get Movie Details - Invalid (404)
│   ├── List Movies - Default (20)
│   ├── List Movies - Custom Limit (10)
│   ├── List Movies - With Pagination
│   └── List Movies - Limit 100 (Max)
│
└── 📁 7. Integration Tests (Chaining)
    ├── Full User Journey: Recommend → Details → Similar
    └── Compare Predictions for Different Users
```

---

## 🔧 Sử dụng với Docker/Podman

### 1. Chạy API với Podman

```bash
# Build image
podman build -t movielens-api .

# Run container
podman run -d --name movielens-api \
  -p 8000:8000 \
  movielens-api

# Kiểm tra API đang chạy
curl http://localhost:8000/health
```

### 2. Hoặc chạy với Docker Compose

```bash
# Khởi động services
docker compose up -d

# Xem logs
docker compose logs -f api
```

### 3. Test trên Postman

1. Đảm bảo API đang chạy trên `http://localhost:8000`
2. Run collection hoặc từng request trong Postman

---

## ✅ Test Scenarios Covered

| Scenario | Description |
|----------|-------------|
| **Happy Path** | Valid requests với params mặc định |
| **Edge Cases** | N=0, N=1, N=50 (max) |
| **Validation Errors** | user_id=0, movie_id=0, N=100 |
| **Not Found** | user_id=9999, movie_id=9999 |
| **Pagination** | offset, limit params |
| **Filtering** | min_rating, min_similarity |
| **Integration** | Chaining multiple endpoints |

---

## 📊 Test Results

Mỗi request đều có **automated tests** kiểm tra:

```javascript
// Ví dụ test cho recommendations:
pm.test('Status code is 200', function() {
    pm.response.to.have.status(200);
});

pm.test('Returns recommendations array', function() {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('recommendations');
});

pm.test('Predicted ratings are valid (1-5)', function() {
    var jsonData = pm.response.json();
    jsonData.recommendations.forEach(function(rec) {
        pm.expect(rec.predicted_rating).to.be.within(1, 5);
    });
});
```

---

## 🔗 Quick Test Commands (curl)

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Personalized Recommendations (User-based)
```bash
# Gợi ý phim cho user 42
# → /v1/recommend/users/{user_id}
curl "http://localhost:8000/v1/recommend/users/42"

# Gợi ý 5 phim cho user 42, không bao gồm phim đã xem
curl "http://localhost:8000/v1/recommend/users/42?n=5&exclude_watched=true"

# Gợi ý phim cho user 42, chỉ phim có predicted rating >= 4.0
curl "http://localhost:8000/v1/recommend/users/42?min_rating=4.0"
```

### 3. Rating Prediction
```bash
# Dự đoán user 42 sẽ cho movie 318 (The Shawshank Redemption) bao nhiêu sao
# → /v1/predict/users/{user_id}/movies/{movie_id}
curl "http://localhost:8000/v1/predict/users/42/movies/318"

# Dự đoán user 1 sẽ cho movie 1 (Toy Story) bao nhiêu sao
curl "http://localhost:8000/v1/predict/users/1/movies/1"
```

### 4. Similar Movies (Item-based CF)
```bash
# Tìm phim tương tự movie 318 (The Shawshank Redemption)
# → /v1/movies/{movie_id}/similar
curl "http://localhost:8000/v1/movies/318/similar"

# Tìm 5 phim tương tự movie 318, chỉ similar >= 0.8
curl "http://localhost:8000/v1/movies/318/similar?n=5&min_similarity=0.8"

# Tìm phim tương tự movie 1 (Toy Story)
curl "http://localhost:8000/v1/movies/1/similar"
```

### 5. Similar Users (User-based CF)
```bash
# Tìm users có sở thích giống user 42
# → /v1/users/{user_id}/similar
curl "http://localhost:8000/v1/users/42/similar"

# Tìm 5 users tương tự user 42
curl "http://localhost:8000/v1/users/42/similar?n=5"

# Tìm users có similarity >= 0.7 với user 42
curl "http://localhost:8000/v1/users/42/similar?min_similarity=0.7"
```

### 6. Movie Information
```bash
# Lấy thông tin chi tiết của movie 318
# → /v1/movies/{movie_id}
curl "http://localhost:8000/v1/movies/318"

# Danh sách 20 phim đầu tiên
curl "http://localhost:8000/v1/movies"

# Danh sách 10 phim, bắt đầu từ vị trí 20
curl "http://localhost:8000/v1/movies?limit=10&offset=20"
```

---

## 📖 Tổng hợp ý nghĩa các endpoint

| Endpoint | Ý nghĩa |
|----------|---------|
| `/v1/recommend/users/{user_id}` | Gợi ý phim cho **user_id** |
| `/v1/predict/users/{user_id}/movies/{movie_id}` | Dự đoán rating của **user_id** cho **movie_id** |
| `/v1/movies/{movie_id}/similar` | Tìm phim tương tự **movie_id** |
| `/v1/users/{user_id}/similar` | Tìm users giống **user_id** |
| `/v1/movies/{movie_id}` | Thông tin chi tiết **movie_id** |
| `/v1/movies` | Danh sách tất cả phim |
