import React, { useContext, useEffect, useRef, useState } from "react";
import TextField from '@mui/material/TextField';
import Button from "@mui/material/Button";
import { IoMdEye, IoMdEyeOff } from "react-icons/io";
import { Link, NavLink, useNavigate, useParams } from "react-router-dom";
import { MyContext } from "../../App";
import { postDataApi } from "../../utils/api";
import { CircularProgress } from "@mui/material";
import { CgLogIn } from "react-icons/cg";

const ResetPassword = () => {
    const [isShowPassword, setIsShowPassword] = useState(false);
    const [isShowPassword2, setIsShowPassword2] = useState(false);

    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");
    const [isSubmitDisabled, setIsSubmitDisabled] = useState(false);
    const [isLoading, setIsLoading] = useState(false)

    const confirmPasswordRef = useRef(null);

    const context = useContext(MyContext);
    const navigate = useNavigate();

    const { token } = useParams();

    const resetPassword = async (e) => {
        e.preventDefault();
        if (isSubmitDisabled) return;

        setIsLoading(true);

        const response = await postDataApi(`/admin/auth/confirm-reset`, {
            token,
            new_password: newPassword,
            confirm_new_password: confirmPassword
        });

        if (response?.success === true) {
            setIsLoading(false)

            context.openAlertBox(
                "success", response?.message
            )

            setNewPassword("")
            setConfirmPassword("")

            navigate(`/login`)
        } else {
            setIsLoading(false)
            context.openAlertBox("error", response?.data?.detail?.message)
        }
    }

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (
                confirmPasswordRef.current &&
                !confirmPasswordRef.current.contains(event.target)
            ) {
                if (confirmPassword && confirmPassword !== newPassword) {
                    setError("Mật khẩu xác nhận không khớp");
                    setIsSubmitDisabled(true);
                } else {
                    setError("");
                    setIsSubmitDisabled(false);
                }
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [confirmPassword, newPassword]);

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
            <img src="/public/background.png" className="w-full fixed top-0 left-0 opacity-5" />

            <div className="loginBox card w-[600px] h-[auto] pb-20 mx-auto pt-20 relative z-50">
                <div className="text-center">
                    <img src="/public/forgot.png" className="m-auto w-[80px]" />
                </div>

                <h1 className="text-center text-[35px] font-[800] mt-4">Thay đổi mật khẩu mới</h1>

                <form className="w-full mt-5" onSubmit={resetPassword}>
                    <div className="form-group w-full mb-5 relative">
                        <TextField
                            type={isShowPassword === false ? "password" : "text"}
                            id="password" label="New Password" variant="outlined" className="w-full" name="name"
                            disabled={isLoading === true ? true : false}
                            onChange={(e) => setNewPassword(e.target.value)} />

                        <Button className="!absolute top-[10px] right-[10px] z-50 !w-[35px] !h-[35px] !min-w-[35px]
                            !rounded-full !text-black" onClick={() => setIsShowPassword(!isShowPassword)}>
                            {
                                isShowPassword === true ?
                                    <IoMdEye className="text-[20px] opacity-75" />
                                    :
                                    <IoMdEyeOff className="text-[20px] opacity-75" />
                            }
                        </Button>
                    </div>

                    <div className="form-group w-full mb-5 relative" ref={confirmPasswordRef}>
                        <TextField
                            type={isShowPassword2 === false ? "password" : "text"}
                            id="confirm_password" label="Confirm Password" variant="outlined" className="w-full" name="password"
                            value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)}
                            disabled={isLoading === true ? true : false}
                            error={!!error} helperText={error} />

                        <Button className="!absolute top-[10px] right-[10px] z-50 !w-[35px] !h-[35px] !min-w-[35px]
                            !rounded-full !text-black" onClick={() => setIsShowPassword2(!isShowPassword2)}>
                            {
                                isShowPassword2 === true ?
                                    <IoMdEye className="text-[20px] opacity-75" />
                                    :
                                    <IoMdEyeOff className="text-[20px] opacity-75" />
                            }

                        </Button>
                    </div>
                    <div className="flex items-center w-full mt-4 mb-3">
                        <button
                            type="submit"
                            disabled={isSubmitDisabled}
                            className={`btn-blue btn-lg w-full ${isSubmitDisabled || isLoading ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
                        >
                            {
                                isLoading === true ? <CircularProgress color="inherit" />
                                    :
                                    'Change Password'
                            }
                        </button>
                    </div>
                </form>
            </div>
        </section>
    )
}

export default ResetPassword