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
from argparse import ArgumentParser

# Base States
# ===========

class AuctionState:
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
        default=0
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


class FlatPriceState:
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

class CardAuction(AuctionState):
    """State of the card auction contract."""

    type: GlobalStateValue(
        stack_type=abi.String,
        descr="Type of the item",
        default="card"
    )


class EnemyAuction(AuctionState):
    """State of the enemy auction contract."""

    type: GlobalStateValue(
        stack_type=abi.String,
        descr="Type of the item",
        default="enemy"
    )


class CardFlatPrice(FlatPriceState):
    """State of the card flat price contract."""

    type: GlobalStateValue(
        stack_type=abi.String,
        descr="Type of the item",
        default="card"
    )


class EnemyFlatPrice(FlatPriceState):
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
    
    @Subroutine(TealType.none)
    def pay(receiver: Expr, amount: Expr) -> Expr:
        return InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: receiver,
                TxnField.amount: amount,
                TxnField.fee: Int(0)
            }
        )
    
    @app.external(authorize=Authorize.only(app.owner))
    def start_auction(
        paymentTx: abi.PaymentTransaction,
        name: abi.String,
        image_uri: abi.String,
        description: abi.String,
        buy_now_price: abi.Uint64,
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
            app.buy_now_price.set(buy_now_price),
            app.auction_end_time.set(auction_end_time),
            app.auction_start_price.set(auction_start_price),
        )
    
    @app.external
    def bid(paymentTx: abi.PaymentTransaction) -> Expr:
        payment = paymentTx.get()

        end_time = app.auction_end_time.get()
        start_time = app.auction_start_time.get()
        highest_bidder = app.current_bidder.get()
        highest_bid = app.current_bid.get()
        return Seq(
            Assert(paymentTx.receiver() == Global.current_application_address()),
            Assert(payment.amount() > highest_bid),
            Assert(Global.latest_timestamp() < end_time),
            Assert(start_time != Int(0)),
            If(
                highest_bidder != Global.zero_address(),
                pay(highest_bidder, highest_bid),
            ),
            app.current_bidder.set(payment.sender()),
            app.current_bid.set(payment.amount()),
        )
    
    @app.external
    def buy_now(paymentTx: abi.PaymentTransaction) -> Expr:
        start_time = app.auction_start_time.get()
        highest_bidder = app.current_bidder.get()
        highest_bid = app.current_bid.get()
        buy_now_price = app.buy_now_price.get()
        owner = app.owner.get()
        return Seq(
            Assert(start_time != Int(0)),
            Assert(paymentTx.receiver() == Global.current_application_address()),
            Assert(paymentTx.amount() == buy_now_price),
            If(
                highest_bidder != Global.zero_address(),
                pay(highest_bidder, highest_bid),
            ),
            pay(owner, buy_now_price),
            app.owner.set(paymentTx.sender()),
            app.auction_end_time.set_default(),
            app.auction_start_time.set_default(),
            app.auction_start_price.set_default(),
            app.current_bid.set_default(),
            app.current_bidder.set_default(),
        )
    
    @app.external(authorize=Authorize.only(app.owner))
    def end_auction() -> Expr:
        start_time = app.auction_start_time.get()
        highest_bidder = app.current_bidder.get()
        highest_bid = app.current_bid.get()
        owner = app.owner.get()
        return Seq(
            Assert(start_time != Int(0)),
            Assert(Global.latest_timestamp() > app.auction_end_time.get()),
            pay(owner, highest_bid),
            app.owner.set(highest_bidder),
            app.auction_end_time.set_default(),
            app.auction_start_time.set_default(),
            app.auction_start_price.set_default(),
            app.current_bid.set_default(),
            app.current_bidder.set_default(),
        )


def flat_price_blueprint(app: Application) -> None:
    @app.create
    def create() -> Expr:
        return app.initialize_global_state()
    
    @Subroutine(TealType.none)
    def pay(receiver: Expr, amount: Expr) -> Expr:
        return InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: receiver,
                TxnField.amount: amount,
                TxnField.fee: Int(0)
            }
        )
    
    @app.external(authorize=Authorize.only(app.owner))
    def set_price(
        paymentTx: abi.PaymentTransaction,
        name: abi.String,
        image_uri: abi.String,
        description: abi.String,
        price: abi.Uint64,
    ) -> Expr:
        return Seq(
            Assert(paymentTx.receiver() == Global.current_application_address()),
            Assert(paymentTx.amount() == Int(100_000)),
            app.name.set(name),
            app.image_uri.set(image_uri),
            app.description.set(description),
            app.price.set(price),
        )
    
    @app.external
    def buy(paymentTx: abi.PaymentTransaction) -> Expr:
        price = app.price.get()
        owner = app.owner.get()
        return Seq(
            Assert(paymentTx.receiver() == Global.current_application_address()),
            Assert(paymentTx.amount() == price),
            pay(owner, price),
            app.owner.set(paymentTx.sender()),
            app.price.set_default(),
        )


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument(
        "--auction",
        action="store_true",
        help="Build auction NFT app",
    )
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Build flat price NFT app",
    )
    parser.add_argument(
        "--type",
        type=str,
        default="card",
        help="Type of NFT to build (card or enemy)",
    )
    args = parser.parse_args()

    if args.auction:
        if args.type == "card":
            app = Application("card_auction", CardAuction)
        elif args.type == "enemy":
            app = Application("enemy_auction", EnemyAuction)
        else:
            raise ValueError("Invalid NFT type")
        auction_blueprint(app)
    elif args.flat:
        if args.type == "card":
            app = Application("card_flat", CardFlatPrice)
        elif args.type == "enemy":
            app = Application("enemy_flat", EnemyFlatPrice)
        else:
            raise ValueError("Invalid NFT type")
        flat_price_blueprint(app)
    else:
        raise ValueError("Must specify auction or flat")
    
    client = client.ApplicationClient(
        client=sandbox.get_algod_client(),
        app=app,
        signer=sandbox.get_accounts().pop().signer
    )

    app_id, app_addr, txid = client.create()
    print(
        f"""Deployed app in txid {txid}
        App ID: {app_id} 
        Address: {app_addr} 
    """
    )