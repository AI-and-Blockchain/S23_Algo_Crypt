from beaker.sandbox import (
    get_algod_client,
    get_indexer_client,
)

from beaker.client import ApplicationClient

from algosdk.transaction import PaymentTxn
from crypt.blockchain.smart_contracts.membership import app as membership_app

from dotenv import load_dotenv

import os

load_dotenv("./crypt/.env")

algod_client = get_algod_client()
indexer_client = get_indexer_client()


cards = [
    ("phys_attack", "attack w/ strength", "ipfs:/"),
    ("phys_defense", "defend w/ strength", "ipfs:/"),
    ("magic_attack", "attack w/ magic", "ipfs:/"),
    ("magic_defense", "defend w/ magic", "ipfs:/"),
    ("dodge", "defend w/ dexterity", "ipfs:/"),
]

app_client = ApplicationClient(
    client=algod_client,
    app=membership_app,
    app_id=int(os.getenv("METASTATE_APP_ID"))
)

creator = app_client.get_global_state()["governor"]

txn = PaymentTxn(
    sender=creator,
    sp=algod_client.suggested_params(),
    receiver=os.getenv("METASTATE_APP_ADDRESS"),
    amt=1000
)

app_client.call(
    "bootstrap",
    seed=txn,
    card_list=cards
)
