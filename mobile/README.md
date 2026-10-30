# ArecaVision Android

Native Kotlin + Jetpack Compose client for the existing ArecaVision FastAPI service.

## Run

Open this `mobile/` folder in Android Studio, sync Gradle, select a device, and run the `app` configuration. The default API URL points from an emulator to the host machine:

```text
http://10.0.2.2:8000/api/v1/
```

Start the existing backend on port 8000 before using diagnosis or history. For a physical Android device, set the Gradle property `ARECA_API_BASE_URL` to `http://<computer-LAN-IP>:8000/api/v1/` in your user-level Gradle properties or pass it as `-PARECA_API_BASE_URL=...`. The phone and computer must share a network, the backend must listen on `0.0.0.0`, and the firewall must allow port 8000. For local testing, use HTTP only on a trusted network.

The first implementation slice is diagnosis and scan history. See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for the full parity roadmap and backend contract.
