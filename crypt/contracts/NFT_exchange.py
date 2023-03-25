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