import base64
from algosdk import logic


GORA_TOKEN_ID = 1001
GORA_CONTRACT_ID = 1002

GORA_CONTRACT_ADDRESS = logic.get_application_address(GORA_CONTRACT_ID)
addr_decoded = base64.b32decode(GORA_CONTRACT_ADDRESS + "======")
GORA_CONTRACT_ADDRESS_BIN = addr_decoded[:-4] # remove CRC

