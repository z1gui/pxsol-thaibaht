import pathlib
import pxsol

# Enable log
pxsol.config.current.log = 1

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

program_data = pathlib.Path('target/deploy/pxsol_thaibaht.so').read_bytes()
program_pubkey = ada.program_deploy(bytearray(program_data))
print(program_pubkey) # APj2A9gMDhSab7J1Nwtp7LxiZTzb8F3U4vXHLVS4aC9R
