cd app

adk web --allow_origins http://localhost:8080

cd ..
cd frontend

python3 -m http.server 8080