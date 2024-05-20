from pathlib import Path
import sys,json,time,algokit_utils,uuid
sys.path.append(f"{Path(__file__).parent.parent}")
from gora_utils.config import GORA_CONTRACT_ID,GORA_TOKEN_ID
from utils.misc import (get_accounts,get_algod_client,fund_account,
                        stake_algo_for_requests,stake_gora_for_requests,
                        get_gora_box_name,describe_gora_num,deploy_to_localnet)
from utils.request_specs import sportsFeedSourceOneTeamScore,sportsFeedSourceEntireMatchInfo



# THIS SIMPLE EXAMPLE SHOWS HOW TO MAKE A CLASSIC REQUEST TO THE ORACLE FOR SOME INFO PARTAINING TO A SPORT
# TO SEE THE INFO USED AS THE ARGUMENTS/PARAMETER SEE "from demo_configs.request_specs import sportsFeedSource".
# THIS HANDLES THE ORACLE SPECIFICATIONS FOR A CLASSIC SPORTS DATA REQUEST.



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


# MAKE AN ORACLE CALL TO GORACLE
# IN THE FIRST DEMO WE WILL TRY RETURNING ONLY A SINGLE VALUE FROM THE JSON RETURNED BY THE ORACLE'S API
# WE WILL USE THE SCORE OF ONE TEAM

print("MAKING THE FIRST SPORTS FEEDS REQUEST......")
req_key = uuid.uuid4().bytes
user_data = b"SOMETHING_RANDOM_OR_INFORMATIVE" # THIS CAN BE USED AS THE KEY TO STORE AND RETRIEVE REPONSES SAVED ON THE CONTRACT
box_name = get_gora_box_name(req_key,requestContractAddress)

sourceSpec = [
    sportsFeedSourceOneTeamScore.get("sourceId"), # Source ID
    sportsFeedSourceOneTeamScore.get("queryArgs") , # Query arguments
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
        aggregation_number = 1, # FOR A SINGLE VALUE LIKE A NUMBER IT IS REQUIRED YOU USE AN AGGREGATION NUMBER OF 1 INSTEAD OF 0
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

    # THE AVERAGE RESPONSE TIME OF THE ORACLE IS 8secs SO WE NEED A DELAY TO INSURE THE DATA IS SENT BACK TO OUR CONTRACT
    print("Waiting for for oracle return value (up to 5 seconds)")
    time.sleep(5)
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
    print(f"HOME TEAM SCORE : {describe_gora_num(gora_value)}") # THIS IS USED TO DECODE THE RAW DYNAMICBYTE FROM THE CONTRACT
except Exception as e:
    print(f"Oracle returned no data becuase ::: {e}")



# IN THE SECOND DEMO ONE WE WILL TRY RETURNING THE ENTIRE JSON RETURNED BY THE ORACLE'S API
print("MAKING THE SECOND SPORTS FEEDS REQUEST......")
req_key = uuid.uuid4().bytes
user_data = b"SOMETHING_RANDOM_OR_INFORMATIVE" # THIS CAN BE USED AS THE KEY TO STORE AND RETRIEVE REPONSES SAVED ON THE CONTRACT
box_name = get_gora_box_name(req_key,requestContractAddress)


# A GORA SOURCE SPECIFICATION IS A LIST CONSISTING OF THE SOURCE ID, 
# THE QUERY ARGUMENTS AND THE AGGREGATION NUMBER WHICH IS JUST 0 to N WITH ZERO DENOTING MAXIMUM RESULTS AGE
# THE SOURCE SPECIFICATION ARE IN THE FORM [int,[byte,byte.......,byte],int]

sourceSpec = [
    sportsFeedSourceEntireMatchInfo.get("sourceId"), # Source ID
    sportsFeedSourceEntireMatchInfo.get("queryArgs") , # Query arguments
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

    # THE AVERAGE RESPONSE TIME OF THE ORACLE IS 8secs SO WE NEED A DELAY TO INSURE THE DATA IS SENT BACK TO OUR CONTRACT
    print("Waiting for for oracle return value (up to 5 seconds)")
    time.sleep(5)
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

    decoded_response = gora_value.decode('utf-8')
    decoded_response = json.loads(decoded_response) # IN THE SOURCE SPEC IF WE USED b"$.data" instead of b"$.data.awayTeamScore" 
    # THIS WILL RETURN THE ENTIRE JSON RESPONSE FROM THE ORACLE THAN A SINGLE DATA VALUE
    print(f"DECODED RAW JSON DATA RETURNED BY THE ORACLE : {decoded_response}")
    if type(decoded_response) is dict:
        # IF THE ENTIRE ORACLE RESPONSE WAS RETURNED WE DISPLAY THE HOME AND AWAY TEAM SCORE
        print(f"RECEIVED ORACLE RESPONSE VALUE : {decoded_response.get('homeTeamScore')} : {decoded_response.get('awayTeamScore')}")
except Exception as e:
    print(f"Oracle returned no data becuase ::: {e}")


