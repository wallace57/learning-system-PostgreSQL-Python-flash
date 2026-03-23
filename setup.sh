#!/usr/bin/env bash
# =============================================================================
# setup.sh – One-click setup cho Learning Data System (T3H)
# Hỗ trợ: macOS / Linux
# Yêu cầu: Docker Desktop đang chạy
#
# Cách dùng:
#   chmod +x setup.sh
#   ./setup.sh              # Chạy với dữ liệu T3H (mặc định)
#   ./setup.sh generic      # Chạy với dữ liệu generic
#   ./setup.sh down         # Dừng và xóa containers
#   ./setup.sh reset        # Xóa toàn bộ (kể cả volume) và rebuild
#   ./setup.sh tools        # Chạy thêm pgAdmin
# =============================================================================
set -euo pipefail

# ── Màu sắc terminal ─────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

banner() {
  echo -e "${CYAN}${BOLD}"
  echo "  ╔═══════════════════════════════════════════════╗"
  echo "  ║   Learning Data System – T3H Docker Setup     ║"
  echo "  ╚═══════════════════════════════════════════════╝"
  echo -e "${NC}"
}

info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }
step()    { echo -e "\n${BOLD}── $* ${NC}"; }

# ── Kiểm tra Docker ──────────────────────────────────────────────────────────
check_docker() {
  if ! command -v docker &>/dev/null; then
    error "Docker chưa được cài đặt. Tải tại: https://docs.docker.com/get-docker/"
  fi
  if ! docker info &>/dev/null 2>&1; then
    error "Docker Desktop chưa chạy. Hãy khởi động Docker Desktop trước."
  fi
  success "Docker đang chạy ($(docker --version | cut -d' ' -f3 | tr -d ','))"
}

# ── Setup file .env ───────────────────────────────────────────────────────────
setup_env() {
  if [ ! -f ".env" ]; then
    info "Tạo file .env từ .env.example..."
    cp .env.example .env
    success ".env đã được tạo"
  else
    info "Đã có file .env – dùng cấu hình hiện tại"
  fi
  # Load env
  set -a; source .env; set +a
}

# ── Xử lý tham số ────────────────────────────────────────────────────────────
COMMAND="${1:-up}"
PRESET="${2:-}"

banner

case "$COMMAND" in
  # ── Dừng containers ────────────────────────────────────────────────────────
  down|stop)
    step "Dừng containers..."
    docker compose down --remove-orphans
    success "Đã dừng tất cả containers"
    exit 0
    ;;

  # ── Reset toàn bộ (xóa cả volume) ─────────────────────────────────────────
  reset)
    step "Reset toàn bộ (xóa containers + volumes)..."
    warn "Thao tác này sẽ XÓA TOÀN BỘ dữ liệu trong database!"
    read -r -p "Tiếp tục? (y/N): " confirm
    [[ "$confirm" =~ ^[Yy]$ ]] || { info "Hủy."; exit 0; }
    docker compose down -v --remove-orphans 2>/dev/null || true
    success "Đã xóa toàn bộ. Chạy lại: ./setup.sh"
    exit 0
    ;;

  # ── Chạy pgAdmin ───────────────────────────────────────────────────────────
  tools)
    step "Khởi động với pgAdmin..."
    check_docker
    setup_env
    export DATA_PRESET="${PRESET:-t3h}"
    docker compose --profile tools up -d --build
    echo ""
    success "Đã khởi động! Truy cập:"
    echo -e "   ${CYAN}Web Demo :${NC} http://localhost:${WEB_PORT:-5000}"
    echo -e "   ${CYAN}pgAdmin  :${NC} http://localhost:${PGADMIN_PORT:-8080}"
    echo -e "   ${YELLOW}Login pgAdmin:${NC} ${PGADMIN_EMAIL:-admin@t3h.edu.vn} / ${PGADMIN_PASSWORD:-admin123}"
    exit 0
    ;;

  # ── Logs ───────────────────────────────────────────────────────────────────
  logs)
    docker compose logs -f --tail=50
    exit 0
    ;;

  # ── Status ─────────────────────────────────────────────────────────────────
  status|ps)
    docker compose ps
    exit 0
    ;;

  # ── Mặc định: khởi động ────────────────────────────────────────────────────
  up|generic|t3h|*)
    # Xác định preset
    if [[ "$COMMAND" == "generic" ]]; then
      PRESET="generic"
    elif [[ "$COMMAND" == "t3h" ]]; then
      PRESET="t3h"
    else
      PRESET="${PRESET:-t3h}"
    fi
    ;;
esac

# ── Kiểm tra điều kiện ───────────────────────────────────────────────────────
step "Kiểm tra môi trường"
check_docker
setup_env

# ── Xuất biến cho docker-compose ─────────────────────────────────────────────
export DATA_PRESET="$PRESET"
info "Preset dữ liệu: ${BOLD}$(echo "$PRESET" | tr '[:lower:]' '[:upper:]')${NC}"

# ── Dừng containers cũ nếu đang chạy ─────────────────────────────────────────
step "Dừng containers cũ..."
docker compose down --remove-orphans 2>/dev/null || true

