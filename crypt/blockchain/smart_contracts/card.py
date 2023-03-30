"""Contract for signing up for the game. Will mint the starting deck and transfer it to the player.

Fields:
    description: str (Global)

    starting_deck: List[str] (Global)
        List of card names to be minted for the player.

Methods:
    signup: () -> ()
        Mints the starting deck and transfers it to the player.

    update_description: (str) -> ()
        Updates the description of the contract.

    update_starting_deck: (List[str]) -> ()
        Updates the starting deck of the contract.
"""

from beaker import *
from pyteal import *

class Card(abi.NamedTuple):
    name: abi.Field[abi.String]
    image_uri: abi.Field[abi.String]
    asset_id: abi.Field[abi.Uint64]
    
class CardVolume(abi.NamedTuple):
    card: abi.Field[Card]
    volume: abi.Field[abi.Uint64]

class CardMintingState:
    governor: GlobalStateValue(
        stack_type=abi.Address,
        descr="Governor of the contract",
        default=Global.creator_address(),
    )
    all_cards: GlobalStateValue(
        stack_type=abi.DynamicArray[CardVolume],
        descr="All cards in the game",
        default=abi.DynamicArray[CardVolume](),
    )
    starting_deck: GlobalStateValue(
        stack_type=abi.StaticArray[Card, 30],
        descr="Starting deck of the player",
        default=abi.StaticArray[Card, 30](),
    )
    description: GlobalStateValue(
        stack_type=abi.String,
        descr="Description of the contract",
        default="Algo Crypt Card Minting Contract",
    )


card_minter = Application("Algocrypt Card Minting Contract", CardMintingState)

# Methods

@card_minter.create
def create() -> Expr:
    return card_minter.initialize_global_state()

@card_minter.external(authorize=Authorize.only(card_minter.state.governor))
def bootstrap(txn: abi.PaymentTransaction, assets: abi.DynamicArray[abi.Tuple3[abi.String, abi.Uint64, abi.String]]) -> Expr:
    i = ScratchVar(TealType.uint64)
    return Seq(
        For(
            i.store(Int(0)),
            i.load() < Len(assets),
            i.store(i.load() + Int(1)),
        ).Do(
            InnerTxnBuilder.Execute(
                {
                    TxnField.type_enum: TxnType.AssetConfig,
                    TxnField.config_asset_name: Concat(
                        Bytes("CRPT-"), assets[i.load()][0]
                    ),
                    TxnField.config_asset_unit_name: Bytes("CRPT"),
                    TxnField.config_asset_total: assets[i.load()][1],
                    TxnField.config_asset_decimals: Int(0),
                    TxnField.config_asset_manager: Global.current_application_address(),
                    TxnField.config_asset_reserve: Global.current_application_address(),
                    TxnField.fee: Int(0),
                    TxnField.config_asset_url: assets[i.load()][2],
                }
            ),
            aid := InnerTxn.created_asset_id(),
            # add card to all_cards
            card_minter.state.all_cards.set(
                card_minter.state.all_cards.get()
                + abi.DynamicArray[CardVolume](
                    [
                        CardVolume(
                            Card(
                                name=assets[i.load()][0],
                                image_uri=assets[i.load()][2],
                                asset_id=aid,
                            ),
                            volume=assets[i.load()][1],
                        )
                    ]
                )
            ),
        )
    )

@card_minter.external(authorize=Authorize.only(card_minter.state.governor))
def update_governor(new_governor: abi.Account) -> Expr:
    return card_minter.state.governor.set(new_governor.address())

@card_minter.external(authorize=Authorize.only(card_minter.state.governor))
def update_description(new_description: abi.String) -> Expr:
    return card_minter.state.description.set(new_description)

@card_minter.external(authorize=Authorize.only(card_minter.state.governor))
def update_starting_deck(new_starting_deck: abi.Array[abi.String]) -> Expr:
    return card_minter.state.starting_deck.set(new_starting_deck)

@Subroutine(TealType.none)
def transfer_asset(receiver: Expr, asset_id: Expr, amount: Expr) -> Expr:
    return Seq(
            # reduce volume of card
            card_minter.state.all_cards.set(
                card_minter.state.all_cards.get().map(
                    lambda cv: If(
                        cv.card.asset_id == asset_id,
                        cv.volume.set(cv.volume - amount),
                        cv,
                    )
                )
            ),
            InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.asset_receiver: receiver,
                TxnField.asset_amount: amount,
                TxnField.xfer_asset: asset_id,
                TxnField.fee: Int(0),
            }
        )
    )

