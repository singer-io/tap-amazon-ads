# Changelog

## 1.0.1 [#12](https://github.com/singer-io/tap-amazon-ads/pull/12)
- Streams the credentials cannot access (403) are now excluded from the catalog during discovery instead of raising an error.
- Added unit tests for discovery, bookmark read/write, `modify_object`, incremental/full-table sync, sync orchestration, and `get_records` pagination.


## 1.0.0 [#10](https://github.com/singer-io/tap-amazon-ads/pull/10)
#### 1. Replication Keys Flattened from `extendedData` (9 streams)

The replication key for 9 incremental streams was previously stored as a dot-notation path into the nested `extendedData` object (e.g., `extendedData.lastUpdateDateTime`). It is now promoted to a **top-level field** on each record (e.g., `lastUpdateDateTime`).

State bookmarks saved under the old dot-notation key will **not** be found after upgrading, causing those streams to **re-sync from `start_date`**.

**Affected streams and their bookmark key changes:**

| Stream | Old Bookmark Key | New Bookmark Key |
|---|---|---|
| `portfolios` | `extendedData.lastUpdateDateTime` | `lastUpdateDateTime` |
| `sponsored_brands_ads` | `extendedData.lastUpdateDate` | `lastUpdateDate` |
| `sponsored_brands_ad_groups` | `extendedData.lastUpdateDate` | `lastUpdateDate` |
| `sponsored_brands_campaigns` | `extendedData.lastUpdateDate` | `lastUpdateDate` |
| `sponsored_products_ads` | `extendedData.lastUpdateDateTime` | `lastUpdateDateTime` |
| `sponsored_products_ad_groups` | `extendedData.lastUpdateDateTime` | `lastUpdateDateTime` |
| `sponsored_products_campaigns` | `extendedData.lastUpdateDateTime` | `lastUpdateDateTime` |
| `sponsored_products_keywords` | `extendedData.lastUpdateDateTime` | `lastUpdateDateTime` |
| `sponsored_products_negative_keywords` | `extendedData.lastUpdateDateTime` | `lastUpdateDateTime` |

**Migration:** Before upgrading, reset the bookmarks for these streams in your state file, or delete the state file entirely so they sync from `start_date`:

```json
// Old state (v1.x) — bookmarks stored under dot-notation keys
{
  "bookmarks": {
    "portfolios": {
      "extendedData.lastUpdateDateTime": "2024-01-01T00:00:00Z"
    },
    "sponsored_products_campaigns": {
      "extendedData.lastUpdateDateTime": "2024-01-01T00:00:00Z"
    }
  }
}

// New state (v2.0) — bookmarks stored under flat keys
{
  "bookmarks": {
    "portfolios": {
      "lastUpdateDateTime": "2024-01-01T00:00:00Z"
    },
    "sponsored_products_campaigns": {
      "lastUpdateDateTime": "2024-01-01T00:00:00Z"
    }
  }
}
```

#### 2. Primary Key Rename — `sponsored_brands_store_assets`

The primary key field has been renamed to match the exact casing returned by the Amazon Ads API:

| Old Primary Key | New Primary Key |
|---|---|
| `assetID` | `assetId` |

**Migration:** Targets that created a column or index on `assetID` will need to update their schema. In warehouses (e.g., Redshift, Snowflake, BigQuery), rename the column or drop and recreate the table before running v2.0.

---

### Other Changes

- **Configurable `page_size`**: The pagination page size can now be controlled via `page_size` in `config.json` (default: 100).
- **Python 3.12**: CircleCI CI/CD pipeline updated from Python 3.11 to Python 3.12.
- **Integration tests re-enabled** in CircleCI.
- **Schema additions**: The replication key field (`lastUpdateDate`, `lastUpdateDateTime`) is now emitted as a top-level field in the record output for the 9 affected streams, with `format: date-time` in their JSON schemas.

---

## 0.0.1 — Initial Release

- Initial Singer tap implementation for the Amazon Ads API.
