from tortoise import fields
from tortoise.models import Model


class Market(Model):
    id = fields.UUIDField(pk=True)
    symbol = fields.CharField(max_length=255, unique=True)
    venue = fields.CharField(max_length=50)
    last_odds = fields.FloatField(null=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "markets"
        indexes = [("updated_at", "symbol")]


class Signal(Model):
    id = fields.UUIDField(pk=True)
    market = fields.ForeignKeyField("models.Market", related_name="signals")
    trigger_type = fields.CharField(max_length=100)
    value = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "signals"
        indexes = [("created_at",)]


class Order(Model):
    id = fields.UUIDField(pk=True)
    signal = fields.ForeignKeyField("models.Signal", related_name="orders", null=True)
    venue = fields.CharField(max_length=50)
    side = fields.CharField(max_length=10)
    size = fields.FloatField()
    status = fields.CharField(max_length=50, default="pending")
    sent_at = fields.DatetimeField(null=True)
    confirmed_at = fields.DatetimeField(null=True)
    latency_ms = fields.IntField(null=True)

    class Meta:
        table = "orders"
        indexes = [("sent_at",)]


class Position(Model):
    id = fields.UUIDField(pk=True)
    market = fields.ForeignKeyField("models.Market", related_name="positions")
    venue = fields.CharField(max_length=50)
    side = fields.CharField(max_length=10)
    size = fields.FloatField()
    entry_price = fields.FloatField()
    opened_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "positions"
        indexes = [("opened_at",)]


class PnLSnapshot(Model):
    id = fields.UUIDField(pk=True)
    timestamp = fields.DatetimeField(auto_now_add=True)
    value = fields.FloatField()
    venue = fields.CharField(max_length=50)

    class Meta:
        table = "pnl_snapshots"
        indexes = [("timestamp", "venue")]
