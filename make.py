import base64
import sys
import pxsol


def mint(user: pxsol.wallet.Wallet, amount: int) -> None:
    assert user.pubkey.base58() == '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt' # Is ada?
    prog_pubkey = pxsol.core.PubKey.base58_decode('APj2A9gMDhSab7J1Nwtp7LxiZTzb8F3U4vXHLVS4aC9R')
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)[0]
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(data_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
    rq.data = bytearray([0x00]) + bytearray(amount.to_bytes(8))
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)

def balance(user: pxsol.core.PubKey) -> int:
    prog_pubkey = pxsol.core.PubKey.base58_decode('APj2A9gMDhSab7J1Nwtp7LxiZTzb8F3U4vXHLVS4aC9R')
    data_pubkey = prog_pubkey.derive_pda(user.p)[0]
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})
    return int.from_bytes(base64.b64decode(info['data'][0]))        

def transfer(user: pxsol.wallet.Wallet, into: pxsol.core.PubKey, amount: int) -> None:
    prog_pubkey = pxsol.core.PubKey.base58_decode('APj2A9gMDhSab7J1Nwtp7LxiZTzb8F3U4vXHLVS4aC9R')
    upda_pubkey = prog_pubkey.derive_pda(user.pubkey.p)[0]
    into_pubkey = into
    ipda_pubkey = prog_pubkey.derive_pda(into_pubkey.p)[0]
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(upda_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(into_pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(ipda_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
    rq.data = bytearray([0x01]) + bytearray(amount.to_bytes(8))
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)


if __name__ == '__main__':
    ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    if len(sys.argv) < 2:
        print("Usage: python3 make.py [mint amount | balance [pubkey] | transfer into_pubkey amount]")
        raise SystemExit(2)
    cmd = sys.argv[1]
    if cmd == "mint":
        amount = 100
        if len(sys.argv) >= 3:
            amount = int(sys.argv[2])
        mint(ada, amount)
    elif cmd == "balance":
        pubkey = ada.pubkey
        if len(sys.argv) >= 3:
            pubkey = pxsol.core.PubKey.base58_decode(sys.argv[2])
        print(balance(pubkey))
    elif cmd == "transfer":
        if len(sys.argv) < 4:
            print("Usage: python3 make.py transfer into_pubkey amount")
            raise SystemExit(2)
        into_pubkey = pxsol.core.PubKey.base58_decode(sys.argv[2])
        amount = int(sys.argv[3])
        transfer(ada, into_pubkey, amount)
        print(balance(ada.pubkey))
        print(balance(into_pubkey))
    else:
        print("Usage: python3 make.py [mint amount | balance [pubkey] | transfer into_pubkey amount]")
        raise SystemExit(2)
