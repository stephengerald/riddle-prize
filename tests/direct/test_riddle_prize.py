from pathlib import Path
import hashlib
import json

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "riddle_prize.py"
SDK = "v0.2.16"
PROMPT = "independent semantic riddle judge"
RIDDLE = "I have cities but no houses, forests but no trees, and water but no fish. What am I?"
CRITERIA = "Correct answers identify a map or an ordinary geographic map; semantically equivalent wording is accepted."
SOLUTION_NONCE = "solution-secret-2026"


def solution_commitment():
    payload = {"schema": "riddle-prize/solution/v1", "answer_criteria": CRITERIA, "nonce": SOLUTION_NONCE}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


def deploy(vm, direct_deploy, alice):
    vm.sender = alice
    return direct_deploy(str(CONTRACT), RIDDLE, solution_commitment(), 2, sdk_version=SDK)


def test_commit_reveal_semantic_winner(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    answer = "It is a geographic map."
    nonce = "player-answer-secret"
    player = "0x" + direct_bob.hex()
    commitment = contract.make_answer_commitment(player, answer, nonce)
    direct_vm.sender = direct_bob
    contract.submit_commitment(commitment)
    direct_vm.sender = direct_alice
    contract.close_and_reveal_solution(CRITERIA, SOLUTION_NONCE)
    direct_vm.sender = direct_bob
    contract.reveal_answer(answer, nonce)
    direct_vm.mock_llm(PROMPT, json.dumps({"result": "CORRECT"}))
    contract.judge_answer(player)
    assert contract.get_state()["winner_count"] == 1
    assert contract.get_player_result(player)["result"] == "CORRECT"
    assert contract.get_winner(0) == player.lower()
    leader = direct_vm._captured_validators[-1][0]
    assert direct_vm.run_validator(leader_result=leader) is True


def test_player_commitment_binds_answer_and_nonce(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    player = "0x" + direct_bob.hex()
    commitment = contract.make_answer_commitment(player, "A geographic map", "correct-player-nonce")
    direct_vm.sender = direct_bob
    contract.submit_commitment(commitment)
    direct_vm.sender = direct_alice
    contract.close_and_reveal_solution(CRITERIA, SOLUTION_NONCE)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("answer_commitment_mismatch"):
        contract.reveal_answer("A geographic map", "wrong-player-nonce")


def test_creator_authority_and_bad_model_result_fail_closed(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    player = "0x" + direct_bob.hex()
    answer = "A map"
    nonce = "player-map-secret"
    direct_vm.sender = direct_bob
    contract.submit_commitment(contract.make_answer_commitment(player, answer, nonce))
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("only_creator"):
        contract.close_and_reveal_solution(CRITERIA, SOLUTION_NONCE)
    direct_vm.sender = direct_alice
    contract.close_and_reveal_solution(CRITERIA, SOLUTION_NONCE)
    direct_vm.sender = direct_bob
    contract.reveal_answer(answer, nonce)
    direct_vm.mock_llm(PROMPT, json.dumps({"result": "MAYBE"}))
    with direct_vm.expect_revert("invalid_result"):
        contract.judge_answer(player)
    assert contract.get_player_result(player)["result"] == "NONE"
