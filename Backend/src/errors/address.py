from fastapi import HTTPException, status

class AddressException:
    @staticmethod
    def not_found_to_delete():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy địa chỉ để xóa",
                "error_code": "address_001"
            }
        )

    @staticmethod
    def not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy địa chỉ",
                "error_code": "address_003"
            }
        )

    @staticmethod
    def empty_list():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy bất cứ địa chỉ nào",
                "error_code": "address_002"
            }
        )

    @staticmethod
    def invalid_address():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Địa chỉ đã nhập không hợp lệ",
                "error_code": "address_002"
            }
        )

    @staticmethod
    def province_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy tỉnh thành trên",
                "error_code": "address_003"
            }
        )

    @staticmethod
    def ward_not_found():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy phường/xã trên",
                "error_code": "address_003"
            }
        )