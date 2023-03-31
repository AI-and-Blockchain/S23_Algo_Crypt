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
