{
  "compilers": {
    "solc": {
      "version": "0.8.20"
    }
  },
  "networks": {
    "sepolia": {
      "url": "${BLOCKCHAIN_RPC_URL}",
      "accounts": ["${BLOCKCHAIN_PRIVATE_KEY}"]
    }
  },
  "contracts": {
    "SatyaVerifyProvenance": {
      "chainId": 11155111
    }
  }
}
