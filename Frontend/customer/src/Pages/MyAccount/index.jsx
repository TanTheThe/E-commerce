import Button from "@mui/material/Button";
import React, { useContext, useEffect, useRef, useState } from "react";
import TextField from '@mui/material/TextField';
import AccountSideBar from "../../components/AccountSideBar";
import { MyContext } from "../../App";
import { useNavigate } from "react-router-dom";
import { putDataApi } from "../../utils/api";
import { CircularProgress } from "@mui/material";
import { IoMdEye, IoMdEyeOff } from "react-icons/io";

const MyAccount = () => {
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

    const [formFields, setFormFields] = useState({
        first_name: '',
        last_name: '',
        phone: ''
    })

    useEffect(() => {
        if (context?.userData?.content) {
            setFormFields({
                first_name: context.userData.content.first_name || '',
                last_name: context.userData.content.last_name || '',
                phone: context.userData.content.phone || ''
            });
        }
    }, [context?.userData]);

    const onChangeInput = (e) => {
        const { name, value } = e.target
        setFormFields(prevFields => ({
            ...prevFields,
            [name]: value
        }))
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

        if (!validateValue) return;

        setIsLoading(true)

        try {
            const response = await putDataApi("/customer/user", formFields);

            if (response?.success === true) {
                context.setUserData(prev => ({
                    ...prev,
                    content: {
                        ...prev.content,
                        first_name: formFields.first_name,
                        last_name: formFields.last_name,
                        phone: formFields.phone
                    }
                }));

                context.openAlertBox("success", response?.message || "Profile updated successfully!")
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || "Failed to update profile")
            }
        } catch (error) {
            console.error("Error updating profile:", error);
            context.openAlertBox("error", "An error occurred while updating your profile");
        } finally {
            setIsLoading(false)
        }
    }

    const handleChangePassword = async (e) => {
        e.preventDefault()
        if (isSubmitDisabled) return;

        setIsLoadingChangePassword(true)
        setError("");

        try {
            const response = await putDataApi("/customer/auth/change-password", {
                old_password: oldPassword,
                new_password: newPassword,
                confirm_new_password: confirmPassword
            });

            if (response?.success === true) {
                context.openAlertBox("success", response?.message || "Password changed successfully!")

                setOldPassword("");
                setNewPassword("");
                setConfirmPassword("");
                setIsShowChangePassword(false);
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || "Failed to change password")
            }
        } catch (error) {
            console.error("Error changing password:", error);
            context.openAlertBox("error", "An error occurred while changing your password");
        } finally {
            setIsLoadingChangePassword(false)
        }
    }

    useEffect(() => {
        const token = localStorage.getItem("accesstoken")
        if (token === null) {
            navigate('/login')
        }
    }, [navigate])

    useEffect(() => {
        const isValid =
            oldPassword.trim() !== "" &&
            newPassword.trim() !== "" &&
            confirmPassword.trim() !== "" &&
            confirmPassword === newPassword &&
            newPassword.length >= 6;

        setIsSubmitDisabled(!isValid);

        if (confirmPassword && confirmPassword !== newPassword) {
            setError("Mật khẩu xác nhận không khớp");
        } else if (newPassword && newPassword.length < 6) {
            setError("Mật khẩu mới phải có ít nhất 6 ký tự");
        } else {
            setError("");
        }
    }, [oldPassword, newPassword, confirmPassword]);

    const PasswordToggleButton = ({ isShow, onToggle }) => (
        <Button
            className="!absolute top-[12px] right-[2px] z-50 !w-[35px] !h-[35px] !min-w-[35px] !rounded-full !text-black hover:!bg-gray-100 transition-colors"
            onClick={onToggle}
            type="button"
        >
            {isShow ? (
                <IoMdEye className="text-[20px] opacity-75" />
            ) : (
                <IoMdEyeOff className="text-[20px] opacity-75" />
            )}
        </Button>
    );

    if (context?.isLoading) {
        return (
            <section className="py-10 w-full">
                <div className="container flex gap-5">
                    <div className="col1 w-[20%]">
                        <AccountSideBar />
                    </div>
                    <div className="col2 w-[80%] flex items-center justify-center">
                        <CircularProgress size={50} />
                    </div>
                </div>
            </section>
        );
    }

    return (
        <section className="py-10 w-full bg-gray-50 min-h-screen">
            <div className="container max-w-7xl mx-auto px-4">
                <div className="flex flex-col lg:flex-row gap-6">
                    <div className="lg:w-[280px] flex-shrink-0">
                        <AccountSideBar />
                    </div>

                    <div className="flex-1">

                        <div className="card bg-white p-6 shadow-lg rounded-xl mb-6 border border-gray-100">
                            <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                                <h2 className="text-2xl font-bold text-gray-800 mb-0">My Profile</h2>
                                <Button
                                    className="!bg-blue-600 !text-white hover:!bg-blue-700 !px-6 !py-2 !rounded-lg !font-medium transition-all duration-200"
                                    onClick={() => setIsShowChangePassword(prev => !prev)}
                                >
                                    {isShowChangePassword ? "Hide Change Password" : "Change Password"}
                                </Button>
                            </div>

                            <form className="mt-6" onSubmit={handleSubmit}>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <TextField
                                            type="text"
                                            id="first_name"
                                            name="first_name"
                                            value={formFields.first_name}
                                            label="First Name"
                                            variant="outlined"
                                            size="medium"
                                            className="w-full"
                                            onChange={onChangeInput}
                                            disabled={isLoading}
                                            sx={{
                                                '& .MuiOutlinedInput-root': {
                                                    '&:hover fieldset': {
                                                        borderColor: '#3b82f6',
                                                    },
                                                    '&.Mui-focused fieldset': {
                                                        borderColor: '#3b82f6',
                                                    },
                                                },
                                            }}
                                        />
                                    </div>

                                    <div>
                                        <TextField
                                            type="text"
                                            id="last_name"
                                            name="last_name"
                                            value={formFields.last_name}
                                            label="Last Name"
                                            variant="outlined"
                                            size="medium"
                                            className="w-full"
                                            onChange={onChangeInput}
                                            disabled={isLoading}
                                            sx={{
                                                '& .MuiOutlinedInput-root': {
                                                    '&:hover fieldset': {
                                                        borderColor: '#3b82f6',
                                                    },
                                                    '&.Mui-focused fieldset': {
                                                        borderColor: '#3b82f6',
                                                    },
                                                },
                                            }}
                                        />
                                    </div>
                                </div>

                                <div className="mt-6">
                                    <div className="md:w-1/2">
                                        <TextField
                                            type="text"
                                            id="phone"
                                            name="phone"
                                            value={formFields.phone}
                                            label="Phone Number"
                                            variant="outlined"
                                            size="medium"
                                            className="w-full"
                                            onChange={onChangeInput}
                                            disabled={isLoading}
                                            error={formFields.phone !== "" && !isValidVietnamesePhone(formFields.phone)}
                                            helperText={
                                                formFields.phone !== "" && !isValidVietnamesePhone(formFields.phone)
                                                    ? "Số điện thoại không hợp lệ"
                                                    : ""
                                            }
                                            sx={{
                                                '& .MuiOutlinedInput-root': {
                                                    '&:hover fieldset': {
                                                        borderColor: '#3b82f6',
                                                    },
                                                    '&.Mui-focused fieldset': {
                                                        borderColor: '#3b82f6',
                                                    },
                                                },
                                            }}
                                        />
                                    </div>
                                </div>

                                <div className="flex items-center mt-8">
                                    <button
                                        type="submit"
                                        disabled={!validateValue || isLoading}
                                        className={`px-8 py-3 rounded-lg font-semibold text-white transition-all duration-200 flex items-center gap-2 ${(!validateValue || isLoading)
                                                ? "bg-gray-400 cursor-not-allowed"
                                                : "bg-blue-600 hover:bg-blue-700 cursor-pointer shadow-lg hover:shadow-xl"
                                            }`}
                                    >
                                        {isLoading ? (
                                            <>
                                                <CircularProgress color="inherit" size={20} />
                                                <span>Updating...</span>
                                            </>
                                        ) : (
                                            'Update Profile'
                                        )}
                                    </button>
                                </div>
                            </form>
                        </div>

                        {isShowChangePassword && (
                            <div className="card bg-white p-6 shadow-lg rounded-xl border border-gray-100">
                                <div className="flex items-center pb-4 border-b border-gray-200">
                                    <h2 className="text-2xl font-bold text-gray-800 mb-0">Change Password</h2>
                                </div>

                                <form className="mt-6" onSubmit={handleChangePassword}>
                                    <div className="space-y-6">
                                        <div className="md:w-2/3">
                                            <div className="form-group relative">
                                                <TextField
                                                    type={isShowPasswordOld ? "text" : "password"}
                                                    id="old_password"
                                                    name="old_password"
                                                    label="Current Password"
                                                    variant="outlined"
                                                    size="medium"
                                                    className="w-full"
                                                    value={oldPassword}
                                                    disabled={isLoadingChangePassword}
                                                    onChange={(e) => setOldPassword(e.target.value)}
                                                    sx={{
                                                        '& .MuiOutlinedInput-root': {
                                                            '&:hover fieldset': {
                                                                borderColor: '#3b82f6',
                                                            },
                                                            '&.Mui-focused fieldset': {
                                                                borderColor: '#3b82f6',
                                                            },
                                                        },
                                                    }}
                                                />
                                                <PasswordToggleButton
                                                    isShow={isShowPasswordOld}
                                                    onToggle={() => setIsShowPasswordOld(!isShowPasswordOld)}
                                                />
                                            </div>
                                        </div>

                                        <div className="md:w-2/3">
                                            <div className="form-group relative">
                                                <TextField
                                                    type={isShowPasswordNew ? "text" : "password"}
                                                    id="new_password"
                                                    name="new_password"
                                                    label="New Password"
                                                    variant="outlined"
                                                    size="medium"
                                                    className="w-full"
                                                    value={newPassword}
                                                    disabled={isLoadingChangePassword}
                                                    onChange={(e) => setNewPassword(e.target.value)}
                                                    sx={{
                                                        '& .MuiOutlinedInput-root': {
                                                            '&:hover fieldset': {
                                                                borderColor: '#3b82f6',
                                                            },
                                                            '&.Mui-focused fieldset': {
                                                                borderColor: '#3b82f6',
                                                            },
                                                        },
                                                    }}
                                                />
                                                <PasswordToggleButton
                                                    isShow={isShowPasswordNew}
                                                    onToggle={() => setIsShowPasswordNew(!isShowPasswordNew)}
                                                />
                                            </div>
                                        </div>

                                        <div className="md:w-2/3">
                                            <div className="form-group relative">
                                                <TextField
                                                    type={isShowPasswordConfirm ? "text" : "password"}
                                                    id="confirm_new_password"
                                                    name="confirm_new_password"
                                                    label="Confirm New Password"
                                                    variant="outlined"
                                                    size="medium"
                                                    className="w-full"
                                                    disabled={isLoadingChangePassword}
                                                    value={confirmPassword}
                                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                                    error={!!error}
                                                    helperText={error}
                                                    sx={{
                                                        '& .MuiOutlinedInput-root': {
                                                            '&:hover fieldset': {
                                                                borderColor: '#3b82f6',
                                                            },
                                                            '&.Mui-focused fieldset': {
                                                                borderColor: '#3b82f6',
                                                            },
                                                        },
                                                    }}
                                                />
                                                <PasswordToggleButton
                                                    isShow={isShowPasswordConfirm}
                                                    onToggle={() => setIsShowPasswordConfirm(!isShowPasswordConfirm)}
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex items-center mt-8">
                                        <button
                                            type="submit"
                                            disabled={isSubmitDisabled || isLoadingChangePassword}
                                            className={`px-8 py-3 rounded-lg font-semibold text-white transition-all duration-200 flex items-center gap-2 ${(isSubmitDisabled || isLoadingChangePassword)
                                                    ? "bg-gray-400 cursor-not-allowed"
                                                    : "bg-green-600 hover:bg-green-700 cursor-pointer shadow-lg hover:shadow-xl"
                                                }`}
                                        >
                                            {isLoadingChangePassword ? (
                                                <>
                                                    <CircularProgress color="inherit" size={20} />
                                                    <span>Changing...</span>
                                                </>
                                            ) : (
                                                'Change Password'
                                            )}
                                        </button>
                                    </div>
                                </form>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </section>
    )
}

export default MyAccount