from decimal import Decimal
from src.crud.good_receipts.repositories import GoodsReceiptRepository

goods_receipt_repository = GoodsReceiptRepository()


class UtilsStockService:
    def calculate_weighted_average_cost(self, stock, previous_quantity: int, new_data: dict):
        total_cost = Decimal('0')
        total_qty = 0

        for gr_detail in new_data['gr_details']:
            if gr_detail['unit_cost'] is not None and gr_detail['quantity'] > 0:
                unit_cost = Decimal(str(gr_detail['unit_cost']))
                quantity = Decimal(str(gr_detail['quantity']))
                total_cost += unit_cost * quantity
                total_qty += gr_detail['quantity']

        if total_qty == 0:
            return None, Decimal('0')

        avg_unit_cost = total_cost / Decimal(str(total_qty))

        if stock.cost_price and previous_quantity > 0:
            old_total_value = Decimal(
                str(stock.cost_price)) * Decimal(str(previous_quantity))
            new_total_value = avg_unit_cost * \
                Decimal(str(new_data['total_quantity']))
            total_value = old_total_value + new_total_value
            total_quantity = Decimal(
                str(previous_quantity + new_data['total_quantity']))
            new_cost_price = total_value / total_quantity
        else:
            new_cost_price = avg_unit_cost

        return new_cost_price, avg_unit_cost

    def determine_stock_status(self, stock):
        if stock.available_quantity <= 0:
            return "out_of_stock"
        elif stock.min_stock_level and stock.available_quantity <= stock.min_stock_level:
            return "low_stock"
        else:
            return "available"
