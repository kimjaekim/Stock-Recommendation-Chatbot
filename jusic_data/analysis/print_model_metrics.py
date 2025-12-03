import pickle
from pathlib import Path
import traceback

PKL_PATH = Path(__file__).parent / 'final_multi_timeframe_models.pkl'

# 기대 키: (task, horizon) e.g., ('direction','1day') → dict(model=..., scaler=..., pca=..., features=[...], metrics={...})
EXPECTED_TASKS = ['direction', 'volatility', 'risk']
EXPECTED_HORIZONS = ['1day', '3day', '5day', '10day']


def safe_get(d: dict, key: str, default='N/A'):
    try:
        return d.get(key, default)
    except Exception:
        return default


def format_metrics(metrics: dict | None) -> str:
    if not isinstance(metrics, dict):
        return 'N/A'
    acc = safe_get(metrics, 'accuracy')
    f1 = safe_get(metrics, 'f1')
    auc = safe_get(metrics, 'auc')
    val_acc = safe_get(metrics, 'val_accuracy')
    test_acc = safe_get(metrics, 'test_accuracy')
    test_f1 = safe_get(metrics, 'test_f1')
    test_auc = safe_get(metrics, 'test_auc')
    parts = []
    if acc != 'N/A':
        parts.append(f"acc={acc}")
    if f1 != 'N/A':
        parts.append(f"f1={f1}")
    if auc != 'N/A':
        parts.append(f"auc={auc}")
    if val_acc != 'N/A':
        parts.append(f"val_acc={val_acc}")
    if test_acc != 'N/A':
        parts.append(f"test_acc={test_acc}")
    if test_f1 != 'N/A':
        parts.append(f"test_f1={test_f1}")
    if test_auc != 'N/A':
        parts.append(f"test_auc={test_auc}")
    return ', '.join(parts) if parts else 'N/A'


def main():
    if not PKL_PATH.exists():
        print(f"❌ 모델 파일이 없습니다: {PKL_PATH}")
        return

    with open(PKL_PATH, 'rb') as f:
        obj = pickle.load(f)

    print("====================================================")
    print("📦 final_multi_timeframe_models.pkl - 모델 성능 요약")
    print("====================================================")

    # pkl 구조 추정: dict[(task,horizon)] = {...} 또는 dict[task][horizon]
    def get_entry(task, horizon):
        if isinstance(obj, dict):
            # 1) (task,horizon) 튜플 키
            if (task, horizon) in obj:
                return obj[(task, horizon)]
            # 2) 이중 dict
            if task in obj and isinstance(obj[task], dict) and horizon in obj[task]:
                return obj[task][horizon]
        return None

    for task in EXPECTED_TASKS:
        print(f"\n[{task.upper()}]")
        for hz in EXPECTED_HORIZONS:
            entry = get_entry(task, hz)
            if not entry:
                print(f" - {hz}: N/A (엔트리 없음)")
                continue
            features = safe_get(entry, 'features')
            metrics = safe_get(entry, 'metrics')
            alg = safe_get(entry, 'algorithm')
            model_name = safe_get(entry, 'model_name')
            txt = format_metrics(metrics)
            feats = len(features) if isinstance(features, (list, tuple)) else 'N/A'
            alg_name = model_name if model_name != 'N/A' else alg
            print(f" - {hz}: metrics[{txt}] | features={feats} | algo={alg_name}")

    print("\n✅ 출력 완료")


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