# ── Build images ─────────────────────────────────────────────────────────────
step "Build Docker images..."
docker compose build --parallel
success "Build xong"

# ── Khởi động PostgreSQL + Archive Node ─────────────────────────────────────
step "Khởi động PostgreSQL + Archive Node..."
docker compose up -d postgres archive_node
info "Chờ PostgreSQL (main) sẵn sàng..."

TIMEOUT=60
ELAPSED=0
until docker compose exec -T postgres pg_isready \
        -U "${POSTGRES_USER:-postgres}" \
        -d "${POSTGRES_DB:-learning_data_system}" &>/dev/null; do
  if [ $ELAPSED -ge $TIMEOUT ]; then
    error "PostgreSQL không khởi động được sau ${TIMEOUT}s"
  fi
  printf "."
  sleep 2
  ELAPSED=$((ELAPSED+2))
done
echo ""
success "PostgreSQL (main) sẵn sàng!"

info "Chờ Archive Node (PostgreSQL thứ 2) sẵn sàng..."
ELAPSED=0
until docker compose exec -T archive_node pg_isready \
        -U "archive_reader" -d "t3h_archive" &>/dev/null; do
  if [ $ELAPSED -ge $TIMEOUT ]; then
    warn "Archive Node chưa sẵn sàng sau ${TIMEOUT}s – FDW có thể lỗi"
    break
  fi
  printf "."
  sleep 2
  ELAPSED=$((ELAPSED+2))
done
echo ""
success "Archive Node sẵn sàng! (Schema t3h_archive đã được khởi tạo)"

# ── Chạy Data Generator ──────────────────────────────────────────────────────
step "Chạy Data Generator ($(echo "$PRESET" | tr '[:lower:]' '[:upper:]'))..."
docker compose run --rm \
  -e DB_HOST=postgres \
  -e DB_NAME="${POSTGRES_DB:-learning_data_system}" \
  -e DB_USER="${POSTGRES_USER:-postgres}" \
  -e DB_PASS="${POSTGRES_PASSWORD:-postgres123}" \
  -e DATA_PRESET="$PRESET" \
  data-generator
success "Dữ liệu đã được nạp vào database"

# ── Chạy Demo SQL files (CSDL Nâng cao) ──────────────────────────────────────
step "Import Demo SQL – CSDL Nâng cao (thạc sĩ)..."
DB="${POSTGRES_DB:-learning_data_system}"
USER="${POSTGRES_USER:-postgres}"

DEMO_FILES=(
  "demo_oop_relational"
  "demo_deductive"
  "demo_distributed"
  "demo_nosql_jsonb"
  "demo_spatial_postgis"
  "demo_fulltext_multimedia"
)

for demo in "${DEMO_FILES[@]}"; do
  info "  Chạy ${demo}.sql ..."
  if docker compose exec -T postgres \
      psql -U "$USER" -d "$DB" \
      -v ON_ERROR_STOP=0 \
      -f "/demo_sql/${demo}.sql" \
      > /dev/null 2>&1; then
    success "  ✓ ${demo}.sql"
  else
    # Chạy lại để xem lỗi cụ thể (nhưng không dừng)
    docker compose exec -T postgres \
      psql -U "$USER" -d "$DB" \
      -v ON_ERROR_STOP=0 \
      -f "/demo_sql/${demo}.sql" \
      2>&1 | grep -E "^ERROR|^FATAL" | head -5 || true
    warn "  ⚠ ${demo}.sql có lỗi (xem logs để biết thêm)"
  fi
done
success "Đã import xong 6 demo CSDL Nâng cao"

# ── Khởi động Web App ─────────────────────────────────────────────────────────
step "Khởi động Web Demo..."
docker compose up -d web
sleep 3  # Chờ Flask khởi động

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║  ✓  Hệ thống đã sẵn sàng!                        ║${NC}"
echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e " ${CYAN}🌐 Web Demo       :${NC} http://localhost:${WEB_PORT:-5000}"
echo -e " ${CYAN}🐘 PostgreSQL Main:${NC} localhost:${POSTGRES_PORT:-5432}"
echo -e "    Database         : ${POSTGRES_DB:-learning_data_system}"
echo -e "    User/Pass        : ${POSTGRES_USER:-postgres} / ${POSTGRES_PASSWORD:-postgres123}"
echo -e " ${CYAN}🐘 Archive Node   :${NC} localhost:${ARCHIVE_PORT:-5433}"
echo -e "    Database         : t3h_archive"
echo -e "    User/Pass        : archive_reader / readonly123"
echo ""
echo -e " ${YELLOW}Lệnh hữu ích:${NC}"
echo -e "   ./setup.sh logs      # Xem logs realtime"
echo -e "   ./setup.sh status    # Xem trạng thái containers"
echo -e "   ./setup.sh tools     # Chạy thêm pgAdmin (port ${PGADMIN_PORT:-8080})"
echo -e "   ./setup.sh reset     # Xóa toàn bộ và reset"
echo -e "   ./setup.sh down      # Dừng tất cả"
echo ""
echo -e " ${YELLOW}Kết nối thủ công:${NC}"
echo -e "   psql -h localhost -p ${POSTGRES_PORT:-5432} -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-learning_data_system}"
echo ""
