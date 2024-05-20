from pathlib import Path
import sys,json,time,algokit_utils,uuid
sys.path.append(f"{Path(__file__).parent.parent}")
from utils.request_specs import webPageSource,apiJsonSource
from gora_utils.config import GORA_CONTRACT_ID,GORA_TOKEN_ID
from utils.misc import (get_accounts,get_algod_client,fund_account,
                        stake_algo_for_requests,stake_gora_for_requests,
                        get_gora_box_name,describe_gora_num,deploy_to_localnet)




# CREATE AND DEPLOY THE TEST SMART CONTRACT
ALGOD_CLIENT = get_algod_client()
deployer = get_accounts()[0]

requestContract,requestContractID,requestContractAddress = deploy_to_localnet(deployer,ALGOD_CLIENT)


# BEFORE YOU CAN MAKE REQUESTS TO THE ORACLE YOU NEED TO HAVE SOME ALGORAND ON THE USER'S WALLET
#  AND ALSO ON THE SMART CONTRACT, THIS IS TO ACCOUNT FOR FEES ON THE ALGORAND NETWORK
# FUND THE CONTRACT CREATOR AND REQUESTER ACCOUNT


fund_account(ALGOD_CLIENT,deployer.address, 1_000_000_000_000)
fund_account(ALGOD_CLIENT,requestContractAddress, 1_000_000_000_000)


# ONCE YOU HAVE DEPLOYED YOU SMART CONTRACT YOU NEED TO OPTIN GORA TOKEN AND THE GORA APPLICATION
# AND OPTIN THE NECCESSARY TOKENS ALGOBET TOKEN AND GORA 
print("OPTING INTO GORA AND GORA TOKEN.......")
requestContract.call(
    "opt_in_assets",
    gora_token_reference=GORA_TOKEN_ID,
    gora_app_reference=GORA_CONTRACT_ID,
)


# GORA/ALGO STAKING
# BEFORE YOU CAN MAKE CALLS TO THE GORA ORACLE YOU NEED TO STAKE SOME GORA AND ALGO ON THE GORA ORACLE SMART CONTRACT
# THE ALGO IS USED TO COVER BOX FEES, 
# NOTE : USING A DIFFERENT REQUEST KEY EACH TIME YOU MAKE A CREATES A NEW BOX ON THE GORA CONTRACT WHICH IN TURN COSTS ALGO. 
# THIS DEPLETES THE ALGO YOU STAKED ON THE CONTRACT, YOU MIGHT NEED TO STAKE MORE, IDEALY 2 ALGOS IS ENOUGH FOR A SIMPLE APPLICATION
# THE GORA YOU STAKED IS USED AS THE PAYMENT FOR MAKING REQUESTS, IN WEB2 YOU MIGHT CALL IN THE API COSTS, 
# EACH TIME YOU MAKE A CALL TO THE ORACLE A CERTAIN AMOUNT IS USED AS FEES THIS IS USED AS A REWARD TO THE VALIDATORS FOR VALIDATING YOUR CALLS
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
# NOW LET"S TRYING MAKING A CUSTOM REQUEST TO THE GORA ORACLE
# YOU NEED TO PROVIDE A REQUEST KEY 
# (THIS IS A UNIQUE IDENTIFIER FOR YOUR BOX STORAGE ON THE GORA APPLICATION IN CASE YOU NEED ASSISTANCE DEBUGING YOU APPLICATION ON THE GORA CONTRACT)
print("MAKING A CLASSIC ORACLE REQUEST......")
req_key = uuid.uuid4().bytes
user_data = b"SOMETHING_RANDOM" # THIS USER DATA CAN BE ANYTHING, IT CAN BE USED AS A KEY TO A BOX FOR STORING THE ORACLE RESPONSE ON THE DESTINATION METHOD 
# (CHECK THE DESTINATION METHOD ON THE CONTRACT TO SEE HOW IT IS USED)
box_name = get_gora_box_name(req_key,requestContractAddress) # THIS IS AN ENCODING OF THE GORA KEY USED FOR STORING YOUR REQUEST/RESPONSE ON THE GORA CONTRACT



# IN THE FIRST DEMO WE WILL TRY RETURNING DATA FROM A WEBPAGE USING REGEX
# WE WILL USE THE PRICE INCREASE OF BNB IN THE LAST 24 HOURS FROM COINMARKETCAP.COM

try:
    result = requestContract.call(
        "send_custom_oracle_request",
        request_type = 2,
        request_key=req_key,
        sourceSpec=webPageSource,
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

    print(f"CUSTOM FEED RESPONSE::: BNB HAS INCREASED {describe_gora_num(gora_value)}% IN THE LAST 24 HOURS") # THIS IS USED TO DECODE THE RAW DYNAMICBYTE FROM THE CONTRACT
except Exception as e:
    print(f"Oracle returned no data becuase ::: {e}")




print("MAKING A CLASSIC ORACLE REQUEST......")
req_key = uuid.uuid4().bytes
user_data = b"SOMETHING_RANDOM" 
box_name = get_gora_box_name(req_key,requestContractAddress)



# IN THE SECOND DEMO WE WILL TRY RETURNING DATA FROM AN API AND RETURN THE DATA
# WE WILL USE AN OPEN SOURCE API THAT RETURNS A RANDOM MATCH FACT EACH TIME IT'S CALLED
# IF YOU TAKE A LOOK AT THE SOURCE SPECS OF THE TWO DEMOS YOU WILL NOTICE 2 DIFFERENCES, THE value_type AND value_expr EXPERESSION.
# PLEASE NOTE A VALUE TYPE OF 0 DENOTES THE REPONSE YOU WANT IS CONVERTED TO STRING IF IT IS 1 THEN IT IS CONVERTED INTO A NUMBER


# NOTE : THE SOURCE SPEC FOR CUSTOM URL AND CLASSIC FEEDS ARE DIFFERENT CHECK THE R
try:
    result = requestContract.call(
        "send_custom_oracle_request",
        request_type = 2,
        request_key=req_key,
        sourceSpec=apiJsonSource,
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

    print(f"CUSTOM FEED RESPONSE::: RANDOM CAT FACT :: {gora_value}") # THIS IS USED TO DECODE THE RAW DYNAMICBYTE FROM THE CONTRACT
except Exception as e:
    print(f"Oracle returned no data becuase ::: {e}")
