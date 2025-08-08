import React, { useState } from "react";
import OtpBox from "../../components/OtpBox";
import Button from "@mui/material/Button";
import { MdEmail } from "react-icons/md";
import { BiSolidLockAlt } from "react-icons/bi";
import { CardContent, Card } from "@mui/material";
import { useNavigate } from "react-router-dom";

const Verify = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-120 bg-gray-100 flex flex-col items-center justify-center p-4">
            <h1 className="text-4xl font-bold mb-4 text-gray-800">QUÊN MẬT KHẨU?</h1>
            <p className="text-center text-gray-600 max-w-xl mb-8">
                Vui lòng chọn một trong các cách sau để khôi phục lại mật khẩu của bạn.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl w-full mt-5">
                <Card onClick={() => navigate("/forgot-password-email")} className="rounded-2xl shadow-md transform transition-all duration-500 ease-in-out hover:-translate-y-3 hover:shadow-xl cursor-pointer">
                    <CardContent className="flex flex-col items-center text-center p-6">
                        <div className="text-5xl text-indigo-600 mb-4">
                            <MdEmail />
                        </div>
                        <h3 className="text-xl font-semibold mb-2">Email</h3>
                        <p className="text-sm text-gray-600 mb-4">
                            Chúng tôi sẽ gửi đường dẫn đặt lại mật khẩu đến email của bạn.
                        </p>
                        
                        <p className="text-indigo-600 font-medium text-sm">Khôi phục qua Email</p>
                    </CardContent>
                </Card>

                <Card onClick={() => navigate("/send-mail")} className="rounded-2xl shadow-md transform transition-all duration-500 ease-in-out hover:-translate-y-3 hover:shadow-xl cursor-pointer">
                    <CardContent className="flex flex-col items-center text-center p-6">
                        <div className="text-5xl text-red-500 mb-4">
                            <BiSolidLockAlt />
                        </div>
                        <h3 className="text-xl font-semibold mb-2">OTP</h3>
                        <p className="text-sm text-gray-600 mb-4">
                            Nhập mã OTP được gửi qua SMS để đặt lại mật khẩu nhanh chóng.
                        </p>
                        
                        <p className="text-red-500 font-medium text-sm">Khôi phục bằng OTP</p>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}

export default Verify