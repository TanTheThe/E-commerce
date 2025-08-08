import Button from "@mui/material/Button";
import React, { useContext, useState } from "react";
import OtpBox from "../../components/OtpBox";
import { useLocation, useNavigate } from "react-router-dom";
import { MyContext } from "../../App";
import { postDataApi } from "../../utils/api";

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

        const response = await postDataApi("/customer/auth/forgot-password/verify-otp", {
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
        <section className="section py-10">
            <div className="container">
                <div className="card shadow-md w-[450px] m-auto rounded-md bg-white p-5 px-10">
                    <div className="text-center flex items-center justify-center">
                        <img src="https://cdn-icons-png.flaticon.com/128/7182/7182972.png" width="80" />
                    </div>
                    <h3 className="text-center text-[18px] text-black mt-4">Verify OTP</h3>

                    <p className="text-center mt-0 mb-4">OTP send to <span className="text-[#ff5252] font-bold">
                        {email}</span></p>

                    <form onSubmit={verifyOTP}>
                        <OtpBox length={6} onChange={handleOtpChange} />

                        <div className="flex items-center justify-between mt-5 px-3">
                            <Button type="submit" className="w-full btn-org btn-lg" disabled={isLoading}>
                                {isLoading ? "Verifying..." : "Verify OTP"}
                            </Button>
                        </div>
                    </form>
                </div>
            </div>
        </section>
    )
}

export default ResetPasswordOtp