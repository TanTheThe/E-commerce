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

const EditMaterialModal = ({ open, onClose, onMaterialUpdated, context, materialToEdit }) => {
    const [materialName, setMaterialName] = useState('');
    const [isActive, setIsActive] = useState(true);
    const [loading, setLoading] = useState(false);
    const [nameError, setNameError] = useState('');

    useEffect(() => {
        if (materialToEdit && open) {
            setMaterialName(materialToEdit.name || '');
            setIsActive(materialToEdit.is_active !== undefined ? materialToEdit.is_active : true);
        }
    }, [materialToEdit, open]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!materialName.trim()) {
            setNameError('Tên chất liệu không được để trống');
            return;
        }

        if (!materialToEdit?.id) {
            context.openAlertBox('error', 'Không tìm thấy thông tin chất liệu cần cập nhật');
            return;
        }

        setLoading(true);
        try {
            const requestData = {
                name: materialName.trim(),
                is_active: isActive
            };

            const response = await putDataApi(`/admin/material/${materialToEdit.id}`, requestData);

            if (response.success) {
                context.openAlertBox('success', response.message || 'Cập nhật chất liệu thành công!');
                onMaterialUpdated();
                handleClose();
            } else {
                context.openAlertBox('error', response.data.detail.message || 'Có lỗi xảy ra khi cập nhật chất liệu');
            }
        } catch (error) {
            console.error('Error updating material:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi cập nhật chất liệu');
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setMaterialName('');
        setIsActive(true);
        setNameError('');
        onClose();
    };

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
                    Chỉnh sửa chất liệu
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
                            label="Tên chất liệu"
                            type="text"
                            fullWidth
                            variant="outlined"
                            value={materialName}
                            onChange={(e) => {
                                setMaterialName(e.target.value);
                                setNameError('');
                            }}
                            error={!!nameError}
                            helperText={nameError}
                            placeholder="Ví dụ: Cotton, Polyester, Silk..."
                            required
                        />
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
                                        {isActive ? 'Chất liệu sẽ hiển thị công khai' : 'Chất liệu sẽ bị ẩn'}
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
                    {loading ? 'Đang cập nhật...' : 'Cập nhật chất liệu'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default EditMaterialModal;