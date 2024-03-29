import logging

from algokit_utils import (
    Account,
    ApplicationClient,
    ApplicationSpecification,
    OnSchemaBreak,
    OnUpdate,
    OperationPerformed,
    TransferParameters,
    is_localnet,
    transfer,
)
from algosdk.util import algos_to_microalgos
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

from smart_contracts.membership import app as membership_app
from smart_contracts.nft_exchange import app as nft_exchange_app
from smart_contracts.enemy import app as enemy_app

logger = logging.getLogger(__name__)

# define contracts to build and/or deploy
contracts = [membership_app]


# define deployment behaviour based on supplied app spec
def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    app_spec: ApplicationSpecification,
    deployer: Account,
) -> None:
    is_local = is_localnet(algod_client)
    match app_spec.contract.name:
        case "MetaState":
            app_client = ApplicationClient(
                algod_client,
                app_spec,
                creator=deployer,
                indexer_client=indexer_client,
            )
            deploy_response = app_client.deploy(
                on_schema_break=OnSchemaBreak.ReplaceApp if is_local else OnSchemaBreak.Fail,
            )

            # if only just created, fund smart contract account
            if deploy_response.action_taken in [
                OperationPerformed.Create,
                OperationPerformed.Replace,
            ]:
                transfer_parameters = TransferParameters(
                    from_account=deployer,
                    to_address=app_client.app_address,
                    micro_algos=algos_to_microalgos(10),
                )
                logger.info(f"New app created, funding with {transfer_parameters.micro_algos}µ algos")
                transfer(algod_client, transfer_parameters)

                with open("../.env", "w+") as envfile:
                    envfile.write(f"METASTATE_APP_ID={app_client.app_id}")
                    envfile.write("\n")
                    envfile.write(f"METASTATE_APP_ADDRESS={app_client.app_address}")
                    
        case _:
            pass
