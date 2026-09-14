"""Test script for API endpoints."""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Initialize services before TestClient (TestClient doesn't trigger lifespan)
print("Initializing services...")

from src.api.services.recommendation_engine import load_engine
import src.api.services.similarity_service as sim_module
from src.api.services.similarity_service import get_similarity_service
from src.data.load import load_ratings, load_movies
from src.data.preprocess import process_movies, add_rating_stats
from surprise import Dataset, Reader

# Clear existing singletons
sim_module._similarity_service = None

# Load main model
print("Loading SVD model...")
load_engine()

# Initialize similarity service
ratings_df = load_ratings()
movies_df = load_movies()
processed_movies = process_movies(movies_df)
processed_movies = add_rating_stats(processed_movies, ratings_df)

reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df[['user_id', 'item_id', 'rating']], reader)
trainset = data.build_full_trainset()

sim_module._similarity_service = get_similarity_service()
sim_module._similarity_service._ratings_df = ratings_df
sim_module._similarity_service._movies_df = processed_movies
sim_module._similarity_service._trainset = trainset

from src.api.services.recommendation_engine import get_engine
engine = get_engine()
sim_module._similarity_service.model = engine.model
sim_module._similarity_service._extract_latent_factors()
sim_module._similarity_service._is_loaded = True

# Import app and set movies cache
from src.api.main import app
from src.api.routers import movies as movies_module
movies_module._movies_cache = {
    row['movie_id']: row.to_dict()
    for _, row in processed_movies.iterrows()
}

from fastapi.testclient import TestClient
client = TestClient(app)

print("=" * 60)
print("🧪 Testing MovieLens Recommendation API")
print("=" * 60)

# Test health
print("\n1. Testing /health...")
r = client.get("/health")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")

# Test root
print("\n2. Testing /...")
r = client.get("/")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")

# Test recommendations
print("\n3. Testing /v1/recommend/42...")
r = client.get("/v1/recommend/42?n=5")
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   User ID: {data.get('user_id')}")
    print(f"   Recommendations: {data.get('n_recommendations')}")
    for rec in data.get('recommendations', [])[:3]:
        print(f"   - {rec['movie_id']}: {rec['title']} (pred: {rec['predicted_rating']})")
else:
    print(f"   Error: {r.json()}")

# Test similar movies
print("\n4. Testing /v1/movies/318/similar...")
r = client.get("/v1/movies/318/similar?n=5")
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   Movie ID: {data.get('movie_id')}")
    print(f"   Similar: {data.get('n_similar')}")
    for sim in data.get('similar_movies', [])[:3]:
        print(f"   - {sim['movie_id']}: {sim.get('title', 'N/A')} (sim: {sim['similarity_score']:.4f})")

# Test similar users
print("\n5. Testing /v1/users/42/similar...")
r = client.get("/v1/users/42/similar?n=5")
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   User ID: {data.get('user_id')}")
    print(f"   Similar users: {data.get('n_similar')}")
    for sim in data.get('similar_users', [])[:3]:
        print(f"   - User {sim['user_id']} (sim: {sim['similarity_score']:.4f}, common: {sim['common_ratings']})")

# Test prediction
print("\n6. Testing /v1/predict/42/318...")
r = client.get("/v1/predict/42/318")
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   User: {data['user_id']}, Movie: {data['movie_id']}")
    print(f"   Predicted rating: {data['predicted_rating']}")
    print(f"   Confidence: {data['confidence']}")

print("\n" + "=" * 60)
print("✅ All tests completed successfully!")
print("=" * 60)
