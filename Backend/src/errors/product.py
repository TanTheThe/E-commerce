from fastapi import HTTPException, status
from typing import List

class ProductException:
    @staticmethod
    def not_found_to_delete():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy sản phẩm để xóa",
                "error_code": "product_001",
            },
        )

    @staticmethod
    def invalid_name():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tên sản phẩm không hợp lệ",
                "error_code": "product_002",
            },
        )

    @staticmethod
    def invalid_images():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Sản phẩm cần phải có ít nhất một tấm ảnh",
                "error_code": "product_003",
            },
        )

    @staticmethod
    def invalid_categories():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Sản phẩm phải thuộc ít nhất một danh mục.",
                "error_code": "product_004",
            },
        )

    @staticmethod
    def invalid_variant():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Sản phẩm phải có ít nhất một biến thể.",
                "error_code": "product_005",
            },
        )

    @staticmethod
    def not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy sản phẩm",
                "error_code": "product_006",
            },
        )

    @staticmethod
    def empty_list():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy bất cứ sản phẩm nào",
                "error_code": "product_007",
            },
        )

    @staticmethod
    def not_enough_infor_to_update():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không cung cấp đủ thông tin để cập nhật",
                "error_code": "product_008",
            },
        )

    @staticmethod
    def not_found_variant_to_delete():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy biến thể sản phẩm để xóa",
                "error_code": "product_009",
            },
        )

    @staticmethod
    def not_found_variant():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy biến thể sản phẩm",
                "error_code": "product_010",
            },
        )
        
    @staticmethod
    def variant_sold_out():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Biến thể sản phẩm này đã hết hàng",
                "error_code": "product_010",
            },
        )
        
    @staticmethod
    def invalid_variant_price():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Giá của biến thể sản phẩm không hợp lệ",
                "error_code": "product_010",
            },
        )

    @staticmethod
    def invalid_create_product():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Có lỗi xảy ra trong quá trình tạo sản phẩm",
                "error_code": "product_011",
            },
        )

    @staticmethod
    def out_of_stock(id: str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Biến thế {id} vượt quá số lượng trong kho",
                "error_code": "product_012",
            },
        )

    @staticmethod
    def fail_count_products():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Lỗi trong quá trình tính số lượng sản phẩm",
                "error_code": "product_013",
            },
        )

    @staticmethod
    def sku_exists(existing_skus: set[str]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"SKU đã tồn tại: {list(existing_skus)}",
                "error_code": "product_014",
            },
        )

    @staticmethod
    def not_enough_variant():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không đủ số lượng biến thể",
                "error_code": "product_015",
            },
        )
    
    @staticmethod
    def invalid_product_ids():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Một trong số các sản phẩm yêu cầu cập nhật không hợp lệ",
                "error_code": "product_016",
            },
        )
        
    @staticmethod
    def not_found_product_from_variant():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không tìm thấy sản phẩm dựa vào biến thể đã định",
                "error_code": "product_017",
            },
        )

    @staticmethod
    def some_products_not_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Có một vài sản phẩm không tồn tại",
                "error_code": "product_018",
            },
        )
        
    @staticmethod
    def duplicate_sku():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "SKU của biến thể bị trùng lặp",
                "error_code": "product_018",
            },
        )
        
    @staticmethod
    def sku_already_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "SKU này đã tồn tại trong hệ thống",
                "error_code": "product_018",
            },
        )
        
    @staticmethod
    def category_identifier_must_not_be_empty():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "category_identifier không được để trống",
                "error_code": "product_018",
            },
        )
        
    @staticmethod
    def identifier_must_not_be_empty():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "identifier không được để trống",
                "error_code": "product_018",
            },
        )
        
    @staticmethod
    def min_price_greater_than_max_price():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "min_price không được lớn hơn max_price",
                "error_code": "product_018",
            },
        )
        
    @staticmethod
    def search_must_not_be_empty():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Từ khóa tìm kiếm không được để trống",
                "error_code": "product_018",
            },
        )
        
    @staticmethod
    def search_too_short():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Từ khóa tìm kiếm quá ngắn",
                "error_code": "product_018",
            },
        )