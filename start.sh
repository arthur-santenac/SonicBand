cd "$(dirname "$0")"

source backend/venv/bin/activate
export DATABASE_URL=sqlite:///./db.sqlite3
python -m uvicorn backend.main:app --reload &
BACK_PID=$!
trap "kill $BACK_PID" EXIT

cd frontend/SonicBandFront
echo "Ouvrir http://localhost:8080"
npm run dev
