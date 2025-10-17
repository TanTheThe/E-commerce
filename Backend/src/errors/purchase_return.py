from fastapi import HTTPException, status


class PurchaseReturnException:
    @staticmethod
    def pr_not_found():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Phiếu hoàn trả không tồn tại",
                "error_code": "pr_001",
            },
        )

    @staticmethod
    def pr_must_be_in_confirmed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Phiếu hoàn trả phải đang ở trạng thái confirmed",
                "error_code": "pr_001",
            },
        )


