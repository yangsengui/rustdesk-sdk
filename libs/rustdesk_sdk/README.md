# RustDesk SDK (DLL)

This crate provides a minimal SDK layer over RustDesk for embedding in other languages.
It builds a dynamic library (cdylib) and exposes a C ABI.

## Version

- SDK version: 0.1.0
- RustDesk core version: 1.4.1 (from root Cargo.toml)

## Build

```bash
cargo build -p rustdesk_sdk --release
```

Artifacts:
- Windows: `target/release/rustdesk_sdk.dll`
- macOS: `target/release/librustdesk_sdk.dylib`
- Linux: `target/release/librustdesk_sdk.so`

## Usage (FFI)

All functions are `extern "C"`. Any function that returns `char*` allocates a C string
and **must** be freed with `rd_free_c_string`.

Recommended startup flow:
1. `rd_start_server_safe()`
2. Keep host process alive

## API

### Lifecycle
- `bool rd_global_init()`
  - Initialize RustDesk global state.
- `bool rd_start_server_safe()`
  - Safe startup (same as example):
    - `global_init()` -> if not `is_cm` -> `start_server(false, false)`
    - Clears `stop-service` option before start.
- `bool rd_stop_server()`
  - Sets `stop-service = "Y"` and restarts mediator to stop service.
- `bool rd_is_server_running()`
  - SDK-side running flag.

### Identity & Auth
- `char* rd_get_id()`
  - Returns device ID.
- `char* rd_get_temporary_password()`
  - Returns temporary password.
- `bool rd_update_temporary_password()`
  - Regenerates temporary password.
- `char* rd_get_permanent_password()`
  - Returns permanent password (may be empty).
- `bool rd_set_permanent_password(const char* password)`
  - Sets permanent password.

### Options & Config
- `char* rd_get_option(const char* key)`
  - Returns a single option by key.
- `bool rd_set_option(const char* key, const char* value)`
  - Sets an option by key.
- `char* rd_get_all_options()`
  - Returns JSON of all options.

Common network keys:
- `custom-rendezvous-server` (ID server)
- `relay-server` (relay server)
- `api-server`
- `key`

### Connectivity
- `char* rd_get_rendezvous_server(uint64_t ms_timeout)`
  - Returns JSON: `{ "server": "...", "servers": [...], "is_public": true/false }`
- `int32_t rd_get_nat_type(uint64_t ms_timeout)`
  - Returns NAT type value or -1 on error.
- `bool rd_test_rendezvous_server()`
  - Triggers rendezvous server test.

### Memory
- `void rd_free_c_string(char* s)`
  - Frees strings returned by SDK.

## Example (Python)

See `examples/rustdesk_sdk_tkinter.py`.

## Notes

- Keep the host process running; the service runs in background threads.
- If you set options such as `relay-server`, restart the server to apply them:
  - `rd_stop_server()` then `rd_start_server_safe()`
