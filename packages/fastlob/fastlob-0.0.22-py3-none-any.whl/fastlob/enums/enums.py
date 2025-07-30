'''All the project enumerations are grouped here for simplicity.'''

from enum import Enum

class OrderSide(Enum):
    '''The side of an order/limit, can be BID or ASK.'''

    BID = False
    '''The bid (buy) side.'''
    ASK = True
    '''The ask (sell) side.'''

    @staticmethod
    def invert(side):
        '''Invert the side and return it.'''
        return OrderSide.BID if side == OrderSide.ASK else OrderSide.ASK

class OrderType(Enum):
    '''The type of the order, can be FOK, GTC or GTD.'''

    FOK = 1
    '''A fill or kill (FOK) order is a conditional order requiring the transaction to be executed immediately and to 
    its full amount at a stated price. If any of the conditions are broken, then the order must be automatically 
    canceled (kill) right away.'''
    GTC = 2
    '''A Good-Til-Cancelled (GTC) order is an order to buy or sell a stock that lasts until the order is completed 
    or canceled.
    '''
    GTD = 3
    '''A Good-Til-Day (GTD) order is a type of order that is active until its specified date (UTC seconds timestamp), 
    unless it has already been fulfilled or cancelled.
    '''
    FAKE = 4
    '''Used when running lob with historical data.'''

class OrderStatus(Enum):
    '''The status of an order.'''

    CREATED = 1
    '''Order created but not in a limit queue or executed yet.'''
    PENDING = 2
    '''Order in line in limit to be filled but not modified in any ways yet.'''
    FILLED = 3
    '''Order entirely filled, not in limit.'''
    PARTIAL = 4
    '''Order partially filled.'''
    CANCELED = 5
    '''Order canceled, can not be fully or partially filled anymore.'''
    ERROR = 6
    '''Set by the lob if the order can not be processed.'''

    @staticmethod
    def valid_states() -> set:
        '''Returns the set of states in which an order is considered valid.'''
        return {OrderStatus.CREATED, OrderStatus.PENDING, OrderStatus.PARTIAL}

class ResultType(Enum):
    '''The type of execution result.'''

    LIMIT = 1
    '''If the order was placed in a limit.'''
    MARKET = 2
    '''If the order was executed as market.'''
    PARTIAL_MARKET = 3
    '''If the order was partially executed as market, and then placed in limit.'''
    CANCEL = 4
    '''If the operation was an order cancellation.'''
    ERROR = 5
    '''If the query could not be processed by the lob.'''

    def in_limit(self) -> bool:
        '''True if the operation results in the order sitting in the limit.'''
        return self in {ResultType.LIMIT, ResultType.PARTIAL_MARKET}
