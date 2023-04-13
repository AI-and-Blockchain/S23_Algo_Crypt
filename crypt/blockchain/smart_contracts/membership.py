"""Smart Contract to track membership and meta-state of the game.

Named Tuples and Mappings

    Card
        name: str
        desc: str

    Address -> MembershipRecord
        intelligence: int
        strength: int
        dexterity: int
        library: card_asset_id: int -> Card
    card_descriptions: card_name: str -> card_description: str

"""

import beaker as bk
import pyteal as pt

from beaker.lib.storage import BoxList, BoxMapping


class Card(pt.abi.NamedTuple):
    name: pt.abi.Field[pt.abi.String]
    desc: pt.abi.Field[pt.abi.String]
    url: pt.abi.Field[pt.abi.String]


class MembershipRecord(pt.abi.NamedTuple):
    intelligence: pt.abi.Field[pt.abi.Uint8]
    strength: pt.abi.Field[pt.abi.Uint8]
    dexterity: pt.abi.Field[pt.abi.Uint8]
    library = BoxList(pt.abi.Uint64, 1000)  # card_asset_id
    # TODO: add deck mapping


class MembershipState:
    governor = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        default=pt.Global.creator_address(),
        descr="Address of the governor of the game.",
    )

    n_cards = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Number of card types in the game.",
    )

    def __init__(self, *, membership_record: type[pt.abi.BaseType], card_type: type[pt.abi.BaseType]):
        self.card_bank = BoxMapping(pt.abi.Uint64, pt.abi.Uint64)  # card_asset_id -> card_count
        self.membership = BoxMapping(pt.abi.Address, membership_record)  # address -> membership_record
        self.all_cards = BoxMapping(pt.abi.Uint64, card_type)  # card_asset_id -> card
        self.card_ids = BoxList(pt.abi.Uint64, 1000, "card_ids")  # card_asset_id
        self.starting_deck = BoxList(pt.abi.Uint64, 30, "starting_deck")  # card_asset_id


app = bk.Application(
    name="Algo Crypt Meta State",
    state=MembershipState(
        membership_record=MembershipRecord,
        card_type=Card,
    ),
)

@app.create
def create():
    return app.initialize_global_state()

@app.external(authorize=bk.Authorize.only_creator())
def bootstrap(
    seed: pt.abi.PaymentTransaction,
    card_list: pt.abi.DynamicArray[pt.abi.Tuple3[pt.abi.String, pt.abi.String, pt.abi.String]],
) -> pt.Expr:
    """Bootstrap the game with a list of cards.

    Args:
        seed (pt.abi.PaymentTransaction): seeded transaction
        card_list (pt.abi.Array[
            pt.abi.Tuple3[pt.abi.String, pt.abi.String, pt.abi.String]
            ]): List of cards (name, description, url)

    Returns:
        pt.Expr: pyteal expression
    """
    n_cards = pt.ScratchVar(pt.TealType.uint64)
    i = pt.ScratchVar(pt.TealType.uint64)
    created_asset_id = pt.ScratchVar(pt.TealType.uint64)
    return pt.Seq(
        pt.Assert(
            seed.get().receiver() == pt.Global.current_application_address(),
            comment="Seed transaction must be sent to the application address.",
        ),
        n_cards.store(card_list.length()),
        pt.For(
            i.store(pt.Int(0)),
            i.load() < n_cards.load(),
            i.store(i.load() + pt.Int(1)),
        ).Do(
            pt.Seq(
                (card_details := pt.abi.make(pt.abi.Tuple3[pt.abi.String, pt.abi.String, pt.abi.String])).set(
                    pt.abi.String(), pt.abi.String(), pt.abi.String()
                ),
                card_list[i.load()].store_into(card_details),
                (card_name := pt.abi.make(pt.abi.String)).set(pt.abi.String()),
                (card_desc := pt.abi.make(pt.abi.String)).set(pt.abi.String()),
                (card_url := pt.abi.make(pt.abi.String)).set(pt.abi.String()),
                card_details[0].store_into(card_name),
                card_details[1].store_into(card_desc),
                card_details[2].store_into(card_url),
                pt.InnerTxnBuilder.Execute(
                    {
                        pt.TxnField.type_enum: pt.TxnType.AssetConfig,
                        pt.TxnField.config_asset_name: card_name.get(),
                        pt.TxnField.config_asset_unit_name: pt.Bytes("CRPT-Card-{i}"),
                        pt.TxnField.config_asset_url: card_url.get(),
                        pt.TxnField.config_asset_total: pt.Int(10000),
                        pt.TxnField.config_asset_decimals: pt.Int(0),
                        pt.TxnField.config_asset_default_frozen: pt.Int(0),
                        pt.TxnField.config_asset_manager: pt.Global.current_application_address(),
                        pt.TxnField.config_asset_reserve: pt.Global.current_application_address(),
                        pt.TxnField.config_asset_freeze: pt.Global.current_application_address(),
                        pt.TxnField.config_asset_clawback: pt.Global.current_application_address(),
                        pt.TxnField.fee: pt.Int(0),
                    }
                ),
                (card_obj := Card()).set(card_name, card_desc, card_url),
                created_asset_id.store(pt.InnerTxn.created_asset_id()),
                (asset_uint := pt.abi.make(pt.abi.Uint64)).set(created_asset_id.load()),
                app.state.all_cards[pt.Itob(pt.InnerTxn.created_asset_id())].set(card_obj),
                app.state.card_ids[app.state.n_cards].set(asset_uint),
                app.state.card_bank[pt.Itob(pt.InnerTxn.created_asset_id())].set(pt.Itob(pt.Int(10000))),
                app.state.n_cards.set(app.state.n_cards + pt.Int(1)),
            ),
        ),
    )


