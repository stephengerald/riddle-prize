from __future__ import annotations
import hashlib
import json
from pathlib import Path
from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address

PROMPT = "independent semantic riddle judge"
RIDDLE = "I have cities but no houses, forests but no trees, and water but no fish. What am I?"
CRITERIA = "Correct answers identify a map or ordinary geographic map; semantically equivalent wording is accepted."
SOLUTION_NONCE = "solution-secret-2026"


def solution_commitment():
    data = json.dumps({"schema": "riddle-prize/solution/v1", "answer_criteria": CRITERIA, "nonce": SOLUTION_NONCE}, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(data.encode()).hexdigest()


def context():
    validators = get_validator_factory().batch_create_mock_validators(5, mock_llm_response={"nondet_exec_prompt": {PROMPT: json.dumps({"result": "CORRECT"})}})
    return {"validators": [validator.to_dict() for validator in validators]}


def ok(receipt):
    assert tx_execution_succeeded(receipt)


def test_five_validator_riddle_winner():
    creator, player = create_accounts(2)
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "riddle_prize.py")
    deployed = factory.deploy_contract_tx(args=[RIDDLE, solution_commitment(), 2], account=creator, wait_transaction_status=TransactionStatus.FINALIZED)
    ok(deployed)
    address = extract_contract_address(deployed)
    owner = factory.build_contract(address, account=creator)
    entrant = factory.build_contract(address, account=player)
    answer = "It is a geographic map."
    nonce = "player-answer-secret"
    commitment = entrant.make_answer_commitment(args=[player.address, answer, nonce]).call()
    ok(entrant.submit_commitment(args=[commitment]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(owner.close_and_reveal_solution(args=[CRITERIA, SOLUTION_NONCE]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(entrant.reveal_answer(args=[answer, nonce]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(owner.judge_answer(args=[player.address]).transact(transaction_context=context(), wait_transaction_status=TransactionStatus.FINALIZED))
    assert owner.get_state(args=[]).call()["winner_count"] == 1
