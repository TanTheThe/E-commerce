import React, { useContext, useEffect, useRef, useState } from "react";
import { MyContext } from "../../App";
import { useNavigate } from "react-router-dom";
import Button from "@mui/material/Button";
import { CircularProgress, TextField } from "@mui/material";
import { IoMdEye, IoMdEyeOff } from "react-icons/io";
import { putDataApi } from "../../utils/api";

const Profile = () => {
    const context = useContext(MyContext)
    const navigate = useNavigate();

    const [isLoading, setIsLoading] = useState(false)
    const [isLoadingChangePassword, setIsLoadingChangePassword] = useState(false)
    const [isShowPasswordOld, setIsShowPasswordOld] = useState(false);
    const [isShowPasswordNew, setIsShowPasswordNew] = useState(false);
    const [isShowPasswordConfirm, setIsShowPasswordConfirm] = useState(false);
    const [oldPassword, setOldPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");
    const [isSubmitDisabled, setIsSubmitDisabled] = useState(true);
    const [isShowChangePassword, setIsShowChangePassword] = useState(false);

    const confirmPasswordRef = useRef(null);

    const [formFields, setFormFields] = useState({
        first_name: '',
        last_name: '',
        phone: ''
    })

    const onChangeInput = (e) => {
        const { name, value } = e.target
        setFormFields(() => {
            return {
                ...formFields,
                [name]: value
            }
        })
    }

    const isValidVietnamesePhone = (phone) => {
        const regex = /^(0|\+84)(3[2-9]|5[6|8|9]|7[0|6-9]|8[1-5]|9[0-9])[0-9]{7}$/;
        return regex.test(phone);
    };

    const validateValue =
        Object.values(formFields).some(el => el.trim() !== "") &&
        (formFields.phone === "" || isValidVietnamesePhone(formFields.phone));

    const handleSubmit = async (e) => {
        e.preventDefault()

        setIsLoading(true)

        const response = await putDataApi("/admin/user", formFields);
        console.log(response)

        if (response?.success === true) {

            localStorage.setItem("userFirstName", formFields.first_name)
            localStorage.setItem("userLastName", formFields.last_name)

            context.setUserData(prev => ({
                ...prev,
                first_name: formFields.first_name,
                last_name: formFields.last_name,
                phone: formFields.phone,
                content: {
                    ...prev.content,
                    first_name: formFields.first_name,
                    last_name: formFields.last_name,
                    phone: formFields.phone
                }
            }));

            setIsLoading(false)
            context.openAlertBox(
                "success", response?.message
            )

            setFormFields({
                first_name: "",
                last_name: "",
                phone: ""
            })
        } else {
            setIsLoading(false)
            context.openAlertBox("error", response?.data?.detail?.message)
        }
    }

    const handleChangePassword = async (e) => {
        e.preventDefault()
        if (isSubmitDisabled) return;

        setIsLoadingChangePassword(true)

        const response = await putDataApi("/admin/user/change-password", {
            old_password: oldPassword,
            new_password: newPassword,
            confirm_new_password: confirmPassword
        });
        console.log(response)

        if (response?.success === true) {
            context.openAlertBox(
                "success", response?.message
            )

            setOldPassword("");
            setNewPassword("");
            setConfirmPassword("");
        } else {
            setIsLoadingChangePassword(false)
            context.openAlertBox("error", response?.data?.detail?.message)
        }
        setIsLoadingChangePassword(false)
    }

    useEffect(() => {
        const token = localStorage.getItem("accesstoken")

        if (token === null) {
            navigate('/login')
        }
    }, [context?.isLogin])

    useEffect(() => {
        const isValid =
            oldPassword.trim() !== "" &&
            newPassword.trim() !== "" &&
            confirmPassword.trim() !== "" &&
            confirmPassword === newPassword;

        setIsSubmitDisabled(!isValid);

        if (confirmPassword && confirmPassword !== newPassword) {
            setError("Mật khẩu xác nhận không khớp");
        } else {
            setError("");
        }
    }, [oldPassword, newPassword, confirmPassword]);

    return (
        <section className="py-10 w-full">
            <div className="container flex gap-5">
                <div className="col2 w-[50%]">
                    <div className="card bg-white p-5 shadow-md rounded-md mb-5">
                        <div className="flex items-center pb-3 border-b border-[rgba(0,0,0,0.1)]">
                            <h2 className="pb-0">My Profile</h2>

                            <Button className="!ml-auto" onClick={() => setIsShowChangePassword(prev => !prev)}>
                                {isShowChangePassword ? <h3 className="pb-0 text-[rgba(0,0,0,0.7)]">Hide Change Password</h3> : <h3 className="pb-0 text-[rgba(0,0,0,0.7)]">Change Password</h3>}
                            </Button>
                        </div>


                        <form className="mt-5" onSubmit={handleSubmit}>
                            <div className="flex items-center gap-5">
                                <div className="w-[50%]">
                                    <TextField type="text" id="first_name" name="first_name" value={formFields.first_name} label="First Name" variant="outlined" size="small" className="w-full" onChange={onChangeInput}
                                        disabled={isLoading === true ? true : false} />
                                </div>

                                <div className="w-[50%]">
                                    <TextField type="text" id="last_name" name="last_name" value={formFields.last_name} label="Last Name" variant="outlined" size="small" className="w-full" onChange={onChangeInput}
                                        disabled={isLoading === true ? true : false} />
                                </div>
                            </div>

                            <div className="flex items-center mt-4 gap-5">
                                <div className="w-[50%]">
                                    <TextField type="text" id="phone" name="phone" value={formFields.phone} label="Phone" variant="outlined" size="small" className="w-full" onChange={onChangeInput}
                                        disabled={isLoading === true ? true : false}
                                        error={formFields.phone !== "" && !isValidVietnamesePhone(formFields.phone)}
                                        helperText={
                                            formFields.phone !== "" && !isValidVietnamesePhone(formFields.phone)
                                                ? "Số điện thoại không hợp lệ"
                                                : ""
                                        } />
                                </div>
                            </div>

                            <div className="flex items-center gap-4 mt-5">
                                <button type="submit" disabled={!validateValue || isLoading}
                                    className={`btn-blue btn-lg w-[200px] ${(!validateValue || isLoading) ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}>
                                    {
                                        isLoading === true ? <CircularProgress color="inherit" />
                                            :
                                            'Update Profile'
                                    }
                                </button>
                            </div>
                        </form>
                    </div>

                    {isShowChangePassword && (
                        <div className="card bg-white p-5 shadow-md rounded-md">
                            <div className="flex items-center pb-3 border-b border-[rgba(0,0,0,0.1)]">
                                <h2 className="pb-0">Change Password</h2>
                            </div>

                            <form className="mt-5" onSubmit={handleChangePassword}>
                                <div className="flex items-center gap-5">
                                    <div className="form-group w-[70%] relative">
                                        <TextField
                                            type={isShowPasswordOld === false ? "password" : "text"}
                                            id="old_password" name="old_password" label="Old Password" variant="outlined" size="small" className="w-full"
                                            value={oldPassword} disabled={isLoadingChangePassword === true ? true : false}
                                            onChange={(e) => setOldPassword(e.target.value)} />

                                        <Button className="!absolute top-[4px] right-[2px] z-50 !w-[35px] !h-[35px] !min-w-[35px]
                            !rounded-full !text-black" onClick={() => setIsShowPasswordOld(!isShowPasswordOld)}>
                                            {
                                                isShowPasswordOld === true ?
                                                    <IoMdEye className="text-[20px] opacity-75" />
                                                    :
                                                    <IoMdEyeOff className="text-[20px] opacity-75" />
                                            }
                                        </Button>
                                    </div>
                                </div>

                                <div className="flex items-center mt-4 gap-5">
                                    <div className="form-group w-[70%] relative">
                                        <TextField
                                            type={isShowPasswordNew === false ? "password" : "text"}
                                            id="new_password" name="new_password" label="New Password" variant="outlined" size="small" className="w-full"
                                            value={newPassword} disabled={isLoadingChangePassword === true ? true : false}
                                            onChange={(e) => setNewPassword(e.target.value)} />

                                        <Button className="!absolute top-[4px] right-[2px] z-50 !w-[35px] !h-[35px] !min-w-[35px]
                            !rounded-full !text-black" onClick={() => setIsShowPasswordNew(!isShowPasswordNew)}>
                                            {
                                                isShowPasswordNew === true ?
                                                    <IoMdEye className="text-[20px] opacity-75" />
                                                    :
                                                    <IoMdEyeOff className="text-[20px] opacity-75" />
                                            }
                                        </Button>
                                    </div>
                                </div>

                                <div className="flex items-center mt-4 gap-5">
                                    <div className="form-group w-[70%] mb-5 relative" ref={confirmPasswordRef}>
                                        <TextField
                                            type={isShowPasswordConfirm === false ? "password" : "text"}
                                            id="confirm_new_password" name="confirm_new_password" label="Confirm Password" variant="outlined" size="small" className="w-full"
                                            disabled={isLoadingChangePassword === true ? true : false}
                                            value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)}
                                            error={!!error} helperText={error} />

                                        <Button className="!absolute top-[4px] right-[2px] z-50 !w-[35px] !h-[35px] !min-w-[35px]
                            !rounded-full !text-black" onClick={() => setIsShowPasswordConfirm(!isShowPasswordConfirm)}>
                                            {
                                                isShowPasswordConfirm === true ?
                                                    <IoMdEye className="text-[20px] opacity-75" />
                                                    :
                                                    <IoMdEyeOff className="text-[20px] opacity-75" />
                                            }
                                        </Button>
                                    </div>
                                </div>

                                <div className="flex items-center w-full mb-3">
                                    <button
                                        type="submit"
                                        disabled={
                                            isSubmitDisabled ||
                                            !oldPassword ||
                                            !newPassword ||
                                            !confirmPassword ||
                                            confirmPassword !== newPassword
                                        }
                                        className={`btn-blue btn-lg w-[250px] flex items-center justify-center transition ${isSubmitDisabled || isLoadingChangePassword ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
                                    >
                                        {
                                            isLoadingChangePassword === true ? <CircularProgress color="inherit" />
                                                :
                                                'Change Password'
                                        }
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}
                </div>
            </div>
        </section>
    )
}

export default Profile