@app.external(authorize=bk.Authorize.only_creator())
def set_starting_deck(card_list: pt.abi.DynamicArray[pt.abi.Uint64]) -> pt.Expr:
    """Set the starting deck for new members.

    Args:
        card_list (pt.abi.Array[
            pt.abi.Tuple2[pt.abi.Uint64, pt.abi.Uint64]
            ]): List of cards (card_asset_id, card_count)

    Returns:
        pt.Expr: pyteal expression
    """
    i = pt.ScratchVar(pt.TealType.uint64)
    return pt.Seq(
        pt.Assert(
            card_list.length() == pt.Int(30),
            comment="Starting deck must have 30 cards.",
        ),
        pt.For(
            i.store(pt.Int(0)),
            i.load() < card_list.length(),
            i.store(i.load() + pt.Int(1)),
        ).Do(
            card_list[i.load()].use(app.state.starting_deck[i.load()].set),
        ),
    )


@app.external(authorize=bk.Authorize.only_creator())
def add_card(card_name: pt.abi.String, card_desc: pt.abi.String, card_url: pt.abi.String) -> pt.Expr:
    """Add a new card to the game.

    Args:
        card_name (pt.abi.String): Name of the card
        card_desc (pt.abi.String): Description of the card
        card_url (pt.abi.String): URL of the card

    Returns:
        pt.Expr: pyteal expression
    """
    return pt.Seq(
        pt.Assert(
            app.state.n_cards < pt.Int(1000),
            comment="Cannot add more than 1000 cards.",
        ),
        pt.InnerTxnBuilder.Execute(
            {
                pt.TxnField.type_enum: pt.TxnType.AssetConfig,
                pt.TxnField.config_asset_name: card_name.get(),
                pt.TxnField.config_asset_unit_name: pt.Bytes("CRPT-Card-{app.state.n_cards}"),
                pt.TxnField.config_asset_total: pt.Int(10000),
                pt.TxnField.config_asset_decimals: pt.Int(0),
                pt.TxnField.config_asset_default_frozen: pt.Int(0),
                pt.TxnField.config_asset_manager: pt.Global.current_application_address(),
                pt.TxnField.config_asset_reserve: pt.Global.current_application_address(),
                pt.TxnField.config_asset_freeze: pt.Global.current_application_address(),
                pt.TxnField.config_asset_clawback: pt.Global.current_application_address(),
                pt.TxnField.fee: pt.Int(0),
            }
        ),
        (card_obj := Card()).set(card_name, card_desc, card_url),
        (asset_uint := pt.abi.make(pt.abi.Uint64)).set(pt.InnerTxn.created_asset_id()),
        app.state.all_cards[pt.Itob(pt.InnerTxn.created_asset_id())].set(card_obj),
        app.state.card_ids[app.state.n_cards].set(asset_uint),
        app.state.card_bank[pt.Itob(pt.InnerTxn.created_asset_id())].set(pt.Itob(pt.Int(10000))),
        app.state.n_cards.set(app.state.n_cards + pt.Int(1)),
    )


