import typing


class ObjectDict(dict):
    def __getattr__(self, name: str) -> typing.Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: typing.Any):
        self[name] = value


develop = ObjectDict({
    # The default state of a commitment, one of the confirmed or finalized.
    'commitment': 'confirmed',
    # Display log output.
    'log': 0,
    'rpc': ObjectDict({
        # Many solana public nodes will limit the number of rpc requests. Add a fixed cooldown time.
        'cooldown': 0.2,
        # Endpoint.
        'url': 'http://127.0.0.1:8899',
    }),
})

mainnet = ObjectDict({
    'commitment': 'confirmed',
    'log': 0,
    'rpc': ObjectDict({
        'cooldown': 1,
        'url': 'https://api.mainnet-beta.solana.com',
    }),
})

testnet = ObjectDict({
    'commitment': 'confirmed',
    'log': 0,
    'rpc': ObjectDict({
        'cooldown': 1,
        'url': 'https://api.devnet.solana.com',
    }),
})


current = develop
