import asyncio
import hashlib
import json

from sqlalchemy import ForeignKey, Identity, func, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    @classmethod
    def get(cls, block: str | int | None = None, **kwargs):
        query = select(cls)

        if isinstance(block, int):
            block_number = block
        elif isinstance(block, str):
            block_query = select(Block.number).filter_by(hash=block)
            block_number = select(block_query.scalar_subquery())
        else:
            block_number = select(func.max(Block.number))
        
        if kwargs:
            query = query.filter_by(**kwargs)

        return query.filter(cls.block <= block_number).order_by(cls.block.desc()).limit(1)


def default_block_hash(context):
    return Block.get_hash(
        context.get_current_parameters()["number"]
    )  # TODO number autoincrement


class Block(Base):
    __tablename__ = "Blocks"

    number: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hash: Mapped[str] = mapped_column(
        default=default_block_hash,
        index=True,
        unique=True,
    )

    extrinsics: Mapped[list["Extrinsic"]] = relationship()

    on_created = asyncio.Queue()

    @classmethod
    async def new_block(cls, session):
        block_id = await session.scalar(select(func.max(cls.number)).with_for_update())
        block = cls(
            number=block_id + 1,
        )

        session.add(block)

        await session.commit()

        return block

    @classmethod
    def get_hash(cls, block_number: int):
        return f"0x{hashlib.sha256(bytes(block_number)).hexdigest()}"

    @classmethod
    def query(cls, block: str | int | None = None):
        # TODO limit(1)

        if isinstance(block, int):
            return select(cls).filter_by(number=block).limit(1)

        if isinstance(block, str):
            return select(cls).filter_by(hash=block).limit(1)

        return select(cls).order_by(cls.number.desc()).limit(1)


# TODO wygodne metody do parsowania (inwestygowania) coś jak alternatywa dla spy
class Extrinsic(Base):
    __tablename__ = "Extrinsics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    block: Mapped[int] = mapped_column(ForeignKey("Blocks.number"))

    account_id: Mapped[str]
    call_args: Mapped[str]  # TODO type
    call_function: Mapped[str]
    call_module: Mapped[str]
    era_current: Mapped[int]
    era_period: Mapped[int]
    nonce: Mapped[int]
    signature: Mapped[str]
    tip: Mapped[int]
    # mode

    def encode(self, substrate):
        extrinsic = substrate._registry.create_scale_object(
            "Extrinsic",
            metadata=substrate._metadata,
        )
        extrinsic.encode(
            {
                "account_id": self.account_id,
                "asset_id": {"tip": self.tip, "asset_id": None},
                "call_args": json.loads(self.call_args),
                "call_function": self.call_function,
                "call_module": self.call_module,
                "era": {
                    "current": self.era_current,
                    "period": self.era_period,
                },
                "mode": "Disabled",
                "nonce": self.nonce,
                "signature_version": 1,
                "signature": self.signature,
                "tip": self.tip,
            },
        )

        return str(extrinsic.data)


class Subnet(Base):
    __tablename__ = "Subnets"

    netuid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    block: Mapped[int] = mapped_column(ForeignKey("Blocks.number"))
    name: Mapped[str]
    token_symbol: Mapped[str]
    owner_coldkey: Mapped[str]
    owner_hotkey: Mapped[str]
    tempo: Mapped[int]
    identity: Mapped[str]

    @classmethod
    def get(cls, netuid: int, block: str | int | None = None):
        return super().get(block).filter_by(netuid=netuid)


