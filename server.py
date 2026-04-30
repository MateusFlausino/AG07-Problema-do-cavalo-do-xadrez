from __future__ import annotations

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from knight_ga import GAConfig, run_genetic_algorithm


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "sim", "on"}


def first_param(params: dict[str, list[str]], key: str, default: str | None = None) -> str | None:
    values = params.get(key)
    if not values:
        return default
    return values[0]


def parse_int(params: dict[str, list[str]], key: str, default: int) -> int:
    try:
        return int(first_param(params, key, str(default)) or default)
    except ValueError:
        return default


def parse_float(params: dict[str, list[str]], key: str, default: float) -> float:
    try:
        return float(first_param(params, key, str(default)) or default)
    except ValueError:
        return default


def config_from_query(query: str) -> GAConfig:
    params = parse_qs(query)
    raw_seed = first_param(params, "seed", "")
    seed = int(raw_seed) if raw_seed and raw_seed.lstrip("-").isdigit() else None

    return GAConfig(
        population_size=parse_int(params, "population", 240),
        generations=parse_int(params, "generations", 1000),
        tournament_size=parse_int(params, "tournament", 4),
        elite_size=parse_int(params, "elitism", 6),
        crossover_rate=parse_float(params, "crossover", 0.9),
        mutation_rate=parse_float(params, "mutationRate", 0.35),
        mutation_operator=first_param(params, "mutationOperator", "mixed") or "mixed",
        seed=seed,
        warm_start=parse_bool(first_param(params, "warmStart", "1"), True),
        report_every=parse_int(params, "reportEvery", 5),
    )


class KnightTourHandler(SimpleHTTPRequestHandler):
    server_version = "KnightTourGA/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def log_message(self, format: str, *args) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/api/health":
            self.send_json({"ok": True})
            return

        if parsed.path == "/api/run":
            self.stream_ga(parsed.query)
            return

        if parsed.path == "/":
            self.path = "/index.html"

        super().do_GET()

    def send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def stream_ga(self, query: str) -> None:
        config = config_from_query(query)

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()

        try:
            for payload in run_genetic_algorithm(config):
                event_name = "done" if payload["done"] else "progress"
                message = f"event: {event_name}\ndata: {json.dumps(payload)}\n\n"
                self.wfile.write(message.encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            return


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor do AG para o passeio do cavalo.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()

    httpd = ThreadingHTTPServer((args.host, args.port), KnightTourHandler)
    try:
        print(f"Servidor iniciado em http://{args.host}:{args.port}")
    except OSError:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor finalizado.")


if __name__ == "__main__":
    main()
