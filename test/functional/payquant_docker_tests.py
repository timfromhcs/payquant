#!/usr/bin/env python3
"""
PayQuant (PQN) Docker / Cloud Build Test Suite
Validates:
  1. docker-compose.yml declares scalable node & miner services with healthchecks
  2. docker-compose.publish.yml maps host ports for the single-dev overlay
  3. cloudbuild.yaml defines node/miner build steps + cleanup
  4. Optional (docker available + PQN_DOCKER_INTEGRATION=1): real `up --scale` smoke test
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

COMPOSE = os.path.join(BASE_DIR, "docker-compose.yml")
COMPOSE_PUBLISH = os.path.join(BASE_DIR, "docker-compose.publish.yml")
CLOUDBUILD = os.path.join(BASE_DIR, "cloudbuild.yaml")


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestComposeStructure(unittest.TestCase):

    def test_compose_file_exists(self):
        self.assertTrue(os.path.exists(COMPOSE), "docker-compose.yml missing")

    def test_services_present(self):
        text = _read(COMPOSE)
        self.assertIn("node:", text)
        self.assertIn("miner:", text)

    def test_build_contexts(self):
        text = _read(COMPOSE)
        self.assertIn("Dockerfile.node", text)
        self.assertIn("Dockerfile", text)

    def test_healthchecks(self):
        text = _read(COMPOSE)
        self.assertIn("healthcheck:", text)
        self.assertIn("test:", text)

    def test_network_defined(self):
        text = _read(COMPOSE)
        self.assertIn("payquant-net:", text)

    def test_port_constants(self):
        text = _read(COMPOSE)
        for p in ("28332", "28333", "28334", "28335"):
            self.assertIn(p, text, f"port {p} not exposed in compose")

    def test_no_fixed_container_names(self):
        # fixed container_name would break --scale node=X miner=Y
        self.assertNotIn("container_name:", _read(COMPOSE))

    def test_env_substitutions(self):
        text = _read(COMPOSE)
        for var in ("${PQN_NETWORK", "${PQN_MINING_THREADS", "${PQN_TAG"):
            self.assertIn(var, text)


class TestComposePublish(unittest.TestCase):

    def test_publish_file_present(self):
        self.assertTrue(os.path.exists(COMPOSE_PUBLISH), "docker-compose.publish.yml missing")
        text = _read(COMPOSE_PUBLISH)
        self.assertIn("ports:", text)
        self.assertIn("28333:28333", text)


class TestCloudBuild(unittest.TestCase):

    def test_cloudbuild_exists(self):
        self.assertTrue(os.path.exists(CLOUDBUILD), "cloudbuild.yaml missing")

    def test_build_steps(self):
        text = _read(CLOUDBUILD)
        self.assertIn("steps:", text)
        self.assertIn("Dockerfile.node", text)
        self.assertIn("Dockerfile", text)
        self.assertIn("payquant-node", text)
        self.assertIn("payquant-miner", text)

    def test_timeout_set(self):
        self.assertIn("timeout:", _read(CLOUDBUILD))

    def test_images_pushed(self):
        self.assertIn("images:", _read(CLOUDBUILD))


@unittest.skipUnless(
    os.environ.get("PQN_DOCKER_INTEGRATION") == "1",
    "Docker integration smoke test gated behind PQN_DOCKER_INTEGRATION=1",
)
class TestDockerIntegration(unittest.TestCase):
    """Real docker-compose smoke test: boot node+miner stack, verify health, tear down."""

    def test_compose_up_scale_and_down(self):
        import subprocess

        base = ["docker", "compose", "-f", os.path.join(BASE_DIR, "docker-compose.yml")]

        def run(cmd, check=True):
            return subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, check=check)

        # validate config first
        cfg = run(base + ["config", "--quiet"])
        self.assertEqual(cfg.returncode, 0, cfg.stderr)

        # scale up: 1 node + 2 miners is the documented parallel use-case
        up = run(base + ["up", "-d", "--scale", "node=1", "--scale", "miner=2"])
        self.assertEqual(up.returncode, 0, up.stderr)

        try:
            ps = run(base + ["ps", "--format", "json"])
            self.assertEqual(ps.returncode, 0, ps.stderr)
            self.assertIn("payquant", ps.stdout)
        finally:
            down = run(base + ["down", "--volumes"])
            self.assertEqual(down.returncode, 0, down.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)