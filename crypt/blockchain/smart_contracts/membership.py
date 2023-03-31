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
    governor: bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        default=pt.Global.creator_address(),
        descr="Address of the governor of the game.",
    )

    def __init__(self, *, membership_record: type[pt.abi.BaseType], card_type: type[pt.abi.BaseType]):
        self.card_bank = BoxMapping(pt.abi.Uint64, pt.abi.Uint64)  # card_asset_id -> card_count
        self.membership = BoxMapping(pt.abi.Address, membership_record)  # address -> membership_record
        self.all_cards = BoxMapping(pt.abi.Uint64, card_type)  # card_asset_id -> card


app = bk.Application(
    name="Algo Crypt Meta State",
    state=MembershipState(
        membership_record=MembershipRecord,
        card_type=Card,
    ),
)


@app.external(authorize=bk.Authorize.only_creator())
def bootstrap(
    seed: pt.abi.PaymentTransaction,
    card_list: pt.abi.DynamicArray[pt.abi.Tuple3[pt.abi.String, pt.abi.String, pt.abi.String]],
    *,
    output: pt.abi.DynamicArray[pt.abi.Uint64],
) -> pt.Expr:
    """Bootstrap the game with a list of cards.

    Args:
        seed (pt.abi.PaymentTransaction): seeded transaction
        card_list (pt.abi.Array[
            pt.abi.Tuple3[pt.abi.String, pt.abi.String, pt.abi.String]
            ]): List of cards (name, description, url)
        output (pt.abi.Array[pt.abi.Uint64]): List of card asset ids

    Returns:
        pt.Expr: pyteal expression
    """
    n_cards = pt.ScratchVar(pt.TealType.uint64)
    i = pt.ScratchVar(pt.TealType.uint64)
    return pt.Seq(
        pt.Assert(
            seed.get().receiver() == pt.Global.current_application_address(),
            comment="Seed transaction must be sent to the application address.",
        ),
        n_cards.store(card_list.length()),
        pt.For(
            i.store(0),
            i.load() < n_cards.load(),
            i.store(i.load() + 1),
            pt.Seq(
                pt.InnerTxnBuilder(
                    {
                        pt.TxnField.type_enum: pt.TxnType.AssetConfig,
                        pt.TxnField.config_asset_name: card_list[i.load()][0],
                        pt.TxnField.config_asset_unit_name: pt.Bytes("CRPT-Card-{i}"),
                        pt.TxnField.config_asset_total: 10000,
                        pt.TxnField.config_asset_decimals: 0,
                        pt.TxnField.config_asset_default_frozen: False,
                        pt.TxnField.config_asset_manager: pt.Global.current_application_address(),
                        pt.TxnField.config_asset_reserve: pt.Global.current_application_address(),
                        pt.TxnField.config_asset_freeze: pt.Global.current_application_address(),
                        pt.TxnField.config_asset_clawback: pt.Global.current_application_address(),
                        pt.TxnField.fee: pt.Int(0),
                    }
                ),
                (card_name := pt.abi.String()).set(pt.Bytes("{card_list[i.load()][0]}")),
                (card_desc := pt.abi.String()).set(pt.Bytes("{card_list[i.load()][1]}")),
                (card_url := pt.abi.String()).set(pt.Bytes("{card_list[i.load()][2]}")),
                (card_obj := Card()).set(card_name, card_desc, card_url),
                app.state.all_cards[pt.InnerTxn.asset_id()].set(card_obj),
                output.set(output.get() + [pt.InnerTxn.asset_id()]),
            ),
        ),
    )
