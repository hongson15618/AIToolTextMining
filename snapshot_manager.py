import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), "saved_snapshots")
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

def save_snapshot(
    name: str,
    df_input: pd.DataFrame,
    df_live: pd.DataFrame,
    results: List[Dict[str, Any]],
    processed_rows: int,
    total_rows: int,
    target_col: str,
    elapsed_time: float,
    custom_id: Optional[str] = None
) -> str:
    """
    Lưu tiến độ hoặc kết quả clean thành một bản sao (JSON checkpoint).
    """
    now = datetime.now()
    snapshot_id = custom_id or f"SNP_{now.strftime('%Y%m%d_%H%M%S')}_{processed_rows}of{total_rows}"
    filename = f"{snapshot_id}.json"
    filepath = os.path.join(SNAPSHOT_DIR, filename)

    status = "Hoàn thành 100%" if processed_rows >= total_rows else f"Tạm dừng ({processed_rows}/{total_rows} dòng - {round(processed_rows/max(1, total_rows)*100, 1)}%)"

    snapshot_data = {
        "snapshot_id": snapshot_id,
        "name": name.strip() if name.strip() else f"Bản sao ({now.strftime('%d/%m/%Y %H:%M:%S')}) - {processed_rows}/{total_rows} dòng",
        "created_at": now.strftime("%d/%m/%Y %H:%M:%S"),
        "timestamp": time.time(),
        "total_rows": total_rows,
        "processed_rows": processed_rows,
        "status": status,
        "target_col": target_col,
        "elapsed_time": round(elapsed_time, 2),
        "df_input": df_input.to_dict(orient="records") if df_input is not None else [],
        "df_live": df_live.to_dict(orient="records") if df_live is not None else [],
        "results": results or []
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, ensure_ascii=False, indent=2)

    return snapshot_id

def list_snapshots() -> List[Dict[str, Any]]:
    """
    Liệt kê danh sách tất cả các bản sao đã lưu (chỉ đọc metadata để tối ưu tốc độ).
    """
    snapshots = []
    if not os.path.exists(SNAPSHOT_DIR):
        return snapshots

    for fname in os.listdir(SNAPSHOT_DIR):
        if fname.endswith(".json"):
            filepath = os.path.join(SNAPSHOT_DIR, fname)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    snapshots.append({
                        "snapshot_id": data.get("snapshot_id", fname[:-5]),
                        "name": data.get("name", "Bản sao không tên"),
                        "created_at": data.get("created_at", ""),
                        "timestamp": data.get("timestamp", 0),
                        "total_rows": data.get("total_rows", 0),
                        "processed_rows": data.get("processed_rows", 0),
                        "status": data.get("status", "N/A"),
                        "target_col": data.get("target_col", ""),
                        "elapsed_time": data.get("elapsed_time", 0.0),
                        "file_size_kb": round(os.path.getsize(filepath) / 1024, 1)
                    })
            except Exception:
                continue

    # Sắp xếp mới nhất lên đầu
    snapshots.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    return snapshots

def load_snapshot(snapshot_id: str) -> Optional[Dict[str, Any]]:
    """
    Nạp dữ liệu chi tiết của một bản sao từ file JSON.
    """
    filepath = os.path.join(SNAPSHOT_DIR, f"{snapshot_id}.json")
    if not os.path.exists(filepath):
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Chuyển đổi ngược lại thành DataFrame
    if "df_input" in data and isinstance(data["df_input"], list):
        data["df_input"] = pd.DataFrame(data["df_input"])
    else:
        data["df_input"] = pd.DataFrame()

    if "df_live" in data and isinstance(data["df_live"], list):
        data["df_live"] = pd.DataFrame(data["df_live"])
    else:
        data["df_live"] = pd.DataFrame()

    return data

def delete_snapshot(snapshot_id: str) -> bool:
    """
    Xóa một bản sao theo ID.
    """
    filepath = os.path.join(SNAPSHOT_DIR, f"{snapshot_id}.json")
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception:
            return False
    return False
