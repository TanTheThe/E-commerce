import Button from "@mui/material/Button";
import React, { useContext, useEffect, useState } from "react";
import { CgLogIn } from "react-icons/cg";
import { FaEyeSlash, FaRegEye, FaRegUser } from "react-icons/fa";
import { FcGoogle } from "react-icons/fc";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { Line } from "recharts";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import { CircularProgress, TextField } from "@mui/material";
import { IoMdEye, IoMdEyeOff } from "react-icons/io";
import { postDataApi } from "../../utils/api"
import { MyContext } from "../../App";

const Login = () => {
    const [isLoading, setIsLoading] = useState(false)
    const [formFields, setFormFields] = useState({
        email: '',
        password: ''
    })
    const history = useNavigate()

    const validateValue = Object.values(formFields).every(el => el)

    const [loadingGoogle, setLoadingGoogle] = useState(false);
    const [isShowPassword, setIsShowPassword] = useState(false)

    function handleClickGoogle() {
        setLoadingGoogle(true);
    }

    const context = useContext(MyContext)

    const onChangeInput = (e) => {
        const { name, value } = e.target
        setFormFields(() => {
            return {
                ...formFields,
                [name]: value
            }
        })
    }

    useEffect(() => {
        const accessToken = localStorage.getItem("accesstoken");
        if (accessToken) {
            history("/")
        }
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault()

        setIsLoading(true)

        const response = await postDataApi("/admin/auth/login", formFields);
        console.log(response)

        if (response?.success === true) {
            console.log(response);

            sessionStorage.setItem("loginToken", response?.data?.token)
            sessionStorage.setItem("isFirstLogin", response?.data?.isFirstLogin)

            setIsLoading(false)
            context.openAlertBox(
                "success", response?.message
            )

            setFormFields({
                email: "",
                password: ""
            })

            history("/verify")
        } else {
            setIsLoading(false)
            context.openAlertBox("error", response?.data?.detail?.message)
        }
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
                    <img src="logo.svg" className="m-auto" />
                </div>

                <h1 className="text-center text-[35px] font-[800] mt-4">Welcome Back!<br />
                    <span className="text-[#3872fa]">Sign in with your credentials.</span>
                </h1>

                <div className="flex items-center justify-center w-full mt-5">
                    <Button
                        size="small"
                        onClick={handleClickGoogle}
                        endIcon={<FcGoogle />}
                        loading={loadingGoogle}
                        loadingPosition="end"
                        variant="outlined"
                        className="!bg-none !py-2 !text-[15px] !capitalize !px-5 !text-[rgba(0,0,0,0.7)]"
                    >
                        Signin with Google
                    </Button>
                </div>

                <br />

                <div className="w-full flex items-center justify-center gap-3">
                    <span className="flex items-center w-[100px] h-[2px] bg-[rgba(0,0,0,0.2)]"></span>
                    <span className="text-[15px] font-[500]">Or, Sign in with your email</span>
                    <span className="flex items-center w-[100px] h-[2px] bg-[rgba(0,0,0,0.2)]"></span>
                </div>

                <form className="w-full px-8 mt-3" onSubmit={handleSubmit}>
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

                    <div className="form-group mb-4 w-full flex items-center justify-between">
                        <FormControlLabel control={<Checkbox defaultChecked />} label="Remember me" />

                        <Link to="/forgot-password" className="text-[#3872fa] font-[700] text-[15px] hover:underline hover:text-gray-700">
                            Forgot Password?
                        </Link>
                    </div>

                    <div className="flex items-center w-full mt-3 mb-3">
                        <button type="submit" disabled={!validateValue || isLoading} className={`btn-blue btn-lg w-full ${(!validateValue || isLoading) ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}>
                            {
                                isLoading === true ? <CircularProgress color="inherit" />
                                    :
                                    'Login'
                            }
                        </button>
                    </div>
                </form>
            </div>
        </section>
    )
}

export default Login