'''Order params are used to create orders, they are created by the client.'''

import time
from math import ceil
from decimal import Decimal
from numbers import Number
from typing import Optional

from fastlob.enums import OrderSide, OrderType
from fastlob.utils import todecimal_price, todecimal_quantity
from fastlob.consts import TICK_SIZE_PRICE, TICK_SIZE_QTY, MAX_VALUE

class OrderParams:
    '''
    This class is used for instantiating orders, it is necessary because we do not want to have the system 
    performing any safety checks, or at least it should have to do as few as possible. 
    Therefore this class is used to force the user to provide valid order attributes.
    '''

    side: OrderSide
    price: Decimal
    quantity: Decimal
    otype: OrderType
    expiry: Optional[int]

    def __init__(self, side: OrderSide, price: Number, quantity: Number, otype: OrderType = OrderType.GTC,
                 expiry: Optional[Number] = None):

        OrderParams.check_args(side, price, quantity, otype, expiry)

        self.side     = side
        self.price    = todecimal_price(price)
        self.quantity = todecimal_quantity(quantity)
        self.otype    = otype
        self.expiry   = int(expiry) if expiry is not None else None

    @staticmethod
    def check_args(side: OrderSide, price: Number, quantity: Number, otype: OrderType, expiry: Optional[Number]):
        '''
        Check for args correctness. 
        This method is very important, since we do not check for this after the object is created.
        If something is wrong it raises the corresponding exception.
        '''

        if not isinstance(side, OrderSide):
            raise TypeError(f'side should of type OrderSide but is {type(side)}')

        if not isinstance(price, Number):
            raise TypeError(f'price should be of type Number but is {type(price)}')

        if not isinstance(quantity, Number):
            raise TypeError(f'quantity should be of type Number but is {type(quantity)}')

        if not isinstance(otype, OrderType):
            raise TypeError(f'ordertype should be of type OrderType but is {type(otype)}')

        if expiry and not isinstance(expiry, Number):
            raise TypeError(f'expiry should be of type Number but is {type(expiry)}')

        if otype == OrderType.GTD:
            if expiry is None: raise ValueError('order is GTD but expiry is None')

            expiry = int(expiry)
            now = ceil(time.time())
            if expiry <= now:
                raise ValueError(f'order expiry ({expiry}) is less than current timestamp ({now}), or too close')

        price_decimal = todecimal_price(price)
        quantity_decimal = todecimal_quantity(quantity)

        if price_decimal < TICK_SIZE_PRICE:
            raise ValueError(f'price ({price}) must be greater than {TICK_SIZE_PRICE}')

        if quantity_decimal < TICK_SIZE_QTY:
            raise ValueError(f'quantity ({quantity}) must be greater than {TICK_SIZE_QTY}')

        if price_decimal > MAX_VALUE:
            raise ValueError(f'price ({price}) is too large')

        if quantity_decimal > MAX_VALUE:
            raise ValueError(f'quantity ({quantity}) is too large')

    def unwrap(self) -> tuple[Decimal, Decimal, OrderType, Optional[int]]:
        return self.price, self.quantity, self.otype, self.expiry

    def __repr__(self) -> str:
        return f'OrderParams(side={self.side.name}, price={self.price}, qty={self.quantity}, ' + \
            f'type={self.otype}, expiry={self.expiry})'
