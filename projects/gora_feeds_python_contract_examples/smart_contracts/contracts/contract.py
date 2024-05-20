from algopy import ARC4Contract,arc4,Application,Asset,op,Txn,log
from smart_contracts.gora_utils.misc_methods import make_oracle_request,opt_into_application,opt_into_asset
from smart_contracts.gora_utils.oracle_specs import (SourceSpec,SourceSpecOffChain,SourceSpecUrl,
                                                     BoxType,RequestSpec,RequestSpecOffChain,RequestSpecUrl,
                                                     ResponseBody)

class GoraCaller(ARC4Contract):
    """Gora's Example Contract using puya"""
    
    @arc4.abimethod
    def opt_in_assets(self,gora_token_reference: Asset,gora_app_reference: Application)->None:
        """ OPTIN THE CONTRACT TO THE NATIVE TOKEN AND GORA CONTRACT """

        assert Txn.sender == op.Global.creator_address, "expected creator"

        opt_into_asset(gora_token_reference)
        opt_into_application(gora_app_reference)
    
    @arc4.abimethod
    def return_oracle_response(self,user_data:arc4.DynamicBytes)->arc4.DynamicBytes:
        """
            READ THE ORACLE RESPONSE, 
            THIS USES THE USER DATA AS THE KEY TO THE BOX BECAUSE WE USED THE USER 
            DATA AS THE KEY TO THE BOX WHEN SAVING THE ORACLE REPONSE .
        """

        (data, exists) = op.Box.get(user_data.native)
        return arc4.DynamicBytes.from_bytes(data)

    @arc4.abimethod
    def handle_oracle_response(self,resp_type: arc4.UInt32,resp_body_bytes: arc4.DynamicBytes)->None:
        """ 
            THIS IS A SAMPLE DESTINATION METHOD, THIS SHOWS HOW THE RESPONSE FROM THE 
            ORACLE CAN BE SAVED/USED IN A SMART CONTRACT. 
            IN OUR CASE WE ONLY SAVE THE RESPONSE TO THE SMART CONTRACT

            USING A BOX STORAGE INSTEAD OF USING A LOCAL OR GLOBAL STORAGE,
            GIVES US THE FREEDOM TO RETURN ENTIRE JSON RESPONSE INSTEAD OF JUST A SINGLE JSON DATA VALUE
        """

        # auth_dest_call(Bytes(GORA_CONTRACT_ADDRESS_BIN)),
        # smart_assert(resp_type.get() == Int(1)),
        
        resp_body = ResponseBody.from_bytes(resp_body_bytes.native)
        user_data = resp_body.user_data.copy()
        oracle_value = resp_body.oracle_value.copy()
        (data, exists) = op.Box.get(user_data.native)
        if exists:
            delBox = op.Box.delete(user_data.native) # delete the box if it exists to create a new data
        op.Box.put(user_data.native,oracle_value.native)
    
    @arc4.abimethod
    def send_classic_oracle_request(
        self,
        request_type : arc4.UInt64, 
        request_key : arc4.DynamicBytes, 
        sourceSpec : arc4.DynamicArray[SourceSpec], 
        destination_app_id :  arc4.UInt64,
        destination_method : arc4.DynamicBytes, 
        aggregation_number : arc4.UInt32, 
        user_data : arc4.DynamicBytes, 
        box_references : arc4.DynamicArray[BoxType], 
        app_references : arc4.DynamicArray[arc4.UInt64],
        asset_references : arc4.DynamicArray[arc4.UInt64], 
        account_references : arc4.DynamicArray[arc4.Address]
    )->None:
        
        """
            Make an classic oracle request with specified parameters.
            This type of request are requests sent to the gora oracle for results from the oracle.
        """
        
        request_spec = RequestSpec(sourceSpec.copy(),aggregation_number,user_data.copy())
        requestSpec = arc4.DynamicBytes(request_spec.bytes)

        make_oracle_request(
            request_type,
            request_key,
            requestSpec,
            destination_app_id,
            destination_method,
            user_data,
            box_references,
            app_references,
            asset_references,
            account_references,
        )
    
    @arc4.abimethod
    def send_custom_oracle_request(
        self,
        request_type : arc4.UInt64, 
        request_key : arc4.DynamicBytes, 
        sourceSpec : arc4.DynamicArray[SourceSpecUrl], 
        destination_app_id :  arc4.UInt64,
        destination_method : arc4.DynamicBytes, 
        aggregation_number : arc4.UInt32, 
        user_data : arc4.DynamicBytes, 
        box_references : arc4.DynamicArray[BoxType], 
        app_references : arc4.DynamicArray[arc4.UInt64],
        asset_references : arc4.DynamicArray[arc4.UInt64], 
        account_references : arc4.DynamicArray[arc4.Address]
    
    )->None:
    
        """
            Make an custom oracle request with specified parameters.
            This type of request are requests sent to a custom url/api for results, 
            this url/api can include anything or it might even be a webpage.
        """

        request_spec = RequestSpecUrl(sourceSpec.copy(),aggregation_number,user_data.copy())
        requestSpec = arc4.DynamicBytes(request_spec.bytes)

        make_oracle_request(
            request_type,
            request_key,
            requestSpec,
            destination_app_id,
            destination_method,
            user_data,
            box_references,
            app_references,
            asset_references,
            account_references,
        )
        

    @arc4.abimethod
    def send_offchain_oracle_request(
        self,
        request_type : arc4.UInt64, 
        request_key : arc4.DynamicBytes, 
        sourceSpec : arc4.DynamicArray[SourceSpecOffChain], 
        destination_app_id :  arc4.UInt64,
        destination_method : arc4.DynamicBytes, 
        aggregation_number : arc4.UInt32, 
        user_data : arc4.DynamicBytes, 
        box_references : arc4.DynamicArray[BoxType], 
        app_references : arc4.DynamicArray[arc4.UInt64],
        asset_references : arc4.DynamicArray[arc4.UInt64], 
        account_references : arc4.DynamicArray[arc4.Address]
    
    )->None:
    
        """
            Make an offchain oracle request with specified parameters.
            This type of request are requests sent to an off-chain service for results, 
        """

        request_spec = RequestSpecOffChain(sourceSpec.copy(),aggregation_number,user_data.copy())
        requestSpec = arc4.DynamicBytes(request_spec.bytes)

        make_oracle_request(
            request_type,
            request_key,
            requestSpec,
            destination_app_id,
            destination_method,
            user_data,
            box_references,
            app_references,
            asset_references,
            account_references,
        )