@card_minter.external
def signup() -> Expr:
    i = ScratchVar(TealType.uint64)
    return Seq(
        For(
            i.store(Int(0)),
            i.load() < Len(card_minter.state.starting_deck.get()),
            i.store(i.load() + Int(1)),
        ).Do(
            transfer_asset(
                Global.sender_address(),
                card_minter.state.starting_deck.get()[i.load()].asset_id,
                Int(1),
            )
        )
    )

@card_minter.external(authorize=Authorize.only(card_minter.state.governor))
def add_card(name: abi.String, image_uri: abi.String, volume: abi.Uint64) -> Expr:
    return Seq(
        InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.AssetConfig,
                TxnField.config_asset_name: Concat(
                    Bytes("CRPT-"), name
                ),
                TxnField.config_asset_unit_name: Bytes("CRPT"),
                TxnField.config_asset_total: volume,
                TxnField.config_asset_decimals: Int(0),
                TxnField.config_asset_manager: Global.current_application_address(),
                TxnField.config_asset_reserve: Global.current_application_address(),
                TxnField.fee: Int(0),
                TxnField.config_asset_url: image_uri,
            }
        ),
        aid := InnerTxn.created_asset_id(),
        # add card to all_cards
        card_minter.state.all_cards.set(
            card_minter.state.all_cards.get()
            + abi.DynamicArray[CardVolume](
                [
                    CardVolume(
                        Card(
                            name=name,
                            image_uri=image_uri,
                            asset_id=aid,
                        ),
                        volume=volume,
                    )
                ]
            )
        ),
    )

@card_minter.external(authorize=Authorize.only(card_minter.state.governor))
def add_cards(cards: abi.DynamicArray[abi.Tuple3[abi.String, abi.Uint64, abi.String]]) -> Expr:
    i = ScratchVar(TealType.uint64)
    return Seq(
        For(
            i.store(Int(0)),
            i.load() < Len(cards),
            i.store(i.load() + Int(1)),
        ).Do(
            InnerTxnBuilder.Execute(
                {
                    TxnField.type_enum: TxnType.AssetConfig,
                    TxnField.config_asset_name: Concat(
                        Bytes("CRPT-"), cards[i.load()][0]
                    ),
                    TxnField.config_asset_unit_name: Bytes("CRPT"),
                    TxnField.config_asset_total: cards[i.load()][1],
                    TxnField.config_asset_decimals: Int(0),
                    TxnField.config_asset_manager: Global.current_application_address(),
                    TxnField.config_asset_reserve: Global.current_application_address(),
                    TxnField.fee: Int(0),
                    TxnField.config_asset_url: cards[i.load()][2],
                }
            ),
            aid := InnerTxn.created_asset_id(),
            # add card to all_cards
            card_minter.state.all_cards.set(
                card_minter.state.all_cards.get()
                + abi.DynamicArray[CardVolume](
                    [
                        CardVolume(
                            Card(
                                name=cards[i.load()][0],
                                image_uri=cards[i.load()][2],
                                asset_id=aid,
                            ),
                            volume=cards[i.load()][1],
                        )
                    ]
                )
            ),
        )
    )

@card_minter.external(authorize=Authorize.only(card_minter.state.governor))
def remove_card(asset_id: abi.Uint64) -> Expr:
    return Seq(
        # remove card from all_cards
        card_minter.state.all_cards.set(
            card_minter.state.all_cards.get().filter(
                lambda cv: cv.card.asset_id != asset_id
            )
        ),
    )

@card_minter.external(authorize=Authorize.only(card_minter.state.governor))
def mint_card_to_enemy(asset_id: abi.Uint64, enemy: abi.Address, amount: abi.Uint64) -> Expr:
    return Seq(
        # reduce volume of card
        card_minter.state.all_cards.set(
            card_minter.state.all_cards.get().map(
                lambda cv: If(
                    cv.card.asset_id == asset_id,
                    cv.volume.set(cv.volume - Int(1)),
                    cv,
                )
            )
        ),
        InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.asset_receiver: enemy,
                TxnField.asset_amount: amount,
                TxnField.xfer_asset: asset_id,
                TxnField.fee: Int(0),
            }
        ),
    )

client = client.ApplicationClient(
    client=sandbox.get_algod_client(),
    app=card_minter,
    signer=sandbox.get_accounts().pop().signer
)

app_id, app_addr, txid = client.create()
print(
    f"""Deployed app in txid {txid}
    App ID: {app_id} 
    Address: {app_addr} 
"""
)
