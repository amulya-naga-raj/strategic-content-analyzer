import pandas as pd
import numpy as np
import io

PLATFORM_SIGNATURES = {
    "YouTube": ["video title", "video views", "watch time (hours)", "subscribers gained"],
    "Instagram": ["impressions", "reach", "profile visits", "website clicks"],
    "TikTok": ["video views", "profile views", "likes", "comments", "shares"],
    "LinkedIn": ["impressions", "clicks", "ctr (%)", "reactions"],
    "Twitter": ["impressions", "engagements", "retweets", "likes"],
}

STANDARD_COLUMNS = [
    "platform", "post_id", "date", "title",
    "views", "impressions", "reach",
    "likes", "comments", "shares", "saves",
    "watch_time", "duration",
    "engagement_rate", "authenticity_score", "manipulation_flag"
]

COLUMN_MAPS = {
    "YouTube": {
        "views": ["video views", "views"],
        "impressions": ["impressions"],
        "reach": ["reach", "unique viewers"],
        "likes": ["likes"],
        "comments": ["comments"],
        "shares": ["shares"],
        "saves": ["saves", "playlist adds"],
        "watch_time": ["watch time (hours)", "watch time (minutes)", "average view duration"],
        "duration": ["video length", "duration"],
        "title": ["video title", "content title", "title"],
        "date": ["date", "publish date", "published at"],
        "post_id": ["video id", "content id", "post id"],
    },
    "Instagram": {
        "views": ["video views", "views", "reach"],
        "impressions": ["impressions"],
        "reach": ["reach", "accounts reached"],
        "likes": ["likes", "post likes"],
        "comments": ["comments"],
        "shares": ["shares", "sends"],
        "saves": ["saves", "bookmarks"],
        "watch_time": ["video watch time", "avg watch time"],
        "duration": ["video duration"],
        "title": ["description", "caption", "post description"],
        "date": ["date", "publish time", "posted"],
        "post_id": ["post id", "content id", "media id"],
    },
    "TikTok": {
        "views": ["video views", "views"],
        "impressions": ["impressions"],
        "reach": ["reach", "unique viewers"],
        "likes": ["likes"],
        "comments": ["comments"],
        "shares": ["shares"],
        "saves": ["saves", "bookmarks"],
        "watch_time": ["total play time", "average watch time"],
        "duration": ["video duration", "duration"],
        "title": ["video title", "caption", "description"],
        "date": ["date", "publish time"],
        "post_id": ["video id", "content id"],
    },
    "LinkedIn": {
        "views": ["impressions", "views"],
        "impressions": ["impressions"],
        "reach": ["reach", "unique impressions"],
        "likes": ["reactions", "likes"],
        "comments": ["comments"],
        "shares": ["reposts", "shares"],
        "saves": ["saves"],
        "watch_time": ["video views", "watch time"],
        "duration": ["video duration"],
        "title": ["post title", "content", "title"],
        "date": ["date", "publish date"],
        "post_id": ["post id", "content urn"],
    },
    "Twitter": {
        "views": ["impressions", "views"],
        "impressions": ["impressions"],
        "reach": ["reach"],
        "likes": ["likes", "favorites"],
        "comments": ["replies", "comments"],
        "shares": ["retweets"],
        "saves": ["bookmarks"],
        "watch_time": [],
        "duration": [],
        "title": ["tweet text", "text", "content"],
        "date": ["time", "date", "created at"],
        "post_id": ["tweet id", "post id", "id"],
    },
}


def _safe_read(file_bytes):
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return pd.read_csv(io.BytesIO(file_bytes), encoding=enc)
        except Exception:
            continue
    raise ValueError("Could not decode CSV.")


def _detect_platform(df):
    cols = [c.lower().strip() for c in df.columns]
    best, best_score = "Unknown", 0
    for platform, sig in PLATFORM_SIGNATURES.items():
        score = sum(1 for s in sig if s in cols)
        if score > best_score:
            best, best_score = platform, score
    return best


def _find(df, src_cols, candidates, fallback=None):
    for c in candidates:
        if c in src_cols:
            return df[src_cols[c]].values
    return fallback if fallback is not None else None


