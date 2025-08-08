import Button from "@mui/material/Button";
import React, { useContext, useEffect, useState } from "react";
import { CgLogIn } from "react-icons/cg";
import { FaEyeSlash, FaRegEye, FaRegUser } from "react-icons/fa";
import { FcGoogle } from "react-icons/fc";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { Line } from "recharts";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import OtpBox from "../../Components/OtpBox";
import { postDataApi } from "../../utils/api";
import { MyContext } from "../../App";



const Verify = () => {
    const [otp, setOtp] = useState("")
    const [isLoading, setIsLoading] = useState(false)
    const [qrCodeBase64, setQrCodeBase64] = useState("");
    const [isShowQR, setIsShowQR] = useState(false);
    const [isCheckingToken, setIsCheckingToken] = useState(true)
    const [shouldNavigate, setShouldNavigate] = useState(false);
    const navigate = useNavigate()
    const [token, setToken] = useState("")
    const context = useContext(MyContext)

    useEffect(() => {
        if (shouldNavigate) {
            navigate('/', { replace: true });
            setShouldNavigate(false);
        }
    }, [shouldNavigate, navigate]);

    useEffect(() => {
        (async () => {
            const accessToken = localStorage.getItem("accesstoken");
            if (accessToken) {
                navigate("/")
                return
            }

            const loginToken = sessionStorage.getItem("loginToken");
            if (!loginToken) {
                navigate("/login");
            } else {
                const isFirstLogin = sessionStorage.getItem("isFirstLogin");
                console.log(isFirstLogin);
                if (isFirstLogin === 'true') {
                    const response = await postDataApi("/admin/auth/login/2fa", {
                        token: loginToken
                    });
                    setQrCodeBase64(response?.data?.qr_code_base64)
                    setIsShowQR(true)
                }
                setToken(loginToken);
            }
            setIsCheckingToken(false);
        })()
    }, []);

    const handleOtpChange = (value) => {
        setOtp(value)
    }

    const verifyOTP = async (e) => {
        e.preventDefault()

        setIsLoading(true);

        const response = await postDataApi("/admin/auth/login/verify", {
            token,
            otp
        });

        if (response?.success === true) {

            localStorage.setItem("accesstoken", response?.data?.access_token);
            localStorage.setItem("refreshtoken", response?.data?.refresh_token);

            await context.checkLogin()

            context.openAlertBox("success", "Xác thực OTP thành công");

            sessionStorage.removeItem("isFirstLogin")
            sessionStorage.removeItem("loginToken")

            setShouldNavigate(true);
        } else {
            setIsLoading(false);
            context.openAlertBox("error", response?.data?.detail.message)
        }
    }

    if (isCheckingToken) return null;

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

                <h1 className="text-center text-[35px] font-[800] mt-4">Xác minh tài khoản<br />
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

                {isShowQR && (
                    <div className="fixed top-0 left-0 w-full h-full bg-black-popup bg-opacity-50 flex justify-center items-center z-50">
                        <div className="bg-white p-5 rounded-xl text-center">
                            <h2 className="text-xl font-bold mb-4">Quét mã QR để bật Google Authenticator</h2>
                            <img src={`data:image/png;base64,${qrCodeBase64}`} alt="QR Code" className="mx-auto mb-4" />
                            <Button onClick={() => setIsShowQR(false)} className="btn-blue">Đóng</Button>
                        </div>
                    </div>
                )}
            </div>
        </section>
    )
}

export default Verify