#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

COMPOSE_FILE="docker-compose.lia2.yml"
ENV_FILE=".env"

fail() {
  echo "[LIA2][ERRO] $1" >&2
  exit 1
}

requireCommand() {
  command -v "$1" >/dev/null 2>&1 || fail "Comando obrigatório não encontrado: $1"
}

containerIsRunning() {
  local containerName="$1"
  [ "$(docker inspect -f '{{.State.Running}}' "$containerName" 2>/dev/null || true)" = "true" ]
}

readContainerEnv() {
  local containerName="$1"
  local variableName="$2"

  docker inspect \
    --format '{{range .Config.Env}}{{println .}}{{end}}' \
    "$containerName" 2>/dev/null \
    | awk -F= -v key="$variableName" '$1 == key {sub(/^[^=]*=/, ""); print; exit}'
}

generateToken() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 32
  else
    head -c 48 /dev/urandom | base64 | tr -d '\n=/+' | head -c 64
  fi
}

getEnvValue() {
  local key="$1"
  if [ -f "$ENV_FILE" ]; then
    grep -E "^${key}=" "$ENV_FILE" | tail -n 1 | cut -d= -f2- || true
  fi
}

ensureEnvKey() {
  local key="$1"
  local value="$2"

  if ! grep -qE "^${key}=" "$ENV_FILE" 2>/dev/null; then
    printf '\n%s=%s\n' "$key" "$value" >> "$ENV_FILE"
  elif [ -z "$(getEnvValue "$key")" ]; then
    local tempFile
    tempFile="$(mktemp)"
    awk -v target="$key" -v replacement="$value" '
      BEGIN { FS=OFS="=" }
      $1 == target { print target, replacement; next }
      { print }
    ' "$ENV_FILE" > "$tempFile"
    mv "$tempFile" "$ENV_FILE"
  fi
}

setEnvKey() {
  local key="$1"
  local value="$2"
  local tempFile

  if grep -qE "^${key}=" "$ENV_FILE" 2>/dev/null; then
    tempFile="$(mktemp)"
    awk -v target="$key" -v replacement="$value" '
      BEGIN { FS=OFS="=" }
      $1 == target { print target, replacement; next }
      { print }
    ' "$ENV_FILE" > "$tempFile"
    mv "$tempFile" "$ENV_FILE"
  else
    printf '\n%s=%s\n' "$key" "$value" >> "$ENV_FILE"
  fi
}

detectDatabaseWithAppSchema() {
  local postgresUser="$1"
  local postgresPassword="$2"
  local fallbackDb="$3"
  local databases
  local databaseName

  databases="$(
    docker exec \
      -e PGPASSWORD="$postgresPassword" \
      postgres \
      psql -U "$postgresUser" -d postgres -At \
      -c "SELECT datname FROM pg_database WHERE datallowconn = true AND datistemplate = false ORDER BY datname;" \
      2>/dev/null || true
  )"

  while IFS= read -r databaseName; do
    [ -n "$databaseName" ] || continue

    if docker exec \
      -e PGPASSWORD="$postgresPassword" \
      postgres \
      psql -U "$postgresUser" -d "$databaseName" -At \
      -c "SELECT 1 FROM pg_namespace WHERE nspname = 'app' LIMIT 1;" \
      2>/dev/null | grep -qx "1"; then
      echo "$databaseName"
      return 0
    fi
  done <<< "$databases"

  echo "$fallbackDb"
}

createInitialEnv() {
  local postgresUser="$1"
  local postgresPassword="$2"
  local postgresDb="$3"

  cat > "$ENV_FILE" <<EOF
LIA2_ENVIRONMENT=DEV
LIA2_RELEASE=0.7.1-agentic-tutor-visual-learning-fix01
LIA2_BACKEND_PORT=8196
LIA2_STUDENT_WEB_PORT=8197
LIA2_CONTROL_API_PORT=8198
LIA2_CONTROL_CENTER_PORT=8199
LIA2_POSTGRES_USER=${postgresUser}
LIA2_POSTGRES_PASSWORD=${postgresPassword}
LIA2_POSTGRES_DB=${postgresDb}
EOF
}

echo "[LIA2] Validando pré-requisitos..."
requireCommand docker
docker compose version >/dev/null 2>&1 || fail "Docker Compose v2 não está disponível."

containerIsRunning "postgres" || fail "O container PostgreSQL existente 'postgres' não está em execução."
containerIsRunning "ollama" || fail "O container Ollama existente 'ollama' não está em execução."

docker network inspect docker_default >/dev/null 2>&1 \
  || fail "A rede Docker externa 'docker_default' não foi encontrada."

if [ ! -f "$ENV_FILE" ]; then
  echo "[LIA2] Criando configuração local sem alterar PostgreSQL/Ollama existentes..."

  postgresUser="$(readContainerEnv postgres POSTGRES_USER)"
  postgresPassword="$(readContainerEnv postgres POSTGRES_PASSWORD)"
  postgresDb="$(readContainerEnv postgres POSTGRES_DB)"

  postgresUser="${postgresUser:-postgres}"
  postgresDb="${postgresDb:-$postgresUser}"

  if [ -z "$postgresPassword" ]; then
    read -r -s -p "Informe a senha do PostgreSQL (será salva apenas no .env local): " postgresPassword
    echo
  fi

  [ -n "$postgresPassword" ] || fail "Senha PostgreSQL não informada."

  postgresDb="$(detectDatabaseWithAppSchema "$postgresUser" "$postgresPassword" "$postgresDb")"
  echo "[LIA2] Database selecionado: $postgresDb"

  createInitialEnv "$postgresUser" "$postgresPassword" "$postgresDb"
fi

chmod 600 "$ENV_FILE"

# Foundation 003B adiciona segurança operacional mesmo em instalações que já possuem .env do 003A.
ensureEnvKey "LIA2_ADMIN_TOKEN" "$(generateToken)"
ensureEnvKey "LIA2_OPS_INTERNAL_TOKEN" "$(generateToken)"
setEnvKey "LIA2_RELEASE" "0.7.1-agentic-tutor-visual-learning-fix01"

echo "[LIA2] Validando arquitetura do repositório e fronteiras Docker..."
python3 scripts/validateStudentWebArchitecture.py

echo "[LIA2] Executando testes antes da subida..."

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build \
  lia2-backend lia2-control-api lia2-ops-agent

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm -e LIA2_PROCESSING_WORKER_ENABLED=false -e LIA2_PEDAGOGICAL_WORKER_ENABLED=false -e LIA2_AGENT_TUTOR_WORKER_ENABLED=false lia2-backend pytest -q
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm lia2-control-api pytest -q
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm lia2-ops-agent pytest -q

echo "[LIA2] Validando builds de produção do Student Web e Control Center..."
docker compose -f docker-compose.lia2.yml build lia2-student-web lia2-control-center

echo "[LIA2] Aplicando migrations do schema lia2..."
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm lia2-backend \
  alembic -c database/alembic.ini upgrade head

echo "[LIA2] Construindo e subindo o Agentic Tutor + Visual Learning Engine 009 FIX01..."
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --build

echo
echo "[LIA2] Agentic Tutor + Visual Learning Engine 009 FIX01 iniciado."
echo "Control Center: http://localhost:8199"
echo "Student Web:    http://localhost:8197"
echo "Backend Docs:   http://localhost:8196/docs"
echo "Control API:    http://localhost:8198/docs"
echo
echo "Token administrativo DEV:"
echo "$(getEnvValue LIA2_ADMIN_TOKEN)"
echo
echo "Use esse token somente no login do Control Center."
