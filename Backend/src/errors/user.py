from fastapi import HTTPException, status


class UserException:
    @staticmethod
    def email_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Email đã tồn tại",
                "error_code": "user_001",
            },
        )

    @staticmethod
    def role_invalid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Role không hợp lệ",
                "error_code": "user_002",
            },
        )

    @staticmethod
    def only_staff_can_be_assigned():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Chỉ staff mới có thể được gán làm quản lý/nhân viên kho",
                "error_code": "user_003",
            },
        )

    @staticmethod
    def only_staff_active_can_be_assigned():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể gán nhân viên không hoạt động làm quản lý/nhân viên kho",
                "error_code": "user_004",
            },
        )

    @staticmethod
    def only_staff_activity_can_be_viewed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Chỉ có thể xem lịch sử hoạt động của nhân viên",
                "error_code": "user_005",
            },
        )

    @staticmethod
    def cant_assign_manager_in_this_function():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể gán vai trò manager tại chức năng này",
                "error_code": "user_006",
            },
        )

    @staticmethod
    def staff_has_been_assigned_to_another_warehouse():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Nhân viên đã được phân công vào kho khác",
                "error_code": "user_007",
            },
        )

    @staticmethod
    def staff_already_in_this_warehouse(role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Nhân viên đã được phân công vào kho này với vai trò {role}",
                "error_code": "user_008",
            },
        )

    @staticmethod
    def staff_not_in_this_warehouse():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Nhân viên không thuộc kho này",
                "error_code": "user_009",
            },
        )

    @staticmethod
    def cant_remove_manager_in_this_function():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Không thể gỡ vai trò manager tại chức năng này",
                "error_code": "user_010",
            },
        )

    @staticmethod
    def staff_already_in_this_role(role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Nhân viên đang ở vai trò {role} rồi",
                "error_code": "user_011",
            },
        )

    @staticmethod
    def one_staff_doesnt_exist():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Có một hoặc nhiều nhân viên không tồn tại",
                "error_code": "user_012",
            },
        )

    @staticmethod
    def more_than_one_staff_doesnt_in_warehouse():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Có một hoặc nhiều nhân viên không làm việc tại kho này",
                "error_code": "user_013",
            },
        )

    @staticmethod
    def new_role_for_old_manager():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Vai trò mới cho quản lý cũ không được là manager",
                "error_code": "user_014",
            },
        )
