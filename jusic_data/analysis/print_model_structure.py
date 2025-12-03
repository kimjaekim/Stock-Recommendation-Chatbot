# print_model_structure.py
import os
import io
import sys
import pickle
import argparse
from typing import Any, Dict, Optional

# Windows 콘솔 한글/유니코드 출력 대응
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

KEYS_ACC = ["acc", "accuracy"]
KEYS_F1 = ["f1", "f1_score"]
KEYS_AUC = ["auc", "roc_auc", "roc_auc_score"]
KEYS_N = ["n", "count", "num_samples", "samples"]
KEYS_POS = ["pos_rate", "positive_rate", "positive_ratio"]

def pick(d: Dict[str, Any], keys) -> Optional[float]:
    if not isinstance(d, dict):
        return None
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None

def fmt(v: Optional[float], nd=6) -> str:
    if v is None:
        return "-"
    try:
        if isinstance(v, (int,)):
            return str(v)
        return f"{float(v):.{nd}f}"
    except Exception:
        return str(v)

def short_params(params: Dict[str, Any]) -> Dict[str, Any]:
    keys = [
        "penalty", "C", "solver", "max_iter", "class_weight", "random_state",
        "n_estimators", "max_depth", "min_samples_split", "min_samples_leaf",
        "final_estimator", "passthrough",
    ]
    out = {}
    for k in keys:
        if k in params:
            v = params[k]
            out[k] = v.__class__.__name__ if hasattr(v, "__class__") and k == "final_estimator" else v
    return out

