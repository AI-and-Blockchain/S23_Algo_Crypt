"""Utility functions for smart contracts and blockchain interaction.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from algosdk import encoding, mnemonic, transaction, algod
import base64


def compile_teal(client: algod.AlgodClient, source: str) -> bytes:
    """Compile a TEAL program.

    Args:
        client: An AlgodClient instance.
        source: The TEAL source code.

    Returns:
        The compiled TEAL program.
    """
    return base64.b64decode(client.compile(source)["result"])

def private_key_from_mnemonic(mnemonic_phrase: str) -> bytes:
    """Derive a private key from a mnemonic phrase.

    Args:
        mnemonic_phrase: A mnemonic phrase.

    Returns:
        The private key.
    """
    return mnemonic.to_private_key(mnemonic_phrase)

def format_state(state: List[Dict[str, Any]]) -> List[Tuple[bytes, bytes]]:
    """Format a list of state dicts into a list of (key, value) tuples.

    https://developer.algorand.org/docs/get-details/dapps/pyteal/

    Args:
        states: A list of state dicts.

    Returns:
        A list of (key, value) tuples.
    """
    formatted = {}
    for item in state:
        key = item["key"]
        value = item["value"]
        formatted_key = base64.b64decode(key).decode("utf-8")
        if value["type"] == 1:
            # byte string
            if formatted_key == "voted":
                formatted_value = base64.b64decode(value["bytes"]).decode("utf-8")
            else:
                formatted_value = value["bytes"]
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value["uint"]
    return formatted

def read_global_state(client: algod.AlgodClient, app_id: int) -> List[Tuple[bytes, bytes]]:
    """Read the global state of an application.

    https://developer.algorand.org/docs/get-details/dapps/pyteal/

    Args:
        client: An AlgodClient instance.
        app_id: The application ID.

    Returns:
        The global state.
    """
    app = client.application_info(app_id)
    global_state = (
        app["params"]["global-state"] if "global-state" in app["params"] else []
    )
    return format_state(global_state)