def _find_numeric(df, src_cols, candidates):
    for c in candidates:
        if c in src_cols:
            return pd.to_numeric(df[src_cols[c]], errors="coerce").values
    return None


def _map_columns(df, platform):
    col_map = COLUMN_MAPS.get(platform, {})
    src_cols = {c.lower().strip(): c for c in df.columns}
    out = pd.DataFrame()
    report = {"mapped": {}, "missing": []}
    out["platform"] = platform
    out["post_id"] = _find(df, src_cols, col_map.get("post_id", []), fallback=range(len(df)))
    out["date"] = _find(df, src_cols, col_map.get("date", []))
    out["title"] = _find(df, src_cols, col_map.get("title", []), fallback="")
    for metric in ["views", "impressions", "reach", "likes", "comments", "shares", "saves", "watch_time", "duration"]:
        candidates = col_map.get(metric, [])
        val = _find_numeric(df, src_cols, candidates)
        if val is not None:
            out[metric] = val
            matched = next((c for c in candidates if c in src_cols), "inferred")
            report["mapped"][metric] = matched
        else:
            out[metric] = np.nan
            report["missing"].append(metric)
    try:
        out["engagement_rate"] = (
            (out["likes"].fillna(0) + out["comments"].fillna(0) + out["shares"].fillna(0))
            / out["views"].replace(0, np.nan) * 100
        ).round(2)
    except Exception:
        out["engagement_rate"] = np.nan
    out["authenticity_score"] = np.nan
    out["manipulation_flag"] = False
    return out[STANDARD_COLUMNS], report


def process_upload(file_bytes):
    df = _safe_read(file_bytes)
    df.columns = [str(c).strip() for c in df.columns]
    platform = _detect_platform(df)
    mapped, report = _map_columns(df, platform)
    return mapped, platform, report


def generate_sample_data(platform="YouTube", n=200):
    rng = np.random.default_rng(42)
    dates = pd.date_range(end="2025-12-31", periods=n, freq="D")
    views = rng.lognormal(mean=10.5, sigma=1.8, size=n).astype(int)
    impressions = (views * rng.uniform(1.2, 2.0, size=n)).astype(int)
    reach = (impressions * rng.uniform(0.6, 0.9, size=n)).astype(int)
    likes = (views * rng.uniform(0.02, 0.12, size=n)).astype(int)
    comments = (likes * rng.uniform(0.05, 0.25, size=n)).astype(int)
    shares = (likes * rng.uniform(0.02, 0.15, size=n)).astype(int)
    saves = (likes * rng.uniform(0.01, 0.10, size=n)).astype(int)
    watch_time = (views * rng.uniform(0.3, 0.8, size=n) * rng.uniform(2, 15, size=n)).astype(int)
    duration = rng.integers(30, 1200, size=n)
    engagement_rate = ((likes + comments + shares) / np.maximum(views, 1) * 100).round(2)
    manip_idx = rng.choice(n, size=int(n * 0.10), replace=False)
    likes[manip_idx] = (views[manip_idx] * rng.uniform(0.5, 0.9, len(manip_idx))).astype(int)
    comments[manip_idx] = (likes[manip_idx] * rng.uniform(0.001, 0.005, len(manip_idx))).astype(int)
    manipulation_flag = np.zeros(n, dtype=bool)
    manipulation_flag[manip_idx] = True
    like_comment_ratio = likes / np.maximum(comments, 1)
    auth = np.clip(100 - (like_comment_ratio / 10), 20, 100).round(1)
    return pd.DataFrame({
        "platform": platform,
        "post_id": [f"{platform[:2].upper()}{str(i+1).zfill(5)}" for i in range(n)],
        "date": dates,
        "title": [f"Post #{i+1} — {platform} Content" for i in range(n)],
        "views": views,
        "impressions": impressions,
        "reach": reach,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "saves": saves,
        "watch_time": watch_time,
        "duration": duration,
        "engagement_rate": engagement_rate,
        "authenticity_score": auth,
        "manipulation_flag": manipulation_flag,
    })
