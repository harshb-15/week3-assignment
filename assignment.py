from decimal import Decimal
import json, datetime
from marshmallow import Schema, fields, post_load

class Stock:
    def __init__(self, symbol, date, open, high, low, close, volume):
        self.symbol = symbol
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        
class Trade:
    def __init__(self, symbol, timestamp, order, price, volume, commission):
        self.symbol = symbol
        self.timestamp = timestamp
        self.order = order
        self.price = price
        self.commission = commission
        self.volume = volume

def custom_decoder(arg):
    if 'objectType' in arg:
        if arg['objectType'] == 'date':
            return 
        elif arg['objectType'] == 'integer':
            return int(arg['value'])
        elif arg['objectType'] == 'stock':
            return Stock(arg['symbol'], datetime.datetime.strptime(arg['date'], '%Y-%m-%d').date(), Decimal(arg['open']), Decimal(arg['high']), Decimal(arg['low']), Decimal(arg['close']), int(arg['volume']))
        elif arg['objectType'] == 'trade':
            return Trade(arg['symbol'], datetime.datetime.strptime(arg['timestamp'], '%Y-%m-%dT%H:%M:%S'), arg['order'], Decimal(arg['price']), int(arg['volume']), Decimal(arg['commission']))
    else:
        return arg 

class CustomEncoder(json.JSONEncoder):
    def default(self, arg):
        if isinstance(arg, Stock):
            return {
                "objectType": "stock",
                "symbol":  arg.symbol,
                "date": arg.date,
                "open": arg.open,
                "high": arg.high,
                "low": arg.low,
                "close": arg.close,
                "volume": arg.volume,
            }
        elif isinstance(arg, Trade):
            return {
                "objectType": "trade",
                "symbol": arg.symbol,
                "timestamp": arg.timestamp,
                "order": arg.order,
                "price": arg.price,
                "volume": arg.volume,
                "commission": arg.commission,
            }
        elif isinstance(arg, Decimal):
            return float(arg)
        elif isinstance(arg, (datetime.datetime, datetime.date)):
            return arg.isoformat()
        else:
            super().default(arg)

activity = {
    "quotes": [
        Stock('TSLA', datetime.date(2018, 11, 22), Decimal('338.19'), Decimal('338.64'), Decimal('337.60'), Decimal('338.19'), 365_607),
        Stock('AAPL', datetime.date(2018, 11, 22), Decimal('176.66'), Decimal('177.25'), Decimal('176.64'), Decimal('176.78'), 3_699_184),
        Stock('MSFT', datetime.date(2018, 11, 22), Decimal('103.25'), Decimal('103.48'), Decimal('103.07'), Decimal('103.11'), 4_493_689)
    ],
    "trades": [
        Trade('TSLA', datetime.datetime(2018, 11, 22, 10, 5, 12), 'buy', Decimal('338.25'), 100, Decimal('9.99')),
        Trade('AAPL', datetime.datetime(2018, 11, 22, 10, 30, 5), 'sell', Decimal('177.01'), 20, Decimal('9.99'))
    ]
}

class StockSchema(Schema):
    symbol = fields.Str()
    date = fields.Date()
    open = fields.Float()
    high = fields.Float()
    low = fields.Float()
    close = fields.Float()
    volume = fields.Int()

    @post_load
    def make_request(self, data, **kwargs)->Stock:
        return Stock(**data)

class TradeSchema(Schema):
    symbol = fields.Str()
    timestamp = fields.DateTime()
    order = fields.Str()
    price = fields.Float()
    volume = fields.Int()
    commission = fields.Float()

    @post_load
    def make_request(self, data, **kwargs)->Trade:
        return Trade(**data)

def serialize_with_marshmallow(obj_):
    if isinstance(obj_, Trade):
        return TradeSchema().dumps(obj_)
    else:
        return StockSchema().dumps(obj_)

def deserialize_with_marshmallow(obj_, schema):
    return schema.loads(obj_)


# encoded = json.dumps(activity, cls=CustomEncoder, indent=2)
# print(encoded)
# decoded = json.loads(encoded, object_hook=custom_decoder)
# print(type(decoded), decoded)