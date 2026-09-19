from fastapi.testclient import TestClient
from proofops_api.app import app

client = TestClient(app)


def test_full_governed_flow_and_rollback_invalidation() -> None:
    state = client.post("/api/demo/reset").json()
    assert state["phase"] == "detected"
    assert state["audit"]["valid"] is True

    for _ in range(7):
        state = client.post("/api/demo/investigate/advance").json()
    assert state["phase"] == "ready_to_propose"
    assert all(agent["status"] == "complete" for agent in state["agents"])

    state = client.post("/api/demo/propose").json()
    proposal_hash = state["proposal"]["record_sha256"]
    state = client.post("/api/demo/approve", json={
        "approver": "总管-01", "proposal_hash": proposal_hash, "acknowledged": True,
    }).json()
    assert state["phase"] == "approved"

    state = client.post("/api/demo/execute").json()
    execution_hash = state["execution"]["record_sha256"]
    assert state["twin"]["backup_chiller"] == "running"

    state = client.post("/api/demo/verify").json()
    assert state["verification"]["status"] == "passed"

    state = client.post("/api/demo/rollback", json={
        "approver": "总管-01", "execution_hash": execution_hash, "confirmed": True,
    }).json()
    assert state["phase"] == "rolled_back"
    assert state["verification"]["status"] == "invalidated"
    assert state["audit"]["valid"] is True


def test_approval_must_bind_exact_proposal_hash() -> None:
    client.post("/api/demo/reset")
    for _ in range(7):
        client.post("/api/demo/investigate/advance")
    client.post("/api/demo/propose")
    response = client.post("/api/demo/approve", json={
        "approver": "总管-01", "proposal_hash": "0" * 64, "acknowledged": True,
    })
    assert response.status_code == 409
