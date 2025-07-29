
import anchorpy
from anchorpy import Idl, Provider, Wallet
import solders
from shadowPaySDK.interface.sol import SOL
import solders  
import spl.token.constants as spl_constants
from solana.rpc.api import Client

import asyncio
import solana
from solana.rpc.async_api import AsyncClient, GetTokenAccountsByOwnerResp

from solders.transaction import Transaction
from solders.system_program import TransferParams as p
from solders.instruction import Instruction, AccountMeta
from solders.rpc.config import RpcSendTransactionConfig
from solders.message import Message
import spl
import spl.token
import spl.token.constants
from spl.token.instructions import get_associated_token_address, create_associated_token_account, TransferCheckedParams, transfer_checked, transfer, close_account, TransferParams
from solders.system_program import transfer as ts
from solders.system_program import TransferParams as tsf
from solders.pubkey import Pubkey
import os
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from solana.rpc.types import TxOpts, TokenAccountOpts
from solana.rpc.types import TxOpts
import solders
from solders.message import Message
from solders.system_program import create_account,CreateAccountParams

# from solders.pubkey import Pubkey
# from solders.keypair import Keypair
# from solders.signature import Signature
# from solders.transaction import Transaction
from spl.token.async_client import AsyncToken


from solana.rpc.commitment import Confirmed
from solana.rpc.async_api import AsyncClient
import anchorpy
from anchorpy import Provider, Wallet, Idl
import pprint
import httpx
import base64
import re
import struct
from shadowPaySDK.const import LAMPORTS_PER_SOL, PROGRAM_ID, CONFIG_PDA



