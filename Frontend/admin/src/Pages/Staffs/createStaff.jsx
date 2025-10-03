import React, { useState, useContext } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Button,
    IconButton,
    InputAdornment,
    Alert
} from '@mui/material';
import { MdClose, MdVisibility, MdVisibilityOff } from 'react-icons/md';
import { MyContext } from '../../App';
import { postDataApi } from '../../utils/api';


const CreateStaffDialog = ({ open, onClose, onSuccess }) => {
    const context = useContext(MyContext);
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        password: ''
    });
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));

        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.first_name.trim()) {
            newErrors.first_name = 'Vui lòng nhập họ';
        }

        if (!formData.last_name.trim()) {
            newErrors.last_name = 'Vui lòng nhập tên';
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!formData.email.trim()) {
            newErrors.email = 'Vui lòng nhập email';
        } else if (!emailRegex.test(formData.email)) {
            newErrors.email = 'Email không hợp lệ';
        }

        if (!formData.password) {
            newErrors.password = 'Vui lòng nhập mật khẩu';
        } else if (formData.password.length < 6) {
            newErrors.password = 'Mật khẩu phải có ít nhất 6 ký tự';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async () => {
        if (!validateForm()) return;

        setLoading(true);
        try {
            const response = await postDataApi('/admin/auth/signup', formData);

            if (response.message) {
                context.openAlertBox('success', response.message);
                handleClose();
                if (onSuccess) onSuccess();
            } else {
                context.openAlertBox('error', response?.data?.detail?.message || 'Tạo tài khoản thất bại');
            }
        } catch (error) {
            console.error('Error creating staff:', error);
            context.openAlertBox('error', error?.response?.data?.detail?.message || 'Lỗi hệ thống khi tạo tài khoản');
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setFormData({
            first_name: '',
            last_name: '',
            email: '',
            password: ''
        });
        setErrors({});
        setShowPassword(false);
        onClose();
    };

    return (
        <Dialog
            open={open}
            onClose={handleClose}
            maxWidth="sm"
            fullWidth
            PaperProps={{
                className: "rounded-lg"
            }}
        >
            <DialogTitle className="flex items-center justify-between border-b pb-3">
                <span className="text-xl font-semibold text-gray-800">
                    Tạo tài khoản nhân viên
                </span>
                <IconButton
                    onClick={handleClose}
                    size="small"
                    className="!text-gray-500 hover:!text-gray-700"
                >
                    <MdClose size={24} />
                </IconButton>
            </DialogTitle>

            <DialogContent className="mt-4">
                <Alert severity="info" className="mb-4">
                    Link xác thực sẽ được gửi qua email đã đăng ký
                </Alert>

                <div className="flex flex-col gap-4">
                    <div className="grid grid-cols-2 gap-3">
                        <TextField
                            label="Họ"
                            name="first_name"
                            value={formData.first_name}
                            onChange={handleInputChange}
                            fullWidth
                            required
                            error={!!errors.first_name}
                            helperText={errors.first_name}
                            disabled={loading}
                        />
                        <TextField
                            label="Tên"
                            name="last_name"
                            value={formData.last_name}
                            onChange={handleInputChange}
                            fullWidth
                            required
                            error={!!errors.last_name}
                            helperText={errors.last_name}
                            disabled={loading}
                        />
                    </div>

                    <TextField
                        label="Email"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        fullWidth
                        required
                        error={!!errors.email}
                        helperText={errors.email}
                        disabled={loading}
                        placeholder="example@company.com"
                    />

                    <TextField
                        label="Mật khẩu"
                        name="password"
                        type={showPassword ? "text" : "password"}
                        value={formData.password}
                        onChange={handleInputChange}
                        fullWidth
                        required
                        error={!!errors.password}
                        helperText={errors.password || "Mật khẩu phải có ít nhất 6 ký tự"}
                        disabled={loading}
                        InputProps={{
                            endAdornment: (
                                <InputAdornment position="end">
                                    <IconButton
                                        onClick={() => setShowPassword(!showPassword)}
                                        edge="end"
                                        size="small"
                                    >
                                        {showPassword ? <MdVisibilityOff /> : <MdVisibility />}
                                    </IconButton>
                                </InputAdornment>
                            )
                        }}
                    />
                </div>
            </DialogContent>

            <DialogActions className="px-6 pb-4 pt-3 border-t">
                <Button
                    onClick={handleClose}
                    className="!text-gray-600 !normal-case"
                    disabled={loading}
                >
                    Hủy
                </Button>
                <Button
                    onClick={handleSubmit}
                    className="!bg-blue-600 hover:!bg-blue-700 !text-white !normal-case !px-6"
                    disabled={loading}
                    variant="contained"
                >
                    {loading ? 'Đang tạo...' : 'Tạo tài khoản'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default CreateStaffDialog;