from algopy.op import Global,ITxnCreate
from algopy import arc4,subroutine,itxn,Asset,TransactionType,UInt64,Application,OnCompleteAction
from .oracle_specs import BoxType,DestinationSpec,REQUEST_METHOD_SPEC


@subroutine
def opt_into_asset(asset: Asset) -> None:
    """This method is used to optin an asset into a contract"""

    ITxnCreate.begin()
    ITxnCreate.set_type_enum(TransactionType.AssetTransfer)
    ITxnCreate.set_asset_receiver(Global.current_application_address)
    ITxnCreate.set_xfer_asset(asset)
    ITxnCreate.submit()


@subroutine
def opt_into_application(application_id: Application) -> None:
    """This method is used to optin an application into a contract"""

    ITxnCreate.begin()
    ITxnCreate.set_type_enum(TransactionType.ApplicationCall)
    ITxnCreate.set_application_id(application_id)
    ITxnCreate.set_on_completion(OnCompleteAction.OptIn)
    ITxnCreate.submit()

@subroutine
def make_oracle_request(
        request_type : arc4.UInt64, 
        request_key : arc4.DynamicBytes, 
        requestSpec : arc4.DynamicBytes, # RequestSpec | RequestSpecUrl | RequestSpecOffChain 
        destination_app_id :  arc4.UInt64,
        destination_method : arc4.DynamicBytes,
        user_data : arc4.DynamicBytes, 
        box_references : arc4.DynamicArray[BoxType], 
        app_references : arc4.DynamicArray[arc4.UInt64],
        asset_references : arc4.DynamicArray[arc4.UInt64], 
        account_references : arc4.DynamicArray[arc4.Address]
    )->None:
    
    """
        Make an oracle request with specified parameters.
    """
    request_type_abi = request_type
    data_box = BoxType(user_data.copy(),destination_app_id)
    box_references.extend((data_box.copy(),))
    
    dest = DestinationSpec(destination_app_id, destination_method.copy())

    destination_abi = arc4.DynamicBytes(dest.bytes)


    itxn.ApplicationCall(
        app_id= Application(1002),
        app_args=( 
            arc4.arc4_signature("request" + REQUEST_METHOD_SPEC),
            requestSpec.copy(), 
            destination_abi.copy(), 
            request_type_abi, 
            request_key.copy(),
            app_references.copy(), 
            asset_references.copy(), 
            account_references.copy(), 
            box_references.copy() 
        ),
        
    ).submit()



# def auth_dest_call(GORA_CONTRACT_ADDRESS_BIN:arc4.Byte)->None:
#     """
#         Confirm that current call to a destination app is coming from Gora.
#     """

#     pass
#     # return Seq(
#     #     (caller_creator_addr = AppParam.creator(Global.caller_app_id())),
#     #     smart_assert(caller_creator_addr.value() == GORA_CONTRACT_ADDRESS_BIN),
#     # )



# def smart_assert(cond):
#     """
#         Assert with a number to indentify it in API error message. The message will be:
#         "shr arg too big, (1000000%d)" where in "%d" is the line number.
#     """

#     err_line = sys._getframe().f_back.f_lineno # calling line number

#     if not cond:
#         return 
#     # return If(Not(cond)).Then(
#     #     InlineAssembly("int 0\nint {}\nshr\n".format(1000000 + err_line))
#     # )
