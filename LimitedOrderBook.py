from os import getsid
from shutil import which
from typing import Dict, List
import yaml
from dataclasses import dataclass
import collections

class PriceLevel:
    def __init__(self, price, quantity, order_id) -> None:
        self.price_dict = collections.defaultdict(list)
        self.price_dict[price] = [(order_id, quantity)]


@dataclass
class Order:
    stock_ticker: str
    price: float
    quantity: int
    side: int

class OrderBooks:
    def __init__(self) -> None:
        self.buybook = collections.defaultdict(dict)
        self.sellbook = collections.defaultdict(dict)
        self.idbook = collections.defaultdict(Order)
    
    def on_new_order(self, order_id, stock_ticker, price, quantity, side):
        if order_id not in self.idbook:
            self.idbook[order_id] = Order(
                stock_ticker=stock_ticker,
                price=price,
                quantity=quantity,
                side=side)
        
        whichbook = self.buybook if side else self.sellbook

        if stock_ticker not in whichbook:
            whichbook[stock_ticker] = PriceLevel(price=price, quantity=quantity,order_id=order_id)
        else:
            curr_prc_lv = whichbook[stock_ticker]
            if price not in curr_prc_lv.price_dict:
                curr_prc_lv.price_dict[price] = [(order_id, quantity)]
            else:
                curr_prc_lv.price_dict[price].append((order_id, quantity))
            # whichbook[stock_ticker] = curr_prc_lv
        
    def on_cancelled_order(self, order_id, quantity_to_cancel):
        myorder = self.idbook[order_id]
        if quantity_to_cancel > myorder.quantity:
            raise Exception('overload quantity')
        else:
            myorder.quantity -= quantity_to_cancel
        getbook = self.buybook if myorder.side else self.sellbook
        pricebook = getbook[myorder.stock_ticker]
        myprclv = pricebook.price_dict[myorder.price]
        od_position = 0
        for i, obj in enumerate(myprclv):
            od, q = obj
            if od == order_id:
                od_position = i
        myprclv[od_position] = (order_id, myorder.quantity)
        
        
    def on_executed_order(self, order_id, quantity_excuted):
        myorder = self.idbook[order_id]
        if quantity_excuted > myorder.quantity:
            raise Exception('overload quantity')
        else:
            myorder.quantity -= quantity_excuted
        getbook = self.buybook if myorder.side else self.sellbook
        pricebook = getbook[myorder.stock_ticker]
        myprclv = pricebook.price_dict[myorder.price]
        od_position = 0
        for i, obj in enumerate(myprclv):
            od, q = obj
            if od == order_id:
                od_position = i
        myprclv[od_position] = (order_id, myorder.quantity)
        

book = OrderBooks()

def on_new_order(order_id, stock_ticker, price, quantity, side):
    book.on_new_order(order_id, stock_ticker, price, quantity, side)


def on_cancelled_order(order_id, quantity_to_cancel):
    book.on_cancelled_order(order_id, quantity_to_cancel)


def on_executed_order(order_id, quantity_excuted):
    book.on_executed_order(order_id, quantity_excuted)

# Return format:
# - List of Price levels (list)
#   - Price level (tuple)
#       - Price (float)
#       - Total quantity (int)
#       - List of order IDs (list of ints)
def top(n, stock_ticker, side):
    mybook = book.buybook if side else book.sellbook
    mypricebook = mybook[stock_ticker].price_dict
    mypricelv = sorted(mypricebook)
    if side:
        if n < len(mypricelv):
            prc_q = [mypricebook[prc] for prc in mypricelv]
            ttlq = sum([prctuple[1] for prctuple in ttlq])

        else:
            return [mypricebook[pl] for pl in mypricelv]
    else:
        if n < len(mypricelv):
            return [mypricebook[pl] for pl in reversed(mypricelv)[:n]]
        else:
            return [mypricebook[pl] for pl in reversed(mypricelv)]
    # print(reversed(sorted(mypricebook)))
    # return [mypricelv[pl] for pl in mypricelv]
    


with open("orders.yml", "r") as stream:
    try:
        raw_orders = yaml.safe_load(stream)
    except Exception as e:
        print(e)

order_objs = raw_orders["orders_ex0"]
# order_objs2 = raw_orders["orders_ex1"]
# print(order_objs)
# print(order_objs2)
new_orders = order_objs['on_new_od']
cancel_orders = order_objs['on_cancel_od']
excute_oders = order_objs['on_execute_od']

for od in new_orders:
    # print(od)
    on_new_order(
        order_id=od['ID'],
        stock_ticker=od['ticker'],
        price=od['price'],
        quantity=od['quantity'],
        side=od['side'])


top(2,'AAPL',1)