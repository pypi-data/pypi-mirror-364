import asyncio
import json

import scalecodec.utils.ss58
import sqlalchemy

from turbobt.simulator import MockedSubtensor, db


class Controller:
    def __init__(self, subtensor: MockedSubtensor):
        self.subtensor = subtensor

    async def __aenter__(self):
        self._minting = asyncio.create_task(self._mint_blocks())
        return self

    async def __aexit__(self, *args, **kwargs):
        self._minting.cancel()
        pass

    async def _mint_blocks(self):
        while True:
            await asyncio.sleep(1)  # TODO

            async with self.subtensor.db_session() as session:
                block = await db.Block.new_block(session)

                extrinsics = await session.scalars(
                    sqlalchemy.select(db.Extrinsic).filter_by(block=block.number)
                )

            for extrinsic in extrinsics:
                call_module = getattr(self.subtensor, extrinsic.call_module)
                call_function = getattr(call_module, extrinsic.call_function)
                call_args = {
                    arg["name"]: (
                        scalecodec.utils.ss58.ss58_encode(arg["value"])
                        if arg["type"] == "AccountId"
                        else arg["value"]
                    )
                    for arg in json.loads(extrinsic.call_args)
                }

                await call_function(
                    extrinsic.account_id,
                    **call_args,
                )

                extrinsic_id = f"0x{extrinsic.id.to_bytes().hex()}"

                try:
                    subscription = self.subtensor.author._subscriptions[extrinsic_id]
                except KeyError:
                    continue

                subscription.put_nowait(
                    {
                        "inBlock": block.hash,
                    },
                )
                subscription.put_nowait(
                    {
                        "finalized": block.hash,
                    },
                )

    # TODO pytest.raises (for testing extrinsics)
    # TODO pytest-httpx?    !!!!!!!!!! mockowanie bazy na daną chwilę

    async def wait_for_epoch(self):
        await self._on_epoch()

    async def _on_epoch(self):
        async with self.subtensor.db_session() as session:
            subnets = await session.scalars(sqlalchemy.select(db.Subnet))

            for subnet in subnets:
                # https://github.com/opentensor/subtensor/blob/4c9836f8cc199bc323956509f59d86d1761dd021/pallets/subtensor/src/coinbase/run_coinbase.rs#L858
                # TODO No commits to reveal until at least epoch 2.

                reveal_epoch = 1    # TODO

                # TODO
                # expired_commits = session.query(db.CRV3WeightCommits).filter(
                #     db.CRV3WeightCommits.netuid == subnet.netuid,
                #     db.CRV3WeightCommits.reveal_round < reveal_epoch,
                # )
                # expired_commits.delete()

                commits = await session.scalars(
                    sqlalchemy.select(db.CRV3WeightCommits).filter_by(
                        netuid=subnet.netuid,
                        commit_epoch=reveal_epoch,
                    ),
                )

                for commit in commits:
                    commit_data = json.loads(commit.commit)

                    # XXX do_set_weights
                    weights = [
                        db.Weights(
                            block=1,    #TODO
                            netuid=subnet.netuid,
                            validator=0,  # TODO uid
                            uid=uid,
                            weight=weight,
                        )
                        for uid, weight in zip(
                            commit_data["uids"],
                            commit_data["weights"],
                        )
                    ]

                    session.add_all(weights)

                # commits.delete()
                await session.commit()
