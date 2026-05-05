
`lifespan` in FastAPI is a **startup/shutdown lifecycle hook**.


means:
- code **before `yield`** = startup
- code **after `yield`** = shutdown

---

## What is commonly put in `lifespan`

Typical things:

### Startup
- connect to databases
- initialize caches
- load ML models
- warm up clients
- create shared resources
- verify config/env values
- start background services

### Shutdown
- close database connections
- stop background tasks
- flush logs
- release file handles
- clean up temporary resources

---

## What should **not** usually go there
Usually **not**:
- route definitions
- `app.include_router(...)`
- `setup_logger()`
- simple module imports
- static constants

Those belong at module level or inside `create_app()`.

---


## Rule of thumb
Use `lifespan` for **resources that need setup and cleanup**.

If something only needs to be defined once and used everywhere, it usually belongs:
- at the top of the file, or
- inside `create_app()`