def print_block(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def print_estimator(prefix: str, est: Any):
    if est is None:
        print(f"- {prefix}: None")
        return
    cls = est.__class__.__name__
    print(f"- {prefix}: {cls}")
    if hasattr(est, "get_params"):
        params = est.get_params(deep=False)
        sp = short_params(params)
        print(f"  params: {sp}")
    if cls.lower().startswith("stacking") and hasattr(est, "estimators"):
        try:
            names = [name for name, _ in est.estimators]
            print(f"  base_estimators: {names}")
            fe = getattr(est, "final_estimator", None)
            if fe is not None:
                print(f"  final_estimator: {fe.__class__.__name__}")
        except Exception:
            pass

def print_pca(pca: Any):
    if pca is None:
        print("- PCA: None")
        return
    cls = pca.__class__.__name__
    n_comp = getattr(pca, "n_components", None)
    print(f"- PCA: {cls}, n_components={n_comp}")
    evr = getattr(pca, "explained_variance_ratio_", None)
    if evr is not None:
        try:
            total = float(sum(evr))
            print(f"  explained_variance_ratio_sum: {total:.4f}")
        except Exception:
            pass

def print_scaler(scaler: Any):
    if scaler is None:
        print("- Scaler: None")
        return
    print(f"- Scaler: {scaler.__class__.__name__}")

def print_features(features: Any):
    if features is None:
        print("- Features: None")
        return
    try:
        flist = list(features)
        print(f"- Features ({len(flist)}): {flist}")
    except Exception:
        print(f"- Features: {features}")

def print_metrics_block(name: str, d: Optional[Dict[str, Any]]):
    acc = f1 = auc = n = pos = None
    if isinstance(d, dict):
        acc = pick(d, KEYS_ACC)
        f1 = pick(d, KEYS_F1)
        auc = pick(d, KEYS_AUC)
        n   = pick(d, KEYS_N)
        pos = pick(d, KEYS_POS)
    print(f"  {name:>5}: acc={fmt(acc,6)} f1={fmt(f1,6)} auc={fmt(auc,6)} n={fmt(n,0)} pos_rate={fmt(pos,4)}")

def print_all_metrics(bundle: Dict[str, Any]):
    print("- metrics:")
    # 일반적으로 쓰는 키 후보 모두 탐색
    train = bundle.get("train_results") or bundle.get("train") or bundle.get("train_metrics")
    val   = bundle.get("val_results")   or bundle.get("valid") or bundle.get("validation") or bundle.get("val_metrics")
    test  = bundle.get("test_results")  or bundle.get("test")  or bundle.get("test_metrics")
    print_metrics_block("train", train)
    print_metrics_block("val",   val)
    print_metrics_block("test",  test)

def is_model_bundle(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    # 키 기반: 모델/전처리/메트릭 관련 키가 하나라도 있으면 번들로 간주
    key_hits = {
        "model", "estimator", "scaler", "pca", "features", "feature_names", "feature_list",
        "train_results", "val_results", "test_results", "train", "valid", "validation", "test",
        "train_metrics", "val_metrics", "test_metrics"
    }
    if any(k in obj for k in key_hits):
        return True
    return False

def print_bundle(name: str, bundle: Dict[str, Any]):
    print_block(f"[{name}]")
    model = bundle.get("model") or bundle.get("estimator")
    scaler = bundle.get("scaler")
    pca = bundle.get("pca")
    features = bundle.get("features") or bundle.get("feature_names") or bundle.get("feature_list")

    print_estimator("Model", model)
    print_scaler(scaler)
    print_pca(pca)
    print_features(features)
    print_all_metrics(bundle)

def walk_obj(root_name: str, obj: Any):
    if is_model_bundle(obj):
        print_bundle(root_name, obj)
        return
    if isinstance(obj, dict):
        nested = any(isinstance(v, dict) for v in obj.values())
        if nested:
            for k, v in obj.items():
                if is_model_bundle(v):
                    print_bundle(f"{root_name}.{k}", v)
                elif isinstance(v, dict):
                    for kk, vv in v.items():
                        if is_model_bundle(vv):
                            print_bundle(f"{root_name}.{k}.{kk}", vv)
                        else:
                            walk_obj(f"{root_name}.{k}.{kk}", vv)
                else:
                    walk_obj(f"{root_name}.{k}", v)
        else:
            for k, v in obj.items():
                if is_model_bundle(v):
                    print_bundle(f"{root_name}.{k}", v)
                else:
                    walk_obj(f"{root_name}.{k}", v)
        return
    if isinstance(obj, (list, tuple)):
        for idx, item in enumerate(obj):
            if is_model_bundle(item):
                print_bundle(f"{root_name}[{idx}]", item)
            else:
                walk_obj(f"{root_name}[{idx}]", item)

def main():
    parser = argparse.ArgumentParser(description="Print saved models structure and metrics from PKL")
    parser.add_argument("--pkl", type=str, default="final_multi_timeframe_models.pkl", help="PKL 파일 경로")
    args = parser.parse_args()

    pkl_path = args.pkl
    if not os.path.isabs(pkl_path):
        pkl_path = os.path.join(os.path.dirname(__file__), pkl_path)

    if not os.path.exists(pkl_path):
        print(f"[ERROR] PKL 파일이 없습니다: {pkl_path}")
        sys.exit(1)

    print_block(f"Load PKL: {pkl_path}")
    with open(pkl_path, "rb") as f:
        obj = pickle.load(f)

    print(f"- Top object type: {obj.__class__.__name__}")
    if isinstance(obj, dict):
        keys = list(obj.keys())
        # 상위 키를 최대 100개까지 미리 보여주어 구조 파악을 돕는다
        preview = keys[:100]
        print(f"- Top-level keys ({len(keys)}): {preview}")
    # 특수 구조: {models, scalers, pcas, performance, medians}
    if isinstance(obj, dict) and {"models", "scalers", "pcas"}.issubset(obj.keys()):
        models = obj.get("models", {})
        scalers = obj.get("scalers", {})
        pcas = obj.get("pcas", {})
        perf = obj.get("performance", {})

        def iter_flat(d):
            for k, v in d.items():
                yield k, v

        def iter_nested(d):
            for t, sub in d.items():
                if isinstance(sub, dict):
                    for h, v in sub.items():
                        yield f"{t}_{h}", v

        # 키 형태 감지 (flat vs nested)
        sample_val = next(iter(models.values()), None)
        is_nested = any(isinstance(v, dict) for v in models.values())
        iterator = iter_nested if is_nested else iter_flat

        seen = set()
        for key, est in iterator(models):
            seen.add(key)
            bundle = {
                "model": est,
                "scaler": (scalers.get(key) if not is_nested else scalers.get(key.split("_")[0], {}).get(key.split("_")[1], None)),
                "pca":    (pcas.get(key)    if not is_nested else pcas.get(key.split("_")[0], {}).get(key.split("_")[1], None)),
            }
            # 성능 묶기 (동일 키 구조 가정)
            if isinstance(perf, dict):
                if not is_nested:
                    bundle.update(perf.get(key, {}))
                else:
                    t, h = key.split("_", 1)
                    bundle.update(perf.get(t, {}).get(h, {}))
            print_bundle(key, bundle)

        # models에 없는 키가 성능/전처리에만 존재할 경우도 보조 출력
        for source_name, source in (("scalers", scalers), ("pcas", pcas), ("performance", perf)):
            # 동일한 iterator로 순회
            itr = iter_nested if any(isinstance(v, dict) for v in source.values()) else iter_flat
            for key, _ in itr(source):
                if key in seen:
                    continue
                print_block(f"[{key}] (no model found, only {source_name})")
                # 가능 정보만 제한적으로 출력
                if source_name == "performance":
                    print_all_metrics(source.get(key, {}) if not is_nested else source.get(key.split("_")[0], {}).get(key.split("_")[1], {}))
        
    else:
        walk_obj("root", obj)
    print("\n완료.")

if __name__ == "__main__":
    main()