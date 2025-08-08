import React, { useContext, useState } from "react";
import { postDataApi } from "../../utils/api";
import { MyContext } from "../../App";
import { CircularProgress } from "@mui/material";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { CgLogIn } from "react-icons/cg";
import Button from "@mui/material/Button";

const SendEmailGetOtp = () => {
    const [email, setEmail] = useState("");
    const context = useContext(MyContext)
    const [isLoading, setIsLoading] = useState(false)
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!email) {
            context.openAlertBox("error", "Please enter email");
            return;
        }

        setIsLoading(true)

        const response = await postDataApi("/admin/auth/forgot-password", {
            email,
            check: "otp"
        });

        if (response?.success === true) {
            context.openAlertBox(
                "success", "Please visit your email to get otp"
            )
            
            navigate("/forgot-password-otp", { state: { email } });
        } else {
            context.openAlertBox("error", response?.data?.detail?.message)
        }

        setIsLoading(false);
    };

    return (
        <section className="bg-white w-full">
            <header className="w-full fixed top-0 left-0 px-10 py-3 flex items-center justify-between z-50">
                <Link to="/">
                    <img src="https://ecme-react.themenate.net/img/logo/logo-light-full.png" className="w-[200px]" />
                </Link>

                <div className="flex items-center gap-0">
                    <NavLink to="/forgot-password" exact={true} activeClassName="isActive">
                        <Button className="!rounded-full !text-[rgba(0,0,0,0.8)] !px-5 flex gap-1">
                            <CgLogIn className="text-[18px]" /> <p className="font-[600]">Options</p>
                        </Button>
                    </NavLink>
                </div>
            </header>
            <img src="background.png" className="w-full fixed top-0 left-0 opacity-5" />

            <div className="loginBox card w-[700px] h-[auto] pb-20 mx-auto pt-20 relative z-50">
                <div className="text-center">
                    <img src="logo.svg" className="m-auto" />
                </div>


                <h1 className="text-center text-[35px] font-[800] mt-4">Cung cấp địa chỉ Email<br />
                    <span className="text-[#3872fa]">Nhận Otp thay đổi mật khẩu từ Email</span>
                </h1>

                <div className="flex flex-col items-center justify-center px-4 mt-5">
                    <form onSubmit={handleSubmit} className="w-full max-w-md">
                        <label htmlFor="email" className="block mb-2 font-medium text-sm">
                            Email *
                        </label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="w-full p-2 border border-gray-300 rounded mb-4 bg-white"
                        />
                        <button
                            type="submit"
                            disabled={!email || isLoading}
                            className={`w-full flex items-center justify-center bg-blue-600 text-white px-4 py-2 rounded transition hover:bg-blue-700 ${(!email || isLoading) ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
                        >
                            {isLoading ? <CircularProgress size={24} color="inherit" /> : "SEND OTP"}
                        </button>
                    </form>
                </div>
            </div>
        </section>
    );
};

export default SendEmailGetOtp;