class SOLCheque:
        def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com", key: Wallet = None):
            self.rpc_url = rpc_url
            if key:
                self.key = solders.keypair.Keypair.from_base58_string(key)
            self.provider = Client(rpc_url)
            self.WRAPED_SOL = spl_constants.WRAPPED_SOL_MINT    # wrapped SOL token mint address
            # self.idl = Idl.from_json(sol_interface.Idl)  # Load the IDL for the program
        def get(self, keypair = None):
              pubkey = SOL.get_pubkey(KEYPAIR=solders.keypair.Keypair.from_base58_string(self.keystore))

              return pubkey
        def get_config(self):
            program_id = PROGRAM_ID
            config_pda, _ = Pubkey.find_program_address([b"config"], program_id)

            response = self.provider.get_account_info(config_pda)
            if response.value is None:
                print("❌ Config PDA not found.")
                return None

            raw = bytes(response.value.data)

            if len(raw) < 89:
                print("❌ Invalid config data length.")
                return None

            admin = Pubkey.from_bytes(raw[0:32])
            treasury = Pubkey.from_bytes(raw[32:64])
            fee_bps = struct.unpack("<Q", raw[64:72])[0]
            token_in_bps = struct.unpack("<Q", raw[72:80])[0]
            token_out_bps = struct.unpack("<Q", raw[80:88])[0]
            initialized = bool(raw[88])

            
            return {
                "pda": str(config_pda),
                "admin": str(admin),
                "treasury": str(treasury),
                "fee_bps": fee_bps,
                "token_in_bps": token_in_bps,
                "token_out_bps": token_out_bps,
                "initialized": initialized,
            }
        def parse_cheque_data(self, pda):
            if isinstance(pda, str):
                pda_pubkey = Pubkey.from_string(pda)
            response = self.provider.get_account_info(pda_pubkey)
            if response.value is None:
                return None
            
            raw_data = bytes(response.value.data)
            id = int.from_bytes(raw_data[0:8], "little")
            amount = int.from_bytes(raw_data[8:16], "little")
            recipient = Pubkey.from_bytes(raw_data[16:48])
            claimed = raw_data[48] != 0
            owner = Pubkey.from_bytes(raw_data[49:81])  

            return {
                "id": id,
                "amount": amount,
                "recipient": str(recipient),
                "claimed": claimed,
                "owner": str(owner),
            }
        def parse_token_cheque_data(self,pda):
            if isinstance(pda, str):
                pda_pubkey = Pubkey.from_string(pda)
            pda_pubkey = pda
            response = self.provider.get_account_info(pda_pubkey)
            if response.value is None:
                return None
            
            raw_data = bytes(response.value.data)
            id = int.from_bytes(raw_data[0:8], "little")
            amount = int.from_bytes(raw_data[8:16], "little")
            mint = Pubkey.from_bytes(raw_data[16:48])
            recipient = Pubkey.from_bytes(raw_data[48:80])
            claimed = raw_data[80] != 0
            owner = Pubkey.from_bytes(raw_data[81:113])  

            return {
                "id": id,
                "amount": amount,
                "mint": str(mint),
                "recipient": str(recipient),
                "claimed": claimed,
                "owner": str(owner),
            }
        def parse_swap_cheque_data(self,pda:str):
            if isinstance(pda, str):
                pda_pubkey = Pubkey.from_string(pda)
            response = self.provider.get_account_info(pda_pubkey)
            if response.value is None:
                return None
            
            raw_data = bytes(response.value.data)
            amountIn = struct.unpack("<Q", raw_data[0:8])[0]
            amountOut = struct.unpack("<Q", raw_data[8:16])[0]
            tokenIn = Pubkey.from_bytes(raw_data[16:48])
            tokenOut = Pubkey.from_bytes(raw_data[48:80])
            recipient = Pubkey.from_bytes(raw_data[80:112])
            claimed = struct.unpack("<?", raw_data[112:113])[0]
            owner = Pubkey.from_bytes(raw_data[113:145])  
            return {
                "id": id,
                "amountIn": amountIn,
                "amountOut": amountOut,
                
                "tokenIn": str(tokenIn),
                "tokenOut": str(tokenOut),
               
                "recipient": str(recipient),
                "claimed": claimed,
                "owner": str(owner)
            }
        def set_params(self, rpc_url = None, key = None):
            if rpc_url:
                self.rpc_url = rpc_url
                self.provider = Client(rpc_url)
            if key:
                self.key = solders.keypair.Keypair.from_base58_string(key)
        # init_cheque & claim_cheque status on 15.07.2025 work

        async def init_cheque(self, cheque_amount, recipient: str, SPACE: int = 85, build_tx: bool = False):
            """
            Initialize a cheque withc the specified amount and recipient.
            """
            # if not self.key:
            #     raise ValueError("Keypair is not set. Please set the keypair before initializing a cheque.")
            CHEQUE_PDA_SIGNATURE = None
            CHEQUE_SPACE = SPACE  
            CHEQUE_RENT = self.provider.get_minimum_balance_for_rent_exemption(CHEQUE_SPACE)
            sol = SOL(
                KEYPAIR=self.key  
            )
            payer = self.key
            pubkey = self.key.pubkey()
            newAcc = solders.keypair.Keypair()
            newAccPubkey = newAcc.pubkey()
            ix_create = create_account(
                params=CreateAccountParams(
                from_pubkey=pubkey,
                to_pubkey=newAccPubkey,
                lamports=CHEQUE_RENT.value,
                space=CHEQUE_SPACE,
                owner=PROGRAM_ID
                )
            )
            recent_blockhash = self.provider.get_latest_blockhash().value.blockhash
            message = Message(instructions=[ix_create], payer=pubkey)

            t = Transaction(message=message, from_keypairs=[payer, newAcc], recent_blockhash=recent_blockhash)
            
            r = self.provider.send_transaction(t,opts=TxOpts())
            CHEQUE_PDA_SIGNATURE = r.value
            CHEQUE_PDA = newAccPubkey  



            total_lamports = int(cheque_amount * LAMPORTS_PER_SOL)


            r = Pubkey.from_string(recipient)  

            data = bytes([0]) + bytes(r) + struct.pack("<Q", total_lamports)

            cfg = self.get_config()
            tresury = cfg["treasury"]
            instruction = Instruction(
                program_id=PROGRAM_ID,
                data=data,  
                accounts=[
                    AccountMeta(pubkey=pubkey, is_signer=True, is_writable=True),     # payer
                    AccountMeta(pubkey=CHEQUE_PDA, is_signer=False, is_writable=True), # cheque PDA
                    AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),
                    AccountMeta(pubkey=Pubkey.from_string(tresury), is_signer=False, is_writable=True),  # treasury

                ]
            )

            recent_blockhash = self.provider.get_latest_blockhash().value.blockhash
            message = Message(instructions=[instruction], payer=pubkey)
            tx = Transaction(message=message, from_keypairs=[payer], recent_blockhash=recent_blockhash)
            response = self.provider.send_transaction(tx,opts=TxOpts(skip_preflight=True))
            confirm = self.provider.confirm_transaction(response.value)
            
            data = {
                "cheque_pda": str(CHEQUE_PDA),
                "signature": str(response.value),
                "create_signature": str(CHEQUE_PDA_SIGNATURE),
                "cheque_amount": cheque_amount,
                "pda_rent_sol": CHEQUE_RENT.value / LAMPORTS_PER_SOL,
            }
            return data

        async def claim_cheque(self, pda_acc: str ):
            instruction_data = bytes([1])
            payer = self.key
            payer_pubkey = payer.pubkey()
            cfg = self.get_config()   
            tressary = cfg["treasury"]
            cheque_data = self.parse_cheque_data(pda=solders.keypair.Keypair.from_base58_string(pda_acc).pubkey())
            owner = cheque_data["owner"]


            ix = Instruction(
                program_id=PROGRAM_ID,
                data=instruction_data,
                accounts = [
                    AccountMeta(pubkey=payer_pubkey, is_signer=True, is_writable=True),
                    AccountMeta(pubkey=Pubkey.from_string(pda_acc), is_signer=False, is_writable=True),
                    AccountMeta(pubkey=CONFIG_PDA[0], is_signer=False, is_writable=True),  
                    AccountMeta(pubkey=Pubkey.from_string(tressary), is_signer=False, is_writable=True),  
                    AccountMeta(pubkey=Pubkey.from_string(cheque_data["owner"]), is_signer=False, is_writable=True),  
                ]
            )

            recent_blockhash = self.provider.get_latest_blockhash().value.blockhash
            message = Message(instructions=[ix], payer=payer_pubkey)
            tx = Transaction(message=message, from_keypairs=[payer], recent_blockhash=recent_blockhash)
            response = self.provider.send_transaction(tx,opts=TxOpts(skip_preflight=True))
            return {
                "signature": str(response.value),
                "pda_account": pda_acc,
            }

        # init_token_cheque work succesfuly

        async def init_token_cheque(
            self,
            token_mint: str,
            token_amount,
            recipient: str,
            CHEQUE_SPACE: int = 115
        ):
            if not self.key:
                raise ValueError("Keypair not set")

            payer = self.key
            payer_pubkey = payer.pubkey()

            token_mint_pubkey = Pubkey.from_string(token_mint)
            recipient_pubkey = Pubkey.from_string(recipient)

            cheque_acc = solders.keypair.Keypair()
            cheque_pubkey = cheque_acc.pubkey()

            rent = self.provider.get_minimum_balance_for_rent_exemption(CHEQUE_SPACE).value

            create_cheque_ix = create_account(
                CreateAccountParams(
                    from_pubkey=payer_pubkey,
                    to_pubkey=cheque_pubkey,
                    lamports=rent,
                    space=CHEQUE_SPACE,
                    owner=PROGRAM_ID
                )
            )

            blockhash = self.provider.get_latest_blockhash().value.blockhash

            tx1 = Transaction(
                message=Message(instructions=[create_cheque_ix], payer=payer_pubkey),
                recent_blockhash=blockhash,
                from_keypairs=[payer, cheque_acc]
            )
            self.provider.send_transaction(tx1, opts=TxOpts(skip_preflight=True))

            

            ata_ix = create_associated_token_account(
                payer=payer_pubkey,
                owner=cheque_pubkey,
                mint=token_mint_pubkey
            )
            cfg = self.get_config()   
            tressary = cfg["treasury"]
            sender_ata = get_associated_token_address(payer_pubkey, token_mint_pubkey)
            cheque_ata = get_associated_token_address(cheque_pubkey, token_mint_pubkey)
            client = AsyncClient(self.rpc_url)
            token = AsyncToken(
                client,
                Pubkey.from_string(token_mint),
                TOKEN_PROGRAM_ID,
                self.key
            )
            token_decimals = (await token.get_mint_info()).decimals
            amount = int(token_amount * (10 ** token_decimals))
            data = bytes([2]) + struct.pack("<Q", amount) + bytes(recipient_pubkey)

            ix_program = Instruction(
                program_id=PROGRAM_ID,
                data=data,
                accounts=[
                    AccountMeta(pubkey=payer_pubkey, is_signer=True, is_writable=True),         # 0 initializer
                    AccountMeta(pubkey=cheque_pubkey, is_signer=True, is_writable=True),        # 1 cheque_pda
                    AccountMeta(pubkey=token_mint_pubkey, is_signer=False, is_writable=True),   # 2 mint
                    AccountMeta(pubkey=sender_ata, is_signer=False, is_writable=True),          # 3 sender ATA
                    AccountMeta(pubkey=cheque_ata, is_signer=False, is_writable=True),          # 4 cheque ATA
                    AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),   # 5 token program
                    AccountMeta(pubkey=CONFIG_PDA[0], is_signer=False, is_writable=False),      # 6 config PDA
                    AccountMeta(pubkey=Pubkey.from_string(tressary), is_signer=False, is_writable=True),        # 7 treasury ATA
                ]
            )



            blockhash = self.provider.get_latest_blockhash().value.blockhash
            tx2 = Transaction(
                message=Message(instructions=[ata_ix, ix_program], payer=payer_pubkey),
                recent_blockhash=blockhash,
                from_keypairs=[payer, cheque_acc]
            )

            sig = self.provider.send_transaction(tx2, opts=TxOpts(skip_preflight=True)).value

            return {
                "cheque_pubkey": str(cheque_pubkey),
                "cheque_pda": str(cheque_acc),
                "signature": str(sig),
                "amount": token_amount
            }


        async def claim_token_cheque(self,  pda_acc: str):

            payer = self.key
            payer_pubkey = payer.pubkey()
            pada_acc = solders.keypair.Keypair.from_base58_string(pda_acc)
            pda_pubkey = pada_acc.pubkey()
            cheque_data = self.parse_token_cheque_data(pda=solders.keypair.Keypair.from_base58_string(pda_acc).pubkey())
            owner = cheque_data["owner"]    
            cheque_token_account = get_associated_token_address(pda_pubkey, Pubkey.from_string(cheque_data["mint"]))
            recipient_token_account = get_associated_token_address(
                Pubkey.from_string(cheque_data["recipient"]), Pubkey.from_string(cheque_data["mint"])
            )
            cfg = self.get_config()   
            tressary = cfg["treasury"]
            data = bytes([3])
            ix_program = Instruction(
                program_id=PROGRAM_ID,
                data=bytes([3]),
                accounts=[
                    AccountMeta(pubkey=payer_pubkey, is_signer=True, is_writable=True),                # 0 claimer
                    AccountMeta(pubkey=pda_pubkey, is_signer=False, is_writable=True),                 # 1 cheque_pda
                    AccountMeta(pubkey=cheque_token_account, is_signer=False, is_writable=True),       # 2 cheque_token_account
                    AccountMeta(pubkey=recipient_token_account, is_signer=False, is_writable=True),    # 3 recipient_token_account
                    AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),          # 4 token_program
                    AccountMeta(pubkey=CONFIG_PDA[0], is_signer=False, is_writable=False),             # 5 config_account
                    AccountMeta(pubkey=Pubkey.from_string(tressary), is_signer=False, is_writable=True), # 6 treasury_account
                ]
            )





            blockhash = self.provider.get_latest_blockhash().value.blockhash

            tx = Transaction(
                message=Message(instructions=[ix_program], payer=payer_pubkey),
                recent_blockhash=blockhash,
                from_keypairs=[payer]
            )

            sig = self.provider.send_transaction(tx, opts=TxOpts(skip_preflight=True)).value

            return {
                "pda_pubkey": str(pda_pubkey),
                "signature": str(sig)
            }
        
        async def init_swap_cheque(self,tokenIn, tokenOut, amoutIn, amountOut,recepient,CHEQUE_SPACE = 150):
            client = AsyncClient(self.rpc_url)
            tokenA = AsyncToken(
                client,
                Pubkey.from_string(tokenIn),
                TOKEN_PROGRAM_ID,
                self.key
            )
            tokenInDecimals = (await tokenA.get_mint_info()).decimals
            tokenB = AsyncToken(
                client,
                Pubkey.from_string(tokenOut),
                TOKEN_PROGRAM_ID,
                self.key
            )
                
            tokenOutDecimals = (await tokenB.get_mint_info()).decimals
            amoutIn = int(amoutIn * (10 ** tokenInDecimals))
            amountOut = int(amountOut * (10 ** tokenOutDecimals))
            cheque_acc = solders.keypair.Keypair()
            cheque_pubkey = cheque_acc.pubkey()
            payer_pubkey = self.key.pubkey() 
            rent = self.provider.get_minimum_balance_for_rent_exemption(CHEQUE_SPACE).value

            create_cheque_ix = create_account(
                CreateAccountParams(
                    from_pubkey=payer_pubkey,
                    to_pubkey=cheque_pubkey,
                    lamports=rent,
                    space=CHEQUE_SPACE,
                    owner=PROGRAM_ID
                )
            )
            blockhash = self.provider.get_latest_blockhash().value.blockhash

            tx1 = Transaction(
                message=Message(instructions=[create_cheque_ix], payer=payer_pubkey),
                recent_blockhash=blockhash,
                from_keypairs=[self.key, cheque_acc]
            )
            self.provider.send_transaction(tx1, opts=TxOpts(skip_preflight=True))
            
            ix_create_ata = create_associated_token_account(
                payer=payer_pubkey,
                owner=cheque_pubkey,
                mint=Pubkey.from_string(tokenIn)
            )
            if tokenIn != tokenOut:
                ix_create_ata_out = create_associated_token_account(
                    payer=payer_pubkey,
                    owner=cheque_pubkey,
                    mint=Pubkey.from_string(tokenOut)
                )
                tx_create_ata_out = Transaction(
                    message=Message(instructions=[ix_create_ata_out], payer=payer_pubkey),
                    recent_blockhash=blockhash,
                    from_keypairs=[self.key]
                )
                sig = self.provider.send_transaction(tx_create_ata_out, opts=TxOpts(skip_preflight=True))
                print("create ata out",sig.value)
                                               
            
           

            sender_ata = get_associated_token_address(payer_pubkey, Pubkey.from_string(tokenIn))
            cheque_ata = get_associated_token_address(cheque_pubkey, Pubkey.from_string(tokenIn))


            data = bytes([4]) + struct.pack("<Q", amoutIn) + struct.pack("<Q", amountOut) + bytes(Pubkey.from_string(recepient))
            swap_cheque = Instruction(
                program_id=PROGRAM_ID,
                data=data,
                accounts=[
                    AccountMeta(payer_pubkey, is_signer=True,is_writable=True),
                    AccountMeta(cheque_pubkey, is_signer=True, is_writable=True),
                    AccountMeta(Pubkey.from_string(tokenIn), is_signer=False, is_writable=False),
                    AccountMeta(Pubkey.from_string(tokenOut), is_signer=False, is_writable=False),
                    AccountMeta(sender_ata, is_signer=False, is_writable=True),
                    AccountMeta(cheque_ata, is_signer=False,is_writable=True),
                    AccountMeta(TOKEN_PROGRAM_ID, is_signer=False,is_writable=False)

                ]
            )
            
            blockhash = self.provider.get_latest_blockhash().value.blockhash

            tx2 = Transaction(
                message=Message(instructions=[ix_create_ata,swap_cheque], payer=payer_pubkey),
                recent_blockhash=blockhash,
                from_keypairs=[self.key, cheque_acc]
            )
            sig = self.provider.send_transaction(tx2, opts=TxOpts(skip_preflight=True)).value
            return {
                "cheque_key": str(cheque_acc),
                "cheque_pda": str(cheque_pubkey),
                "signature": str(sig)
            }
        async def claim_swap_cheque(self, pda_acc: str):
            pda_pubkey = solders.keypair.Keypair.from_base58_string(pda_acc).pubkey()

            swap_data = await self.parse_swap_cheque_data(pda=pda_pubkey)
            tokenIn = swap_data["tokenIn"]
            tokenOut = swap_data["tokenOut"]
            recipient = swap_data["recipient"]
            claimed = swap_data["claimed"]
            cfg = self.get_config()
            tressary = cfg["treasury"]
            sender_ata = get_associated_token_address(self.key.pubkey(), Pubkey.from_string(tokenIn))
            cheque_ata = get_associated_token_address(pda_pubkey, Pubkey.from_string(tokenOut))
            recepient_ata = get_associated_token_address(Pubkey.from_string(recipient), Pubkey.from_string(tokenOut))

            data = bytes([5])
            claim_tx = Instruction(
                program_id=PROGRAM_ID,
                data=data,
                accounts=[
                    AccountMeta(self.key.pubkey(), is_signer=True, is_writable=True),  # claimer
                    AccountMeta(pda_pubkey, is_signer=False, is_writable=True),  # cheque_pda
                    AccountMeta(sender_ata, is_signer=False, is_writable=True),  # sender ATA
                    AccountMeta(cheque_ata, is_signer=False, is_writable=True),  # cheque ATA
                    AccountMeta(recepient_ata, is_signer=False, is_writable=True),  # recipient ATA
                    AccountMeta(Pubkey.from_string(tokenIn), is_signer=False, is_writable=False),  # tokenIn mint
                    AccountMeta(Pubkey.from_string(tokenOut), is_signer=False, is_writable=False),  # tokenOut mint
                    AccountMeta(TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),  # token program
                    AccountMeta(CONFIG_PDA[0], is_signer=False, is_writable=False),  # config PDA
                    AccountMeta(Pubkey.from_string(tressary), is_signer=False, is_writable=True)  # treasury ATA
                ]
            )
            blockhash = self.provider.get_latest_blockhash().value.blockhash
            tx = Transaction(
                blockhash=blockhash,
                message=Message(instructions=[claim_tx], payer=self.key.pubkey()),
                from_keypairs=[self.key]  # Use the keypair to sign the transaction
            )
            sig = self.provider.send_transaction(txn=claim_tx, opts=TxOpts(skip_preflight=True)).value
            return{
                "pda_pubkey": str(pda_pubkey),
                "signature": str(sig)
            }
                        # "id": id,
            #     "amountIn": amountIn,
            #     "amountOut": amountOut,
                
            #     "tokenIn": str(tokenIn),
            #     "tokenOut": str(tokenOut),
               
            #     "recipient": str(recipient),
            #     "claimed": claimed,
