import React, { useState } from "react";
import Button from "@mui/material/Button";
import { MdEmail } from "react-icons/md";
import { BiSolidLockAlt } from "react-icons/bi";
import { CardContent, Card } from "@mui/material";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { CgLogIn } from "react-icons/cg";

const ForgotPassword = () => {
    const navigate = useNavigate();

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

            <div className="loginBox card w-[700px] h-[auto] pb-20 mx-auto pt-20 relative z-50">
                <div className="text-center">
                    <img src="logo.svg" className="m-auto" />
                </div>

                <h1 className="text-center text-[35px] font-[800] mt-4">Quên mật khẩu!<br />
                    <span className="text-[#3872fa]">Lựa chọn phương pháp lấy lại mật khẩu</span>
                </h1>


                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl w-full mt-5">
                    <Card
                        onClick={() => navigate("/forgot-password-email")}
                        className="rounded-2xl border border-gray-200 bg-white/80 backdrop-blur-md shadow-lg transform transition-all duration-300 ease-in-out hover:-translate-y-2 hover:shadow-2xl hover:bg-indigo-50 hover:border-indigo-200 cursor-pointer"
                    >
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

                    <Card
                        onClick={() => navigate("/send-mail")}
                        className="rounded-2xl border border-gray-200 bg-white/80 backdrop-blur-md shadow-lg transform transition-all duration-300 ease-in-out hover:-translate-y-2 hover:shadow-2xl hover:bg-red-50 hover:border-red-200 cursor-pointer"
                    >
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
        </section>
    )
}

export default ForgotPassword