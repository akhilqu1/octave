from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "biomechanical-cost-engine" in data["features"]


def test_profiles():
    res = client.get("/api/profiles")
    assert res.status_code == 200
    data = res.json()
    assert len(data["presets"]) >= 4
    preset_ids = [p["id"] for p in data["presets"]]
    assert "arthritis_moderate" in preset_ids
    assert "tendonitis_flexor" in preset_ids


def test_chords_catalog():
    res_roots = client.get("/api/chords/roots")
    assert res_roots.status_code == 200
    assert "C" in res_roots.json()["primary"]
    assert "F#" in res_roots.json()["primary"]

    res_qual = client.get("/api/chords/qualities")
    assert res_qual.status_code == 200
    assert len(res_qual.json()) >= 7


def test_presets():
    res = client.get("/api/chords/presets")
    assert res.status_code == 200
    presets = res.json()
    assert len(presets) >= 4
    assert any(p["id"] == "barre_gauntlet" for p in presets)


def test_optimize_endpoint():
    payload = {
        "chords": ["F", "C", "G", "Am"],
        "profile_id": "arthritis_moderate"
    }
    res = client.post("/api/optimize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_chords"] == 4
    assert data["total_strain_reduction_pct"] > 0
    assert len(data["steps"]) == 4
    assert len(data["calculation_logs"]) > 0


def test_evaluate_chord_endpoint():
    res = client.get("/api/evaluate/chord/F?profile_id=arthritis_moderate")
    assert res.status_code == 200
    data = res.json()
    assert data["chord"] == "F"
    assert data["standard"]["voicing"]["has_barre"] is True
    assert len(data["alternatives"]) >= 1


def test_index_and_static_serving():
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert "octave" in res_index.text

    res_css = client.get("/static/css/styles.css")
    assert res_css.status_code == 200
    assert "--bg-canvas" in res_css.text

