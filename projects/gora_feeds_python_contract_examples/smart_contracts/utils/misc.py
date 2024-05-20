from typing import List
from pathlib import Path
from algosdk.logic import *
from .abi import GORACLE_ABI
from helpers.build import build
from dataclasses import dataclass
from algosdk.kmd import KMDClient
from algosdk.wallet import Wallet
from algosdk.encoding import decode_address
from algosdk.v2client import algod, indexer
import os,sys,algokit_utils,json,hashlib,struct
from algosdk.abi.method import get_method_by_name, Method
from algosdk.transaction import (AssetTransferTxn,PaymentTxn,wait_for_confirmation,)
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionWithSigner,
    AccountTransactionSigner,
)


KMD_ADDRESS = "http://localhost"
KMD_TOKEN = "a" * 64
KMD_PORT = os.getenv("KMD_PORT", default="4002")
KMD_URL = f"{KMD_ADDRESS}:{KMD_PORT}"

DEFAULT_KMD_WALLET_NAME = "unencrypted-default-wallet"
DEFAULT_KMD_WALLET_PASSWORD = ""

ALGOD_ADDRESS = "http://localhost"
ALGOD_TOKEN = "a" * 64
ALGOD_PORT = os.getenv("ALGOD_PORT", default="4001")
ALGOD_URL = f"{ALGOD_ADDRESS}:{ALGOD_PORT}"

INDEXER_ADDRESS = "http://localhost"
INDEXER_TOKEN = "a" * 64
INDEXER_PORT = os.getenv("INDEXER_PORT", default="8980")
INDEXER_URL = f"{INDEXER_ADDRESS}:{INDEXER_PORT}"



@dataclass
class SandboxAccount:
    """SandboxAccount is a simple dataclass to hold a sandbox account details"""

    #: The address of a sandbox account
    address: str
    #: The base64 encoded private key of the account
    private_key: str
    #: An AccountTransactionSigner that can be used as a TransactionSigner
    signer: AccountTransactionSigner


""" This is acts as the algo dispenser """

def fund_account(ALGOD_CLIENT,receiver_address, amount: int):
    # get dispenser account
    dispenser_account = algokit_utils.get_dispenser_account(ALGOD_CLIENT)
    suggested_params = ALGOD_CLIENT.suggested_params()

    unsigned_txn = PaymentTxn(
        sender=dispenser_account.address,
        sp=suggested_params,
        receiver=receiver_address,
        amt=amount,
    )
    signed_txn = unsigned_txn.sign(dispenser_account.private_key)

    txid = ALGOD_CLIENT.send_transaction(signed_txn)
    txn_result = wait_for_confirmation(ALGOD_CLIENT, txid, 4)

    return json.dumps(txn_result, indent=4)

def get_algod_client(
    addr: str = ALGOD_URL, token: str = ALGOD_TOKEN
) -> algod.AlgodClient:
    return algod.AlgodClient(algod_token=token, algod_address=addr)


def get_kmd_client(addr: str = KMD_URL, token: str = KMD_TOKEN) -> KMDClient:
    """creates a new kmd client using the default sandbox parameters"""
    return KMDClient(kmd_token=token, kmd_address=addr)


def get_indexer_client(
    addr: str = INDEXER_URL, token: str = INDEXER_TOKEN
) -> indexer.IndexerClient:
    """creates a new indexer client using the default sandbox parameters"""
    return indexer.IndexerClient(indexer_token=token, indexer_address=addr)


def get_sandbox_default_wallet() -> Wallet:
    """returns the default sandbox kmd wallet"""
    return Wallet(
        wallet_name=DEFAULT_KMD_WALLET_NAME,
        wallet_pswd=DEFAULT_KMD_WALLET_PASSWORD,
        kmd_client=get_kmd_client(),
    )

def get_accounts(
    kmd_address: str = KMD_URL,
    kmd_token: str = KMD_TOKEN,
    wallet_name: str = DEFAULT_KMD_WALLET_NAME,
    wallet_password: str = DEFAULT_KMD_WALLET_PASSWORD,
) -> List[SandboxAccount]:
    """gets all the accounts in the sandbox kmd, defaults
    to the `unencrypted-default-wallet` created on private networks automatically
    """

    kmd = KMDClient(kmd_token, kmd_address)
    wallets = kmd.list_wallets()

    wallet_id = None
    for wallet in wallets:
        if wallet["name"] == wallet_name:
            wallet_id = wallet["id"]
            break

    if wallet_id is None:
        raise Exception("Wallet not found: {}".format(wallet_name))

    wallet_handle = kmd.init_wallet_handle(wallet_id, wallet_password)

    try:
        addresses = kmd.list_keys(wallet_handle)
        private_keys = [
            kmd.export_key(wallet_handle, wallet_password, addr)
            for addr in addresses
        ]
        kmd_accounts = [
            SandboxAccount(
                addresses[i],
                private_keys[i],
                AccountTransactionSigner(private_keys[i]),
            )
            for i in range(len(private_keys))
        ]
    finally:
        kmd.release_wallet_handle(wallet_handle)

    return kmd_accounts