class SubnetHyperparams(Base):
    __tablename__ = "SubnetHyperparams"

    netuid: Mapped[int] = mapped_column(primary_key=True)
    block: Mapped[int] = mapped_column(ForeignKey("Blocks.number"))

    activity_cutoff: Mapped[int] = 5000
    adjustment_alpha: Mapped[int] = 17893341751498265066    # 18_446_744_073_709_551_615 * 0.97
    adjustment_interval: Mapped[int] = 360
    alpha_high: Mapped[int] = 58982
    alpha_low: Mapped[int] = 45875
    bonds_moving_avg: Mapped[int] = 900000
    commit_reveal_period: Mapped[int] = 1
    commit_reveal_weights_enabled: Mapped[bool] = False
    difficulty: Mapped[int] = 10000000
    immunity_period: Mapped[int] = 5000
    kappa: Mapped[int] = 32767
    liquid_alpha_enabled: Mapped[bool] = False
    max_burn: Mapped[int] = 100000000000
    max_difficulty: Mapped[int] = 18446744073709551615
    max_regs_per_block: Mapped[int] = 1
    max_validators: Mapped[int] = 64
    max_weights_limit: Mapped[int] = 65535
    min_allowed_weights: Mapped[int] = 1
    min_burn: Mapped[int] = 500000
    min_difficulty: Mapped[int] = 18446744073709551615
    registration_allowed: Mapped[bool] = True
    rho: Mapped[int] = 10
    serving_rate_limit: Mapped[int] = 50
    target_regs_per_interval: Mapped[int] = 1
    tempo: Mapped[int] = 100
    weights_rate_limit: Mapped[int] = 100
    weights_version: Mapped[int] = 0
    
    @classmethod
    def get(cls, netuid: int, block: str | int | None = None):
        query = select(cls).filter_by(netuid=netuid)

        if isinstance(block, int):
            block_number = block
        elif isinstance(block, str):
            block_query = select(Block.number).filter_by(hash=block)
            block_number = select(block_query.scalar_subquery())
        else:
            block_number = select(func.max(Block.number))

        return query.filter(cls.block <= block_number).order_by(cls.block.desc()).limit(1)


class Neuron(Base):
    __tablename__ = "Neurons"

    uid: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    netuid: Mapped[int] = mapped_column(ForeignKey("Subnets.netuid"))
    block: Mapped[int] = mapped_column(ForeignKey("Blocks.number"))
    active: Mapped[bool]
    coldkey: Mapped[str]
    hotkey: Mapped[str]
    consensus: Mapped[int] = 0
    dividends: Mapped[int] = 0
    emission: Mapped[int] = 0
    incentive: Mapped[int] = 0
    last_update: Mapped[int] = 0
    pruning_score: Mapped[int] = 65535
    rank: Mapped[int] = 0
    trust: Mapped[int] = 0
    validator_permit: Mapped[bool] = False
    validator_trust: Mapped[int] = 0

    axon_info: Mapped["AxonInfo"] = relationship(back_populates="neuron")
    # certificate: Mapped["NeuronCertificate"] = relationship(back_populates="neuron")


class NeuronCertificate(Base):
    __tablename__ = "NeuronCertificates"

    block: Mapped[int] = mapped_column(ForeignKey("Blocks.number"))
    netuid: Mapped[int] = mapped_column(ForeignKey("Subnets.netuid"))
    hotkey: Mapped[str] = mapped_column(ForeignKey("Neurons.hotkey"), primary_key=True)
    algorithm: Mapped[int]
    public_key: Mapped[bytes]

    # neuron: Mapped["Neuron"] = relationship(back_populates="certificate")


class AxonInfo(Base):
    __tablename__ = "AxonInfo"

    block: Mapped[int] = mapped_column(ForeignKey("Blocks.number"))
    uid: Mapped[int] = mapped_column(ForeignKey("Neurons.uid"), primary_key=True)
    netuid: Mapped[int] = mapped_column(ForeignKey("Subnets.netuid"))
    ip: Mapped[str]
    port: Mapped[int]
    protocol: Mapped[int]

    neuron: Mapped["Neuron"] = relationship(back_populates="axon_info")


# XXX
class StorageDoubleMap(Base):
    __tablename__ = "StorageDoubleMap"

    module: Mapped[str]
    storage: Mapped[str]
    block: Mapped[int] = mapped_column(ForeignKey("Blocks.number"))

    key1: Mapped[int] = mapped_column(primary_key=True)
    key2: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[bytes] = mapped_column(nullable=True)


class CRV3WeightCommits(Base):
    __tablename__ = "CRV3WeightCommits"

    netuid: Mapped[int] = mapped_column(primary_key=True)
    commit_epoch: Mapped[int] = mapped_column(primary_key=True)
    who: Mapped[str]
    commit: Mapped[bytes]
    reveal_round: Mapped[int]


class Weights(Base):
    __tablename__ = "Weights"

    block: Mapped[int] = mapped_column(ForeignKey("Blocks.number"))
    netuid: Mapped[int] = mapped_column(primary_key=True)
    validator: Mapped[int] = mapped_column(primary_key=True)

    uid: Mapped[int]
    weight: Mapped[int]
