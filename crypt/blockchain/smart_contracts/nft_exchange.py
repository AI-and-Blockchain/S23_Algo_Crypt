"""Containts the NFT exchange contract."""

import beaker as bk
import pyteal as pt

from beaker.lib.storage import BoxList, BoxMapping


class NFTExchangeState:
    """State of the NFT exchange contract."""

    owner = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        default=pt.Global.creator_address(),
        descr="Owner of the contract.",
    )

    name = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        default=pt.Bytes(""),
        descr="Name of the contract.",
    )
    descr = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        default=pt.Bytes(""),
        descr="description of the contract.",
    )

    image_uri = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        default=pt.Bytes(""),
        descr="URI of the image of the contract.",
    )

    asset_id = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Asset ID of the NFT.",
    )
    price = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Price of the NFT.",
    )


app = bk.Application(
    name="Asset Exchange",
    state=NFTExchangeState,
)


@app.create
def create() -> pt.Expr:
    """Create the contract."""
    return app.initialize_global_state()


@app.external(authorize=bk.Authorize.only(app.state.owner.get()))
def update(
    name: pt.abi.String,
    descr: pt.abi.String,
    image_uri: pt.abi.String,
    asset_id: pt.abi.Uint64,
    price: pt.abi.Uint64,
) -> pt.Expr:
    """Update the contract.

    Args:
        name (pt.abi.String): name of NFT
        descr (pt.abi.String): descrription of NFT
        image_uri (pt.abi.String): URI of image of NFT
        asset_id (pt.abi.Uint64): asset ID of NFT
        price (pt.abi.Uint64): price of NFT

    Returns:
        pt.Expr: pyteal expression
    """
    return pt.Seq(
        app.state.name.set(name.get()),
        app.state.descr.set(descr.get()),
        app.state.image_uri.set(image_uri.get()),
        app.state.asset_id.set(asset_id.get()),
        app.state.price.set(price.get()),
    )