def deploy_to_localnet(deployer,ALGOD_CLIENT):
    """ This is used to deploy smart contract to the localnet """
    # "/" for linux "\" for windows
    if "win" in str(sys.platform):
        system_delima = "\\"
    else:
        system_delima = "/"

    default_app_path = Path(f"artifacts{system_delima}")
    absolute_app_path = f"{Path(__file__).parent.parent}{system_delima}"
    contract_app_path = Path(f"{Path(__file__).parent.parent}{system_delima}/contracts/contract.py")

    build(default_app_path,contract_app_path)
    app_spec_path = Path(f"{default_app_path.resolve()}{system_delima}GoraCaller.arc32.json")


    requestContract = algokit_utils.ApplicationClient(
        algod_client=ALGOD_CLIENT,
        app_spec=app_spec_path.resolve(),
        signer=deployer,
    )

    requestContract.create()
    requestContractId = requestContract.app_id
    requestContractAddress = requestContract.app_address
    fund_account(ALGOD_CLIENT,requestContractAddress,1_000_000_000_000) # fund the contract with some Algos
    print(
        f"CONTRACT SUCCESFULLY DEPLOYED : \n\n CONTRACT ID :: {requestContractId} \n\n CONTRACT ADDRESS :: {requestContractAddress}"
    )

    return requestContract,requestContractId,requestContractAddress

    
def describe_gora_num(packed):
    """
        Return text description of a numeric oracle response.
        This is used to decode floating point numbers or just numbers returned by the oracle in general
    """

    if packed is None:
        return "None"
    if packed[0] == 0:
        return "NaN"

    int_part = struct.unpack_from('>Q', packed, 1)
    dec_part = struct.unpack_from('>Q', packed, 9)
    prefix = "-" if packed[0] == 2 else ""
    return prefix + str(int_part[0]) + "." + str(dec_part[0])

def get_gora_box_name(req_key, addr):
    """
        Return Algorand storage box name for a Gora request key and requester address.
    """

    pub_key = decode_address(addr)
    hash_src = pub_key + req_key
    name_hash = hashlib.new("sha512_256", hash_src)
    return name_hash.digest()


def get_methods_list(abi_json: dict):
    """ This gets the list of methods given the ABI """

    abi_methods = abi_json["methods"]

    methods_list = []
    for method in abi_methods:
        json_string = json.dumps(method)
        abi_method = Method.from_json(json_string)
        methods_list.append(abi_method)
    return methods_list


def stake_gora_for_requests(algod_client, account,deposit_amount,algobets_contract_address,gora_contract_id,gora_token_id):
    """
        Setup a token deposit with Gora for a given account and app.
        This serves as the vesting/ staking of gora for making requests
    """

    composer = AtomicTransactionComposer()
    unsigned_transfer_txn = AssetTransferTxn(
        sender=account.address,
        sp=algod_client.suggested_params(),
        receiver=get_application_address(gora_contract_id),
        index=gora_token_id,
        amt=deposit_amount,
    )
    signer = AccountTransactionSigner(account.private_key)
    signed_transfer_txn = TransactionWithSigner(
        unsigned_transfer_txn,
        signer
    )
    composer.add_method_call(
        app_id=gora_contract_id,
        method=get_method_by_name(
                get_methods_list(GORACLE_ABI), "deposit_token"
            ),
        sender=account.address,
        sp=algod_client.suggested_params(),
        signer=signer,
        method_args=[ signed_transfer_txn, gora_token_id, algobets_contract_address ]
    )
    composer.execute(algod_client, 4)




def stake_algo_for_requests(algod_client,account,deposit_amount,algobets_contract_address,gora_contract_id):
    """
        Setup an Algo deposit with Gora for a given account and app.
        This serves as the vesting/ staking of algo for making requests
    """
    
    composer = AtomicTransactionComposer()
    unsigned_payment_txn = PaymentTxn(
        sender=account.address,
        sp=algod_client.suggested_params(),
        receiver=get_application_address(gora_contract_id),
        amt=deposit_amount,
    )
    signer = AccountTransactionSigner(account.private_key)
    signed_payment_txn = TransactionWithSigner(
        unsigned_payment_txn,
        signer
    )
    composer.add_method_call(
        app_id=gora_contract_id,
        method=get_method_by_name(
                get_methods_list(GORACLE_ABI), "deposit_algo"
            ),
        sender=account.address,
        sp=algod_client.suggested_params(),
        signer=signer,
        method_args=[ signed_payment_txn, algobets_contract_address ]
    )
    composer.execute(algod_client, 4)