@app.external
def get_card(card_id: pt.abi.Uint64, *, output: Card) -> pt.Expr:
    """Get the card details.

    Args:
        card_id (pt.abi.Uint64): Card ID

    Returns:
        pt.Expr: pyteal expression
    """
    return pt.Seq(
        pt.Assert(
            app.state.all_cards[card_id].exists(),
            comment="Card does not exist.",
        ),
        (card := Card()).set(pt.abi.String(), pt.abi.String(), pt.abi.String()),
        app.state.all_cards[card_id].store_into(card),
        (card_name := pt.abi.String()).set(card[0]),
        (card_desc := pt.abi.String()).set(card[1]),
        (card_url := pt.abi.String()).set(card[2]),
        output.set(card_name, card_desc, card_url),
    )


@app.external
def get_card_aid(index: pt.abi.Uint64, *, output: pt.abi.Uint64) -> pt.Expr:
    """Get asset id for a card in the all_cards array.

    Args:
        index (pt.abi.Uint64): Index of the card

    Returns:
        pt.Expr: pyteal expression
    """
    return pt.Seq(
        pt.Assert(
            index.get() < app.state.n_cards.get(),
            comment="Index out of range.",
        ),
        pt.Assert(
            index.get() < app.state.n_cards.get(),
            comment="Card does not exist.",
        ),
        pt.Assert(
            app.state.n_cards > pt.Int(0),
            comment="No cards exist.",
        ),
        app.state.card_ids[index.get()].store_into(output),
    )


@app.external
def get_card_count(card_id: pt.abi.Uint64, *, output: pt.abi.Uint64) -> pt.Expr:
    """Get the card count.

    Args:
        card_id (pt.abi.Uint64): Card ID

    Returns:
        pt.Expr: pyteal expression
    """
    return pt.Seq(
        pt.Assert(
            app.state.card_bank[card_id].exists(),
            comment="Card does not exist.",
        ),
        app.state.card_bank[card_id].store_into(output),
    )


@pt.Subroutine(pt.TealType.none)
def transfer_starting_deck(recipient: pt.abi.Address) -> pt.Expr:
    """Transfer the starting deck to a new member.

    Args:
        recipient (pt.abi.Address): Address of the recipient

    Returns:
        pt.Expr: pyteal expression
    """
    i = pt.ScratchVar(pt.TealType.uint64)
    return pt.Seq(
        pt.For(
            i.store(pt.Int(0)),
            i.load() < pt.Int(30),
            i.store(i.load() + pt.Int(1)),
        ).Do(
            pt.Seq(
                pt.Assert(
                    pt.Btoi(app.state.card_bank[app.state.starting_deck[i.load()].get()].get()) > pt.Int(0),
                    comment="Insufficient cards in the bank.",
                ),
                pt.InnerTxnBuilder.Execute(
                    {
                        pt.TxnField.type_enum: pt.TxnType.AssetTransfer,
                        pt.TxnField.xfer_asset: pt.Btoi(app.state.starting_deck[i.load()].get()),
                        pt.TxnField.asset_amount: pt.Int(1),
                        pt.TxnField.asset_receiver: recipient.encode(),
                        pt.TxnField.fee: pt.Int(0),
                    }
                ),
                app.state.card_bank[app.state.starting_deck[i.load()].get()].set(
                    pt.Itob(pt.Btoi(app.state.card_bank[app.state.starting_deck[i.load()].get()].get()) - pt.Int(1))
                ),
                (mr := MembershipRecord()).set(pt.abi.Uint8(), pt.abi.Uint8(), pt.abi.Uint8()),
                (card := pt.abi.Uint64()).set(pt.abi.Uint64()),
                app.state.membership[recipient].store_into(mr),
                app.state.starting_deck[i.load()].store_into(card),
                mr.library[i.load()].set(card),
                app.state.membership[recipient].set(mr),
            ),
        ),
    )


@app.external
def signup(
    address: pt.abi.Address,
    strength: pt.abi.Uint8,
    intelligence: pt.abi.Uint8,
    dexterity: pt.abi.Uint8,
) -> pt.Expr:
    """Sign up for the game.

    Args:
        address (pt.abi.Address): Address of the player
        strength (pt.abi.Uint64): Strength
        intelligence (pt.abi.Uint64): Intelligence
        dexterity (pt.abi.Uint64): Dexterity

    Returns:
        pt.Expr: pyteal expression
    """
    return pt.Seq(
        (mr := MembershipRecord()).set(intelligence, strength, dexterity),
        app.state.membership[address].set(mr),
        transfer_starting_deck(address),
    )
