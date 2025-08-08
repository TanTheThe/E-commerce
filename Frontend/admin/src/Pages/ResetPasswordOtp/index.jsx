import Button from "@mui/material/Button";
import React, { useContext, useState } from "react";
import OtpBox from "../../Components/OtpBox";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { MyContext } from "../../App";
import { postDataApi } from "../../utils/api";
import { CgLogIn } from "react-icons/cg";

const ResetPasswordOtp = () => {
    const [otp, setOtp] = useState("")
    const [isLoading, setIsLoading] = useState(false)
    const location = useLocation()
    const email = location.state?.email
    const navigate = useNavigate()

    const context = useContext(MyContext)

    const handleOtpChange = (value) => {
        setOtp(value)
    }

    const verifyOTP = async (e) => {
        e.preventDefault()

        if (!otp || !email) {
            context.openAlertBox("error", "Thiếu OTP hoặc email")
            return;
        }

        setIsLoading(true);

        const response = await postDataApi("/admin/auth/forgot-password/verify-otp", {
            otp,
            email
        });

        if (response?.success === true) {
            context.openAlertBox(
                "success", "Xác thực OTP thành công"
            )

            navigate(`/reset-password/${response?.data?.token}`)
        } else {
            setIsLoading(false)
            context.openAlertBox("error", response?.data?.detail?.message)
        }

        setIsLoading(false);
    }

    return (
        <section className="bg-white w-full">
            <header className="w-full fixed top-0 left-0 px-10 py-3 flex items-center justify-between z-50">
                <Link to="/">
                    <img src="https://ecme-react.themenate.net/img/logo/logo-light-full.png" className="w-[200px]" />
                </Link>

                <div className="flex items-center gap-0">
                    <NavLink to="/login" exact={true} activeClassName="isActive">
                        <Button className="!rounded-full !text-[rgba(0,0,0,0.8)] !px-5 flex gap-1">
                            <CgLogIn className="text-[18px]" /> <p className="font-[600]">Login</p>
                        </Button>
                    </NavLink>
                </div>
            </header>
            <img src="background.png" className="w-full fixed top-0 left-0 opacity-5" />

            <div className="loginBox card w-[600px] h-[auto] pb-20 mx-auto pt-20 relative z-50">
                <div className="text-center">
                    <img src="https://cdn-icons-png.flaticon.com/128/7182/7182972.png" className="m-auto" />
                </div>

                <h1 className="text-center text-[35px] font-[800] mt-4">Thay đổi mật khẩu<br />
                    <span className="text-[#3872fa]">Nhập OTP để tiến hành xác minh</span>
                </h1>

                <br />

                <form onSubmit={verifyOTP}>
                    <div className="text-center flex items-center justify-center flex-col">
                        <OtpBox length={6} onChange={handleOtpChange} />
                    </div>

                    <br />

                    <div className="w-[300px] m-auto">
                        <Button type="submit" className="btn-blue w-full">
                            {isLoading ? "Đang xác thực..." : "Verify OTP"}
                        </Button>
                    </div>
                </form>
            </div>
        </section>
    )
}

export default ResetPasswordOtp