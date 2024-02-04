from typing import Any, Optional, Type, Union, overload

from jinja2 import Undefined

def import_db():
    from blueprint_API import get_db
    return get_db

import datetime

class CrepeSale():
    def __init__(self, id: int, saleID: int, name: str, amount: int, price: float, time: datetime.datetime) -> None:
        self.id = id
        self.saleID = saleID
        self.name = name
        self.amount = amount
        self.price = price
        self.time = time
    
    def __str__(self) -> str:
        return f"ID: {self.id}; SaleID: {self.saleID}; Name: {self.name}; Amount: {self.amount}; Preis: {self.price}; Zeit: {self.time.strftime("%d-%m-%Y, %H:%M:%S")}"

sales_complete: list[CrepeSale] = []

@overload
def get_data(as_string = None) -> list[CrepeSale]: ...

@overload
def get_data(as_string: bool) -> list[str]: ...


def get_data(as_string: Optional[bool] = None) -> Union[list[CrepeSale], list[str]]:
    """Fetches the sales data from the database

    Args:
        as_string (bool, optional): If the data should be returned as String. False is returned as CrepesSale. Defaults to False.

    Returns:
        list[CrepeSale | str]: A list containing either the CrepeSales or strings (see parameter as_string)
    """
    con, cur = import_db()()

    return_list = []

    cur.execute("SELECT * FROM sales")
    all_data = cur.fetchall()
    con.close()
    del con, cur

    for data in all_data:
        time_ = datetime.datetime.fromisoformat(data[5])
        if as_string:
            return_list.append(str(CrepeSale(id=int(data[0]), saleID=int(data[1]), name=data[2], amount=int(data[3]), price=float(data[4]), time=time_)))
        else:
            return_list.append(CrepeSale(id=int(data[0]), saleID=int(data[1]), name=data[2], amount=int(data[3]), price=float(data[4]), time=time_))
        sales_complete.extend(return_list)
    return return_list

def get_highest_sale_id(data: list[CrepeSale]) -> int:
    """Returns highest SaleID

    Args:
        data (list[CrepeSale]): The result of get_data()

    Returns:
        int: The highest SaleID
    """
    high: int = -1
    for sale in data:
        if high < sale.saleID:
            high = sale.saleID
    return high

def sales_to_dict(data: list[CrepeSale]) -> tuple[list[dict[str, int | str | float]], float]:
    return_list: list[dict[str, int | str | float]] = []
    total: float = 0

    for sale in data:
        return_list.append({
                "ID": sale.id,
                "Name": sale.name,
                "amount": sale.amount,
                "price": sale.price
            })
        total += sale.price * sale.amount
    return return_list, total

def get_sales_with_id(data: list[CrepeSale], id: int) -> list[CrepeSale]:
    return_list = []
    for sale in data:
        if sale.saleID == id:
            return_list.append(sale)
    return return_list


def get_dict() -> dict[int, dict[int, dict[str, Any]]]:
    """Result to be sent to jinja

    Returns:
        dict[int, dict[int, dict[str, Any]]]: The data
    """
    data_start = get_data()

    tmp_data = {}
    
    ids: dict[int, CrepeSale] = {}
    
    for crepe in data_start:
        ids[crepe.saleID] = crepe

    for id in ids:
        sales_with_id = get_sales_with_id(data_start, id)
        tmp_data[id] = ({
            "items": sales_to_dict(sales_with_id)[0],
            "time": ids[id].time.isoformat(),
            "total": ids[id].price * ids[id].amount
            })
    return tmp_data

def get_heatmap() -> list[int]:
    """Returns the amount of sales that has been made for each hour of the day

    Returns:
        list[int]: The hours and how many sales have been made
    """

    if (sales_complete == []):
        get_data()
    to_return = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    saleIDs_done = []
    for sale in sales_complete:
        if sale.saleID in saleIDs_done:
            continue
        to_return[sale.time.time().hour] += 1
        saleIDs_done.append(sale.saleID)
    return to_return

if __name__ == "__main__":
    print(get_heatmap())