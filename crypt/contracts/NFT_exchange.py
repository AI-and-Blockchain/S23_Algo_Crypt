"""NFT Exchange contracts for the NFT marketplace. Can be flat price or auction.

Auction Contract

Fields:
    type: str (Global) ("card" or "enemy")
    name: str (Global)
    image_uri: str (Global)
    description: str (Global)
    buy_now_price: int (Global)
    auction_start_time: int (Global)
    auction_end_time: int (Global)
    auction_start_price: int (Global)
    current_bid: int (Global)
    current_bidder: str

Methods:
    bid: (int) -> (int)
        Bids the given amount of money.
        Returns the new current bid.

    buy_now: () -> (int)
        Buys the item for the buy now price.
        Returns the new current bid.

    reset: () -> (int)
        Resets the auction to the initial state.
        Returns the new current bid.

Flat Price Contract

Fields:
    type: str (Global) ("card" or "enemy")
    name: str (Global)
    image_uri: str (Global)
    description: str (Global)
    price: int (Global)

Methods:
    buy: () -> (int)
        Buys the item for the price.
        Returns the new current bid.
"""

from beaker import *
from pyteal import *
from typing import Final

# Base States
# ===========

class Auction(Application):
    """State of the auction contract."""

    owner: GlobalStateValue(
        stack_type=abi.Address,
        descr="Owner of the contract",
        default=Global.creator_address()
    )
    name: GlobalStateValue(
        stack_type=abi.String,
        descr="Name of the item",
        default=""
    )
    image_uri: GlobalStateValue(
        stack_type=abi.String,
        descr="URI of the image of the item",
        default=""
    )
    description: GlobalStateValue(
        stack_type=abi.String,
        descr="Description of the item",
        default=""
    )
    buy_now_price: GlobalStateValue(
        stack_type=abi.Uint64,
        descr="Buy now price of the item",
        default=0
    )
    auction_start_time: GlobalStateValue(
        stack_type=abi.Uint64,
        descr="Start time of the auction",
        default=Global.latest_timestamp()
    )
    auction_end_time: GlobalStateValue(
        stack_type=abi.Uint64,
        descr="End time of the auction",
        default=0
    )
    auction_start_price: GlobalStateValue(
        stack_type=abi.Uint64,
        descr="Start price of the auction",
        default=0
    )
    current_bid: GlobalStateValue(
        stack_type=abi.Uint64,
        descr="Current bid of the auction",
        default=0
    )
    current_bidder: GlobalStateValue(
        stack_type=abi.Address,
        descr="Current bidder of the auction",
        default=Global.zero_address()
    )    


class FlatPrice(Application):
    """State of the flat price contract."""

    owner: GlobalStateValue(
        stack_type=abi.Address,
        descr="Owner of the contract",
        default=Global.creator_address()
    )
    name: GlobalStateValue(
        stack_type=abi.String,
        descr="Name of the item",
        default=""
    )
    image_uri: GlobalStateValue(
        stack_type=abi.String,
        descr="URI of the image of the item",
        default=""
    )
    description: GlobalStateValue(
        stack_type=abi.String,
        descr="Description of the item",
        default=""
    )
    price: GlobalStateValue(
        stack_type=abi.Uint64,
        descr="Price of the item",
        default=0
    )


# Specific States
# ===============

class CardAuction(Auction):
    """State of the card auction contract."""

    type: GlobalStateValue(
        stack_type=abi.String,
        descr="Type of the item",
        default="card"
    )


class EnemyAuction(Auction):
    """State of the enemy auction contract."""

    type: GlobalStateValue(
        stack_type=abi.String,
        descr="Type of the item",
        default="enemy"
    )


class CardFlatPrice(FlatPrice):
    """State of the card flat price contract."""

    type: GlobalStateValue(
        stack_type=abi.String,
        descr="Type of the item",
        default="card"
    )


class EnemyFlatPrice(FlatPrice):
    """State of the enemy flat price contract."""

    type: GlobalStateValue(
        stack_type=abi.String,
        descr="Type of the item",
        default="enemy"
    )


# Blueprints
# ==========

def auction_blueprint(app: Application) -> None:
    @app.create
    def create() -> Expr:
        return app.initialize_global_state()
    
    @app.external(authorize=Authorize.only(app.owner))
    def start_auction(
        paymentTx: abi.PaymentTransaction,
        name: abi.String,
        image_uri: abi.String,
        description: abi.String,
        auction_end_time: abi.Uint64,
        auction_start_price: abi.Uint64,
    ) -> Expr:
        return Seq(
            Assert(paymentTx.receiver() == Global.current_application_address()),
            Assert(paymentTx.amount() == Int(100_000)),
            app.name.set(name),
            app.image_uri.set(image_uri),
            app.description.set(description),
            app.auction_start_time.set(Global.latest_timestamp()),
            app.auction_end_time.set(auction_end_time),
            app.auction_start_price.set(auction_start_price),
        )
