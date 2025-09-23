import React, { useState, useEffect, useRef, useContext } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Box,
    IconButton,
    Typography,
    Backdrop,
    FormControlLabel,
    Switch,
    Chip
} from '@mui/material';
import { IoMdClose } from "react-icons/io";
import { IoCopyOutline } from "react-icons/io5";
import { putDataApi } from '../../utils/api';
import { FaPlus } from 'react-icons/fa';

const EditBrandModal = ({ open, onClose, onBrandUpdated, context, brandToEdit }) => {
    const [brandName, setBrandName] = useState('');
    const [logoBase64, setLogoBase64] = useState('');
    const [isActive, setIsActive] = useState(true);
    const [loading, setLoading] = useState(false);
    const [nameError, setNameError] = useState('');
    const [imagePreview, setImagePreview] = useState(null);

    useEffect(() => {
        if (brandToEdit && open) {
            setBrandName(brandToEdit.name || '');
            setIsActive(brandToEdit.is_active !== undefined ? brandToEdit.is_active : true);

            if (brandToEdit.logo) {
                setImagePreview({
                    url: brandToEdit.logo,
                    isExisting: true
                });
            }
        }
    }, [brandToEdit, open]);

    const convertToBase64 = (file) => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    };

    const handleImageUpload = async (e) => {
        const file = e.target.files[0];
        if (file) {
            try {
                const previewUrl = URL.createObjectURL(file);
                const base64 = await convertToBase64(file);

                if (imagePreview && !imagePreview.isExisting) {
                    URL.revokeObjectURL(imagePreview.url);
                }

                setImagePreview({
                    url: previewUrl,
                    file: file,
                    name: file.name,
                    isExisting: false
                });
                setLogoBase64(base64);
            } catch (error) {
                console.error("Error uploading image:", error);
                context.openAlertBox("error", "Có lỗi xảy ra trong quá trình upload ảnh");
            }
        }
    };

    const removeImage = () => {
        if (imagePreview) {
            if (!imagePreview.isExisting) {
                URL.revokeObjectURL(imagePreview.url);
            }
            setImagePreview(null);
            setLogoBase64('');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!brandName.trim()) {
            setNameError('Tên thương hiệu không được để trống');
            return;
        }

        if (!brandToEdit?.id) {
            context.openAlertBox('error', 'Không tìm thấy thông tin thương hiệu cần cập nhật');
            return;
        }

        setLoading(true);
        try {
            const requestData = {
                name: brandName.trim(),
                is_active: isActive
            };

            if (logoBase64) {
                requestData.logo = logoBase64;
            }

            const response = await putDataApi(`/admin/brand/${brandToEdit.id}`, requestData);

            if (response.success) {
                context.openAlertBox('success', response.message || 'Cập nhật thương hiệu thành công!');
                onBrandUpdated();
                handleClose();
            } else {
                context.openAlertBox('error', response.data.detail.message || 'Có lỗi xảy ra khi cập nhật thương hiệu');
            }
        } catch (error) {
            console.error('Error updating brand:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi cập nhật thương hiệu');
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setBrandName('');
        setLogoBase64('');
        setIsActive(true);
        setNameError('');

        if (imagePreview && !imagePreview.isExisting) {
            URL.revokeObjectURL(imagePreview.url);
        }
        setImagePreview(null);
        onClose();
    };

    useEffect(() => {
        return () => {
            if (imagePreview?.url && !imagePreview.isExisting) {
                URL.revokeObjectURL(imagePreview.url);
            }
        };
    }, [imagePreview]);

    return (
        <Dialog
            open={open}
            onClose={handleClose}
            maxWidth="sm"
            fullWidth
            PaperProps={{
                style: {
                    borderRadius: '12px',
                    padding: '8px'
                }
            }}
            BackdropComponent={Backdrop}
            BackdropProps={{
                style: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                }
            }}
        >
            <DialogTitle sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '20px 24px 16px',
                borderBottom: '1px solid #e5e5e5'
            }}>
                <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
                    Chỉnh sửa thương hiệu
                </Typography>
                <IconButton
                    onClick={handleClose}
                    sx={{
                        color: '#666',
                        '&:hover': {
                            backgroundColor: '#f5f5f5'
                        }
                    }}
                >
                    <IoMdClose size={24} />
                </IconButton>
            </DialogTitle>

            <DialogContent sx={{ padding: '24px' }}>
                <form onSubmit={handleSubmit}>
                    <Box sx={{ mb: 3 }}>
                        <TextField
                            autoFocus
                            margin="dense"
                            label="Tên thương hiệu"
                            type="text"
                            fullWidth
                            variant="outlined"
                            value={brandName}
                            onChange={(e) => {
                                setBrandName(e.target.value);
                                setNameError('');
                            }}
                            error={!!nameError}
                            helperText={nameError}
                            placeholder="Ví dụ: Nike, Adidas, Samsung..."
                            required
                        />
                    </Box>

                    <Box sx={{ mb: 3 }}>
                        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 500 }}>
                            Logo thương hiệu
                        </Typography>
                        {imagePreview ? (
                            <Box sx={{
                                position: 'relative',
                                width: '100%',
                                height: '150px',
                                border: '1px solid #e0e0e0',
                                borderRadius: '8px',
                                overflow: 'hidden',
                                backgroundColor: '#f9f9f9'
                            }}>
                                <img
                                    src={imagePreview.url}
                                    alt={imagePreview.name || 'Brand logo'}
                                    style={{
                                        width: '100%',
                                        height: '100%',
                                        objectFit: 'contain',
                                        padding: '8px'
                                    }}
                                />
                                <IconButton
                                    onClick={removeImage}
                                    sx={{
                                        position: 'absolute',
                                        top: 4,
                                        right: 4,
                                        backgroundColor: '#f44336',
                                        color: 'white',
                                        width: 24,
                                        height: 24,
                                        '&:hover': {
                                            backgroundColor: '#d32f2f'
                                        }
                                    }}
                                >
                                    <IoMdClose size={16} />
                                </IconButton>
                                {!imagePreview.isExisting && (
                                    <Chip
                                        label="Ảnh mới"
                                        size="small"
                                        color="success"
                                        sx={{
                                            position: 'absolute',
                                            bottom: 8,
                                            left: 8
                                        }}
                                    />
                                )}
                            </Box>
                        ) : (
                            <Box sx={{
                                border: '2px dashed #e0e0e0',
                                height: '150px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                backgroundColor: '#f9f9f9',
                                borderRadius: '8px',
                                position: 'relative',
                                cursor: 'pointer',
                                '&:hover': {
                                    borderColor: '#2196F3',
                                    backgroundColor: '#f0f8ff'
                                }
                            }}>
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={handleImageUpload}
                                    style={{
                                        position: 'absolute',
                                        inset: 0,
                                        opacity: 0,
                                        zIndex: 10,
                                        cursor: 'pointer'
                                    }}
                                    id="logoUpload"
                                />
                                <label htmlFor="logoUpload" style={{
                                    textAlign: 'center',
                                    color: '#666',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'center',
                                    gap: '8px'
                                }}>
                                    <FaPlus style={{ fontSize: '24px' }} />
                                    <Typography variant="body2">
                                        Thay đổi logo thương hiệu
                                    </Typography>
                                    <Typography variant="caption" sx={{ color: '#999' }}>
                                        (Không bắt buộc)
                                    </Typography>
                                </label>
                            </Box>
                        )}
                        <Typography variant="caption" sx={{ color: '#666', mt: 1, display: 'block' }}>
                            {imagePreview ? 'Bạn có thể thay đổi logo hoặc giữ nguyên logo hiện tại' : 'Chọn ảnh mới hoặc để trống để giữ logo hiện tại'}
                        </Typography>
                    </Box>

                    <Box sx={{
                        mb: 3,
                        padding: '16px',
                        border: '1px solid #e0e0e0',
                        borderRadius: '8px',
                        backgroundColor: '#f9f9f9'
                    }}>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={isActive}
                                    onChange={(e) => setIsActive(e.target.checked)}
                                    color="primary"
                                />
                            }
                            label={
                                <Box>
                                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                                        Trạng thái hoạt động
                                    </Typography>
                                    <Typography variant="body2" sx={{ color: '#666', fontSize: '0.85rem' }}>
                                        {isActive ? 'Thương hiệu sẽ hiển thị công khai' : 'Thương hiệu sẽ bị ẩn'}
                                    </Typography>
                                </Box>
                            }
                        />
                    </Box>

                    <Box sx={{ mb: 2, textAlign: 'center' }}>
                        <Chip
                            label={isActive ? 'Đang hoạt động' : 'Không hoạt động'}
                            color={isActive ? 'success' : 'error'}
                            variant="outlined"
                            size="small"
                        />
                    </Box>
                </form>
            </DialogContent>

            <DialogActions sx={{
                padding: '16px 24px 24px',
                borderTop: '1px solid #e5e5e5',
                gap: '12px'
            }}>
                <Button
                    onClick={handleClose}
                    variant="outlined"
                    sx={{
                        borderColor: '#ddd',
                        color: '#666',
                        '&:hover': {
                            borderColor: '#bbb',
                            backgroundColor: '#f9f9f9'
                        }
                    }}
                >
                    Hủy
                </Button>
                <Button
                    onClick={handleSubmit}
                    variant="contained"
                    disabled={loading}
                    sx={{
                        backgroundColor: '#2196F3',
                        '&:hover': {
                            backgroundColor: '#1976D2'
                        },
                        '&:disabled': {
                            backgroundColor: '#ccc'
                        }
                    }}
                >
                    {loading ? 'Đang cập nhật...' : 'Cập nhật thương hiệu'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default EditBrandModal;