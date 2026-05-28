# index-test

FastAPI service for managing MongoDB collections and indexes, backed by the [monday.com Document DB](https://developer.monday.com/apps/docs/document-db).

## Project structure

```
main.py              # App init, lifespan, router registration
database.py          # MongoClient singleton and get_db()
routers/
  collection.py      # Collection endpoints
  index.py           # Index endpoints (nested under /collection)
```

## Local development

Set the connection string to a local MongoDB instance (the database name is part of the URI):

```bash
MNDY_MONGODB_CONNECTION_STRING=mongodb://localhost:27017/index_test uvicorn main:app --reload
```

In monday production environments, `MNDY_MONGODB_CONNECTION_STRING` is injected automatically.

To inspect production data locally (read-only, valid for 30 minutes):

```bash
mapps database:connection-string
```

## API

### Collections

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/collection` | List all collections |
| `POST` | `/collection` | Create a collection |
| `DELETE` | `/collection/{name}` | Drop a collection |

**POST /collection**
```json
{ "name": "users" }
```

---

### Indexes

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/collection/{name}/index` | List indexes on a collection |
| `POST` | `/collection/{name}/index` | Create an index |
| `DELETE` | `/collection/{name}/index/{index_name}` | Drop an index by name |

**POST /collection/{name}/index**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `fields` | `[{field, direction}]` | required | Fields to index. `direction`: `1` ascending, `-1` descending |
| `name` | string | auto | Custom index name |
| `unique` | bool | `false` | Enforce unique values |
| `sparse` | bool | `false` | Only index documents that contain the field |
| `ttl` | int | `null` | Auto-expire documents after N seconds (`expireAfterSeconds`). Single-field only |
| `partial_filter_expression` | object | `null` | Only index documents matching this filter |

Simple index:
```json
{
  "fields": [{ "field": "email", "direction": 1 }],
  "unique": true
}
```

Compound index:
```json
{
  "fields": [
    { "field": "userId", "direction": 1 },
    { "field": "createdAt", "direction": -1 }
  ],
  "name": "userId_createdAt"
}
```

TTL index (expire documents 1 hour after `createdAt`):
```json
{
  "fields": [{ "field": "createdAt", "direction": 1 }],
  "ttl": 3600
}
```

Partial index:
```json
{
  "fields": [{ "field": "email", "direction": 1 }],
  "unique": true,
  "partial_filter_expression": { "status": "active" }
}
```

## monday Document DB limits

| Limit | Value |
|-------|-------|
| Max database size | 1 GiB per region |
| Reads | 50,000 / day |
| Writes | 20,000 / day |
| Deletes | 20,000 / day |

Limits reset at midnight Pacific Time. Multi-region apps have independent databases and limits per region.

## Interactive docs

Available at `http://localhost:8000/docs` when running locally.
