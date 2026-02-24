# Strategic Content Analyzer 
# Strategic Content Analyzer

A production-grade data standardization pipeline that automatically detects, repairs, and normalizes social media CSV exports from YouTube, LinkedIn, Instagram, and TikTok into a unified ML-ready schema.

## Problem Solved

Every social media platform exports analytics data differently:
- Different column names (views vs impressions vs play count)
- Different encoding (UTF-8, CP1252, Latin-1)
- Missing or inconsistent metrics
- Cannot be compared or analyzed together

This system automatically:
- Detects the platform from CSV column signatures
- Repairs encoding issues (fixes mojibake like "ÐÑ…")
- Maps heterogeneous metrics into standardized schema
- Reports what was mapped vs what's missing (transparent data quality)

## Architecture
```
strategic-content-analyzer/
├── src/
│   ├── data_processing/
│   │   ├── __init__.py
│   │   └── schema.py          # Core: encoding repair, platform detection, metric mapping
│   └── dashboard/
│       ├── __init__.py
│       └── app.py              # Streamlit dashboard
├── requirements.txt
└── README.md
```

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
streamlit run src/dashboard/app.py
```

Upload any platform CSV export. The system will:
1. Auto-detect platform by column structure
2. Fix encoding issues automatically
3. Map metrics into standard schema
4. Show mapping report with quality metrics

## Standard Schema

All platforms mapped to:
- `platform`, `post_id`, `date`, `author`, `title`, `caption`, `url`
- `views`, `impressions`, `reach`
- `likes`, `comments`, `shares`, `saves`
- `watch_time_seconds`, `duration_seconds`

## Technical Highlights

- **Encoding Repair**: Tries UTF-8 → UTF-8-sig → CP1252 → Latin-1 fallback
- **Schema Intelligence**: Detects platform by column combinations, not user input
- **Transparent Quality**: Shows what mapped, what's missing, and why
- **ML-Ready Output**: Standardized format for engagement prediction, anomaly detection

## Supported Platforms

- YouTube (Trending datasets)
- LinkedIn (Analytics exports)
- Instagram (Business insights)
- TikTok (Creator analytics)