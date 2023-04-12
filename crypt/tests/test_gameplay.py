from crypt.chain_interaction.gameplay import submit_turn
from crypt.blockchain.smart_contracts.enemy import app as enemy_app
import crypt.blockchain.smart_contracts.enemy as enemy
import pytest

from algosdk.v2client.algod import AlgodClient
from algokit_utils import (
    ApplicationClient,
    get_account,
)

from beaker.sandbox import client, consts, sandbox


@pytest.fixture(autouse=True)
def around():
    # create accounts
    accts = sandbox.get_accounts()

    creator = accts.pop()

    enemy_client = ApplicationClient(
        sandbox.get_algod_client(),
        app_spec=enemy_app,
        signer=creator.signer
    )

    app_id, app_addr, txid = enemy_client.create()

    enemy_client.call(
        enemy.bootstrap,
        
    )

    yield app_id, app_addr, accts

    # delete app
    enemy_client.delete()



def test_submit_turn():

    app_id, app_addr, accts = around()

    player = accts.pop()

    # submit turn
    gs = submit_turn(
        sandbox.get_algod_client(),
        app_id,
        player.address,
        (
            ("attack", "strength"),
            ("attack", "strength"),
            ("attack", "strength"),
        ),
    )

    # get state
    state = enemy_client.get_state()

    assert state["player_hp"] == 0
    assert state["enemy_hp"] == 0
    assert state["finished"] == True
