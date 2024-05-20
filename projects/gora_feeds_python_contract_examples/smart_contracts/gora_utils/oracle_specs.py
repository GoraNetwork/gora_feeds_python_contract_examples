import typing
from algopy import arc4

REQUEST_METHOD_SPEC = "(byte[],byte[],uint64,byte[],uint64[],uint64[],address[],(byte[],uint64)[])void"


# Storage box specification.
class BoxType(arc4.Struct):
    key: arc4.DynamicBytes
    app_id:arc4.UInt64


# Oracle source specification
class SourceSpec(arc4.Struct):
    source_id: arc4.UInt32
    source_arg_list: arc4.DynamicArray[arc4.DynamicBytes]
    max_age: arc4.UInt32

# Oracle source specification for General URL (type #2) requests.
class SourceSpecUrl(arc4.Struct):
    url: arc4.DynamicBytes
    auth_url: arc4.DynamicBytes
    value_expr: arc4.DynamicBytes
    timestamp_expr: arc4.DynamicBytes
    max_age: arc4.UInt32
    value_type: arc4.UInt8
    round_to: arc4.UInt8
    gateway_url: arc4.DynamicBytes
    reserved_0: arc4.DynamicBytes
    reserved_1: arc4.DynamicBytes
    reserved_2: arc4.UInt32
    reserved_3: arc4.UInt32

# Oracle source specification for off-chain (type #3) requests.
class SourceSpecOffChain(arc4.Struct):
    api_version: arc4.UInt32 # Minimum off-chain API version required
    spec_type: arc4.UInt8 # executable specification type:
                                          # 0 - in-place code,
                                          # 1 - storage box (8-byte app ID followed by box name)
                                          # 2 - URL
    exec_spec: arc4.DynamicBytes # executable specification
    exec_args: arc4.DynamicArray[arc4.DynamicBytes] # input arguments
    reserved_0: arc4.DynamicBytes # reserved for future use
    reserved_1: arc4.DynamicBytes
    reserved_2: arc4.UInt32
    reserved_3: arc4.UInt32

# Oracle classic request specification.
class RequestSpec(arc4.Struct):
    source_specs: arc4.DynamicArray[SourceSpec]
    aggregation: arc4.UInt32
    user_data: arc4.DynamicBytes

# Oracle general URL (type #2) request specification.
class RequestSpecUrl(arc4.Struct):
    source_specs: arc4.DynamicArray[SourceSpecUrl]
    aggregation: arc4.UInt32
    user_data: arc4.DynamicBytes

# Oracle off-chain (type #3) request specification.
class RequestSpecOffChain(arc4.Struct):
    source_specs: arc4.DynamicArray[SourceSpecOffChain]
    aggregation: arc4.UInt32
    user_data: arc4.DynamicBytes

# Specification of destination called by the oracle when returning data.
class DestinationSpec(arc4.Struct):
    app_id:arc4.UInt64
    method: arc4.DynamicBytes

# Oracle response body.
class ResponseBody(arc4.Struct):
    request_id: arc4.StaticArray[arc4.Byte, typing.Literal[32]]
    requester_addr: arc4.Address
    oracle_value: arc4.DynamicBytes
    user_data: arc4.DynamicBytes
    error_code: arc4.UInt32
    source_errors:arc4.UInt64
