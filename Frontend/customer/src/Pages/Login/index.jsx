import React, { useContext, useEffect, useState } from "react";
import Input from '@mui/material/Input';
import InputLabel from '@mui/material/InputLabel';
import InputAdornment from '@mui/material/InputAdornment';
import FormControl from '@mui/material/FormControl';
import TextField from '@mui/material/TextField';
import AccountCircle from '@mui/icons-material/AccountCircle';
import Button from "@mui/material/Button";
import { IoMdEye, IoMdEyeOff } from "react-icons/io";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { FcGoogle } from "react-icons/fc";
import { MyContext } from "../../App";
import { postDataApi } from "../../utils/api";
import { CircularProgress } from "@mui/material";

const Login = () => {
    const [isLoading, setIsLoading] = useState(false)
    const [isShowPassword, setIsShowPassword] = useState(false)
    const [formFields, setFormFields] = useState({
        email: '',
        password: ''
    })
    const [params] = useSearchParams();
    const verified = params.get("verified");

    const context = useContext(MyContext)
    const history = useNavigate()

    const onChangeInput = (e) => {
        const { name, value } = e.target
        setFormFields(() => {
            return {
                ...formFields,
                [name]: value
            }
        })
    }

    const validateValue = Object.values(formFields).every(el => el)

    const handleSubmit = async (e) => {
        e.preventDefault()

        setIsLoading(true)

        if (formFields.email === "") {
            context.openAlertBox(
                "error", "Please enter email"
            )
            return false
        }

        if (formFields.password === "") {
            context.openAlertBox(
                "error", "Please enter password"
            )
            return false
        }

        const response = await postDataApi("/customer/auth/login", formFields);
        console.log(response)

        if (response?.success === true) {
            console.log(response);

            localStorage.setItem("userEmail", formFields.email)
            localStorage.setItem("accesstoken", response?.data?.access_token)
            localStorage.setItem("refreshtoken", response?.data?.refresh_token)

            await context.checkLogin();

            setIsLoading(false)
            context.openAlertBox(
                "success", response?.message
            )

            setFormFields({
                email: "",
                password: ""
            })

            history("/")
        } else {
            setIsLoading(false)
            context.openAlertBox("error", response?.data?.detail?.message)
        }
    }

    const forgotPassword = () => {
        context.openAlertBox("Success", "OTP Send")
        history('/verify')
    }

    useEffect(() => {
        if (verified === "true") {
            context.openAlertBox("success", "Xác thực tài khoản thành công!")
        } else if (verified === "false") {
            context.openAlertBox("error", "Có lỗi xảy ra trong quá trình xác thực!")
        }
    }, [verified]);


    return (
        <section className="section py-10">
            <div className="container">
                <div className="card shadow-md w-[450px] m-auto rounded-md bg-white p-4">
                    <h3 className="text-center text-[18px] text-black">Login to your account</h3>

                    <form className="w-full mt-5" onSubmit={handleSubmit}>
                        <div className="form-group w-full mb-5">
                            <TextField type="email" id="email" label="Email *" variant="outlined" className="w-full" name="email" value={formFields.email}
                                disabled={isLoading === true ? true : false} onChange={onChangeInput} />
                        </div>
                        <div className="form-group w-full mb-5 relative">
                            <TextField type={isShowPassword === false ? "password" : "text"} id="password" label="Password *" variant="outlined" className="w-full" name="password"
                                disabled={isLoading === true ? true : false} value={formFields.password} onChange={onChangeInput} />
                            <Button className="!absolute top-[10px] right-[10px] z-50 !w-[35px] !h-[35px] !min-w-[35px]
                            !rounded-full !text-black" onClick={() => setIsShowPassword(!isShowPassword)}>
                                {
                                    isShowPassword === true ? <IoMdEye className="text-[20px] opacity-75" /> :
                                        <IoMdEyeOff className="text-[20px] opacity-75" />
                                }

                            </Button>
                        </div>

                        <a className="link cursor-pointer text-[14px] font-[600]" onClick={forgotPassword}>Forgot Password?</a>

                        <div className="flex items-center w-full mt-3 mb-3">
                            <button type="submit" disabled={!validateValue || isLoading} className={`btn-org btn-lg w-full ${(!validateValue || isLoading) ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}>
                                {
                                    isLoading === true ? <CircularProgress color="inherit" />
                                        :
                                        'Login'
                                }
                            </button>
                        </div>

                        <p className="text-center">Not Registered? <Link className="link text-[14px] font-[600] text-[#ff5252]"
                            to="/signup"> Sign Up</Link></p>

                        <p className="text-center font-[500]">Or continue with social account</p>

                        <Button className="flex gap-3 w-full !bg-[#f1f1f1] btn-lg !text-black">
                            <FcGoogle className="text-[20px]" /> Login with Google
                        </Button>
                    </form>
                </div>
            </div>
        </section>
    )
}

export default Login