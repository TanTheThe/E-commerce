from fastapi import HTTPException, status


class StockException:
    @staticmethod
    def min_must_less_than_max():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số lượng tối thiểu phải nhỏ hơn hoặc bằng số lượng tối đa",
                "error_code": "stock_001",
            },
        )

    @staticmethod
    def min_must_greater_than_0():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Số lượng tối thiểu phải nhỏ lơn hơn bằng 0",
                "error_code": "stock_002",
            },
        )
        
    @staticmethod
    def stock_not_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không tìm thấy tồn kho tương ứng",
                "error_code": "stock_003",
            },
        )
        
    @staticmethod
    def insufficient_to_complete_return_purchase(stock_quantity, quantity_to_return):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không đủ tồn kho để hoàn trả. "
                f"Tồn kho hiện tại: {stock_quantity}, "
                f"Yêu cầu hoàn trả: {quantity_to_return}",
                "error_code": "stock_003",
            },
        )
        
    @staticmethod
    def insufficient_available_to_complete_pr(stock_available_quantity, quantity_to_return):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không đủ tồn kho khả dụng để hoàn trả. "
                f"Tồn kho khả dụng: {stock_available_quantity}, "
                f"Yêu cầu hoàn trả: {quantity_to_return}",
                "error_code": "stock_003",
            },
        )
        
    @staticmethod
    def no_inventory_for_product_at_warehouse(variant_id, warehouse_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không tìm thấy tồn kho cho sản phẩm {variant_id} tại kho {warehouse_id}",
                "error_code": "stock_003",
            },
        )
        
    @staticmethod
    def insufficient_inventory_to_fulfill_order(variant_id, stock_quantity, data_quantity):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Không đủ tồn kho để hoàn trả. Variant: {variant_id}, Tồn kho: {stock_quantity}, Cần hoàn trả: {data_quantity}",
                "error_code": "stock_003"
            },
        )

