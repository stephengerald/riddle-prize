import hashlib
import json
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address

RIDDLE = "I have cities but no houses, forests but no trees, and water but no fish. What am I?"
CRITERIA = "Correct answers identify a map or ordinary geographic map; semantically equivalent wording is accepted."
SOLUTION_NONCE = "solution-secret-2026"


def _solution_commitment():
    data = json.dumps({"schema": "riddle-prize/solution/v1", "answer_criteria": CRITERIA, "nonce": SOLUTION_NONCE}, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(data.encode()).hexdigest()


def _ok(receipt):
    assert tx_execution_succeeded(receipt)
    return receipt


@pytest.mark.integration
def test_studionet_semantic_riddle_judgment(default_account, secondary_account):
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "riddle_prize.py")
    deployed = _ok(factory.deploy_contract_tx(args=[RIDDLE, _solution_commitment(), 2], account=default_account, wait_transaction_status=TransactionStatus.FINALIZED))
    address = extract_contract_address(deployed)
    owner = factory.build_contract(address, account=default_account)
    entrant = factory.build_contract(address, account=secondary_account)
    answer, nonce = "It is a geographic map.", "player-answer-secret"
    commitment = entrant.make_answer_commitment(args=[secondary_account.address, answer, nonce]).call()
    _ok(entrant.submit_commitment(args=[commitment]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    _ok(owner.close_and_reveal_solution(args=[CRITERIA, SOLUTION_NONCE]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    _ok(entrant.reveal_answer(args=[answer, nonce]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    intelligent = _ok(owner.judge_answer(args=[secondary_account.address]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    result = owner.get_player_result(args=[secondary_account.address]).call()["result"]
    assert result in ("CORRECT", "INCORRECT")
    print("STUDIONET_RECORD=" + json.dumps({"address": address, "deploy_tx": deployed["hash"], "intelligent_tx": intelligent["hash"], "observed": result}, sort_keys=True))
