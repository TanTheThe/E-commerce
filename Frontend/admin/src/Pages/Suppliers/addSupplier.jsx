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
import { FaPlus } from "react-icons/fa";
import { IoCopyOutline } from "react-icons/io5";
import { postDataApi } from '../../utils/api';

const AddSupplierModal = ({ open, onClose, onSupplierAdded, context }) => {
    const [supplierName, setSupplierName] = useState('');
    const [contactPerson, setContactPerson] = useState('');
    const [phone, setPhone] = useState('');
    const [email, setEmail] = useState('');
    const [address, setAddress] = useState('');
    const [bankAccount, setBankAccount] = useState('');
    const [bankName, setBankName] = useState('');
    const [notes, setNotes] = useState('');
    const [creditLimit, setCreditLimit] = useState('');

    const [loading, setLoading] = useState(false);
    const [nameError, setNameError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!supplierName.trim()) {
            setNameError('Tên nhà cung cấp không được để trống');
            return;
        }

        setLoading(true);
        try {
            const requestData = {
                name: supplierName.trim(),
                contact_person: contactPerson.trim() || null,
                phone: phone.trim() || null,
                email: email.trim() || null,
                address: address.trim() || null,
                bank_account: bankAccount.trim() || null,
                bank_name: bankName.trim() || null,
                credit_limit: creditLimit !== '' ? parseInt(creditLimit) : null,
                notes: notes.trim() || null,
            };

            const response = await postDataApi('/admin/suppliers', requestData);

            if (response.success) {
                context.openAlertBox('success', response.message || 'Thêm nhà cung cấp mới thành công!');
                onSupplierAdded();
                handleClose();
            } else {
                context.openAlertBox('error', response?.data?.detail?.message || 'Có lỗi xảy ra khi thêm nhà cung cấp');
            }
        } catch (error) {
            console.error('Error adding supplier:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi thêm nhà cung cấp mới');
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setSupplierName('');
        setContactPerson('');
        setPhone('');
        setEmail('');
        setAddress('');
        setBankAccount('');
        setBankName('');
        setCreditLimit('');
        setNotes('');
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
                    Thêm Nhà Cung Cấp mới
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
                    <Box sx={{ mb: 2 }}>
                        <TextField
                            autoFocus
                            margin="dense"
                            label="Tên Nhà Cung Cấp (*)"
                            type="text"
                            fullWidth
                            variant="outlined"
                            value={supplierName}
                            onChange={(e) => {
                                setSupplierName(e.target.value);
                                setNameError('');
                            }}
                            error={!!nameError}
                            helperText={nameError}
                            placeholder="Ví dụ: Công ty A"
                            required
                        />
                    </Box>

                    <Box sx={{ mb: 2 }}>
                        <TextField
                            margin="dense"
                            label="Người liên hệ"
                            type="text"
                            fullWidth
                            variant="outlined"
                            value={contactPerson}
                            onChange={(e) => setContactPerson(e.target.value)}
                            placeholder="Ví dụ: Nguyễn Văn A"
                        />
                    </Box>
                    <Box sx={{ mb: 2 }}>
                        <TextField
                            margin="dense"
                            label="Số điện thoại"
                            type="tel"
                            fullWidth
                            variant="outlined"
                            value={phone}
                            onChange={(e) => setPhone(e.target.value)}
                            placeholder="Ví dụ: 0901234567"
                        />
                    </Box>
                    <Box sx={{ mb: 2 }}>
                        <TextField
                            margin="dense"
                            label="Email"
                            type="email"
                            fullWidth
                            variant="outlined"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Ví dụ: email@congty.com"
                        />
                    </Box>
                    <Box sx={{ mb: 2 }}>
                        <TextField
                            margin="dense"
                            label="Địa chỉ"
                            type="text"
                            fullWidth
                            variant="outlined"
                            value={address}
                            onChange={(e) => setAddress(e.target.value)}
                            placeholder="Ví dụ: 123 Đường ABC, Quận XYZ"
                        />
                    </Box>
                    <Box sx={{ mb: 2 }}>
                        <TextField
                            margin="dense"
                            label="Số TK Ngân hàng"
                            type="text"
                            fullWidth
                            variant="outlined"
                            value={bankAccount}
                            onChange={(e) => setBankAccount(e.target.value)}
                        />
                    </Box>
                    <Box sx={{ mb: 2 }}>
                        <TextField
                            margin="dense"
                            label="Tên Ngân hàng"
                            type="text"
                            fullWidth
                            variant="outlined"
                            value={bankName}
                            onChange={(e) => setBankName(e.target.value)}
                        />
                    </Box>

                    <Box sx={{ mb: 2 }}>
                        <TextField
                            margin="dense"
                            label="Hạn mức công nợ (VNĐ)"
                            type="number"
                            fullWidth
                            variant="outlined"
                            value={creditLimit}
                            onChange={(e) => setCreditLimit(e.target.value)}
                            InputProps={{
                                inputProps: { min: 0 }
                            }}
                        />
                    </Box>

                    <Box sx={{ mb: 3 }}>
                        <TextField
                            margin="dense"
                            label="Ghi chú"
                            type="text"
                            fullWidth
                            multiline
                            rows={3}
                            variant="outlined"
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
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
                    disabled={loading || !supplierName.trim()}
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
                    {loading ? 'Đang thêm...' : 'Thêm Nhà Cung Cấp'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default AddSupplierModal;