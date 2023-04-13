from beaker.sandbox import get_indexer_client
import json

indexer = get_indexer_client()

assets = indexer.search_assets()

with open("assets.json", "w+") as assets_file:
    assets_file.write(json.dumps(assets))

txns = indexer.search_transactions()

with open("txns.json", "w+") as txns_file:
    txns_file.write(json.dumps(txns))
