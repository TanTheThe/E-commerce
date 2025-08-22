import React, { useContext, useState } from "react";
import Input from '@mui/material/Input';
import InputLabel from '@mui/material/InputLabel';
import InputAdornment from '@mui/material/InputAdornment';
import FormControl from '@mui/material/FormControl';
import TextField from '@mui/material/TextField';
import AccountCircle from '@mui/icons-material/AccountCircle';
import Button from "@mui/material/Button";
import { IoMdEye, IoMdEyeOff } from "react-icons/io";
import { Link, useNavigate } from "react-router-dom";
import { FcGoogle } from "react-icons/fc";
import { postDataApi } from "../../utils/api";
import { MyContext } from "../../App";
import { CircularProgress } from "@mui/material";
import { BsCheckLg } from "react-icons/bs";

const Register = () => {
    const [isShowPassword, setIsShowPassword] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [formFields, setFormFields] = useState({
        first_name: "",
        last_name: "",
        email: "",
        password: ""
    })

    const context = useContext(MyContext)

    const onChangeInput = (e) => {
        const { name, value } = e.target;
        setFormFields((prev) => ({
            ...prev,
            [name]: value
        }));
    };

    const isValidEmail = (email) =>
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

    const allFieldsFilled = Object.values(formFields).every((el) => el.trim() !== "");
    const isFormValid = allFieldsFilled && isValidEmail(formFields.email);

    const handleSubmit = async (e) => {
        e.preventDefault()

        setIsLoading(true);

        const response = await postDataApi("/customer/user/signup", formFields);

        if (response?.success === true) {
            setIsLoading(false)
            context.openAlertBox(
                "success", response?.message
            )
            setFormFields({
                first_name: "",
                last_name: "",
                email: "",
                password: ""
            })
        } else {
            setIsLoading(false)
            context.openAlertBox("error", response?.data?.detail?.message)
        }
    }

    return (
        <section className="section py-10">
            <div className="container">
                <div className="card shadow-md w-[450px] m-auto rounded-md bg-white p-4">
                    <h3 className="text-center text-[18px] text-black">Register with a new account</h3>

                    <form className="w-full mt-5" onSubmit={handleSubmit}>
                        <div className="form-group w-full mb-5">
                            <TextField type="text" id="first_name" name="first_name" value={formFields.first_name} label="First name" variant="outlined" className="w-full"
                                disabled={isLoading === true ? true : false}
                                onChange={onChangeInput} />
                        </div>
                        <div className="form-group w-full mb-5">
                            <TextField type="text" id="last_name" name="last_name" value={formFields.last_name} label="Last name" variant="outlined" className="w-full"
                                disabled={isLoading === true ? true : false}
                                onChange={onChangeInput} />
                        </div>
                        <div className="form-group w-full mb-5">
                            <TextField type="email" id="email" name="email" value={formFields.email} label="Email *" variant="outlined" className="w-full"
                                disabled={isLoading === true ? true : false}
                                onChange={onChangeInput} error={formFields.email && !isValidEmail(formFields.email)}
                                helperText={
                                    formFields.email && !isValidEmail(formFields.email)
                                        ? "Email không chính xác"
                                        : ""
                                } />
                        </div>
                        <div className="form-group w-full mb-5 relative">
                            <TextField type={isShowPassword === false ? "password" : "text"} id="password" name="password" value={formFields.password}
                                disabled={isLoading === true ? true : false}
                                label="Password *" variant="outlined" className="w-full"
                                onChange={onChangeInput} />
                            <Button className="!absolute top-[10px] right-[10px] z-50 !w-[35px] !h-[35px] !min-w-[35px]
                            !rounded-full !text-black" onClick={() => setIsShowPassword(!isShowPassword)}>
                                {
                                    isShowPassword === true ? <IoMdEye className="text-[20px] opacity-75" /> :
                                        <IoMdEyeOff className="text-[20px] opacity-75" />
                                }

                            </Button>
                        </div>

                        <div className="flex items-center w-full mt-3 mb-3">
                            <button type="submit" disabled={!isFormValid || isLoading} className={`btn-org btn-lg w-full flex gap-3 items-center justify-center transition ${(!isFormValid || isLoading) ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}>
                                {
                                    isLoading === true ? <CircularProgress color="inherit" />
                                        :
                                        'Register'
                                }
                            </button>
                        </div>

                        <p className="text-center">Already have an account? <Link className="link text-[14px] font-[600] text-[#ff5252]"
                            to="/login"> Login</Link></p>

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

export default Register