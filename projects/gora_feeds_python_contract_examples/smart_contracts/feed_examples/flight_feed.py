from pathlib import Path
from algosdk import encoding
import sys,json,time,algokit_utils,uuid
sys.path.append(f"{Path(__file__).parent.parent}")
from utils.request_specs import flightDataSource
from gora_utils.config import GORA_CONTRACT_ID,GORA_TOKEN_ID
from utils.misc import (get_accounts,get_algod_client,fund_account,
                        stake_algo_for_requests,stake_gora_for_requests,
                        get_gora_box_name,describe_gora_num,deploy_to_localnet)



"""
    THIS SIMPLE EXAMPLE SHOWS HOW TO MAKE A CLASSIC REQUEST TO THE ORACLE FOR SOME INFO PARTAINING TO A FLIGHT
    TO SEE THE INFO USED AS THE ARGUMENTS/PARAMETER SEE "from demo_configs.request_specs import flightDataSource".

    THIS HANDLES THE ORACLE SPECIFICATIONS FOR A CLASSIC FLIGHT DATA REQUEST.
    
"""

ALGOD_CLIENT = get_algod_client()
deployer = get_accounts()[0]

requestContract,requestContractID,requestContractAddress = deploy_to_localnet(deployer,ALGOD_CLIENT)


fund_account(ALGOD_CLIENT,deployer.address, 1_000_000_000_000)
fund_account(ALGOD_CLIENT,requestContractAddress, 1_000_000_000_000)



print("OPTING INTO GORA AND GORA TOKEN.......")
requestContract.call(
    "opt_in_assets",
    gora_token_reference=GORA_TOKEN_ID,
    gora_app_reference=GORA_CONTRACT_ID,
)

print("STAKING SOME GORA AND ALGO TO THE GORA CONTRACT......")
deposit_amount = 10_000_000_000
stake_algo_for_requests(
    ALGOD_CLIENT,
    deployer,
    deposit_amount,
    requestContractAddress,
    GORA_CONTRACT_ID
)

stake_gora_for_requests(
    ALGOD_CLIENT,
    deployer,
    deposit_amount,
    requestContractAddress,
    GORA_CONTRACT_ID,
    GORA_TOKEN_ID
)
print("STAKED GORA AND ALGO TO THE GORA CONTRACT")


""" MAKE AN ORACLE CALL TO GORACLE """
print("MAKING A CLASSIC ORACLE REQUEST......")
req_key = uuid.uuid4().bytes
user_data = b"SOMETHING_RANDOM" 
box_name = get_gora_box_name(req_key,requestContractAddress)

# A GORA SOURCE SPECIFICATION IS A LIST CONSISTING OF THE SOURCE ID, 
# THE QUERY ARGUMENTS AND THE AGGREGATION NUMBER WHICH IS JUST 0 to N WITH ZERO DENOTING MAXIMUM RESULTS AGE
# THE SOURCE SPECIFICATION ARE IN THE FORM [int,[byte,byte.......,byte],int]
sourceSpec = [
    flightDataSource.get("sourceId"), # Source ID
    flightDataSource.get("queryArgs") , # Query arguments
    0 # Maximum result age (0 - no limit)
],

try:
    result = requestContract.call(
        "send_classic_oracle_request",
        request_type = 1,
        request_key=req_key,
        sourceSpec=sourceSpec,
        destination_app_id = requestContractID,
        destination_method = b"handle_oracle_response",
        aggregation_number = 0,
        user_data=user_data,
        box_references=[],
        app_references=[],
        asset_references=[],
        account_references=[],

        transaction_parameters=algokit_utils.OnCompleteCallParameters(
            foreign_apps=[ GORA_CONTRACT_ID ],
            boxes=[ (GORA_CONTRACT_ID, box_name),(GORA_CONTRACT_ID, user_data), ],
        ),
    )
    print("REQUEST SENT")

    print("Confirmed in round:", result.confirmed_round)
    print("Top txn ID:", result.tx_id)

    # print("Waiting for for oracle return value (up to 10 seconds)")
    # time.sleep(10)
except Exception as e:
    print(f"Oracle couldn't process request because ::: {e}")


# READ THE RESPONSE RETURNED BY GORACLE
try:
    value = requestContract.call(
        "return_oracle_response",
        user_data=user_data,
        transaction_parameters=algokit_utils.OnCompleteCallParameters(
            signer=deployer.signer,
            sender=deployer.address,
            boxes=[(requestContractID, user_data)],
        ),
    )
    gora_value = value.raw_value

    print(f"WEATHER RESULT: {describe_gora_num(gora_value)}") # THIS IS USED TO DECODE THE RAW DYNAMICBYTE FROM THE CONTRACT
except Exception as e:
    print(f"Oracle returned no data becuase ::: {e}")
