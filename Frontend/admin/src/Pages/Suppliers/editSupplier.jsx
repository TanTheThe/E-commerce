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
import { getDataApi, putDataApi } from '../../utils/api';
import { FaPlus } from 'react-icons/fa';

const EditSupplierModal = ({ open, onClose, onSupplierUpdated, context, supplierToEdit }) => {
    const [supplierName, setSupplierName] = useState('');
    const [contactPerson, setContactPerson] = useState('');
    const [phone, setPhone] = useState('');
    const [email, setEmail] = useState('');
    const [address, setAddress] = useState('');
    const [bankAccount, setBankAccount] = useState('');
    const [bankName, setBankName] = useState('');
    const [creditLimit, setCreditLimit] = useState('');
    const [notes, setNotes] = useState('');
    const [isActive, setIsActive] = useState(true);

    const [loading, setLoading] = useState(false);
    const [fetching, setFetching] = useState(false);
    const [nameError, setNameError] = useState('');

    const fetchSupplierDetail = async (supplierId) => {
        if (!supplierId) return;

        setFetching(true);
        try {
            const response = await getDataApi(`/admin/suppliers/${supplierId}`);

            if (response.success && response.data) {
                const data = response.data;
                setSupplierName(data.name || '');
                setContactPerson(data.contact_person || '');
                setPhone(data.phone || '');
                setEmail(data.email || '');
                setAddress(data.address || '');
                setBankAccount(data.bank_account || '');
                setBankName(data.bank_name || '');
                setCreditLimit(data.credit_limit !== undefined && data.credit_limit !== null ? data.credit_limit.toString() : '');
                setNotes(data.notes || '');
                setIsActive(data.is_active !== undefined ? data.is_active : true);
            } else {
                context.openAlertBox("error", response?.data?.detail?.message || "Lỗi khi tải chi tiết nhà cung cấp.");
            }
        } catch (error) {
            console.error('Error fetching supplier detail:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi tải chi tiết nhà cung cấp.');
        } finally {
            setFetching(false);
        }
    };

    useEffect(() => {
        if (supplierToEdit && open && supplierToEdit.id) {
            fetchSupplierDetail(supplierToEdit.id);
        }
    }, [supplierToEdit, open]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!supplierName.trim()) {
            setNameError('Tên nhà cung cấp không được để trống');
            return;
        }

        if (!supplierToEdit?.id) {
            context.openAlertBox('error', 'Không tìm thấy ID nhà cung cấp cần cập nhật');
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
                is_active: isActive
            };

            const response = await putDataApi(`/admin/suppliers/${supplierToEdit.id}`, requestData);

            if (response.success) {
                context.openAlertBox('success', response.message || 'Cập nhật nhà cung cấp thành công!');
                onSupplierUpdated();
                handleClose();
            } else {
                context.openAlertBox('error', response?.data?.detail?.message || 'Có lỗi xảy ra khi cập nhật nhà cung cấp');
            }
        } catch (error) {
            console.error('Error updating supplier:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi cập nhật nhà cung cấp');
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
                    Chỉnh sửa Nhà Cung Cấp: {supplierToEdit?.code}
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
                {fetching ? (
                    <Box sx={{ p: 4, textAlign: 'center' }}>
                        <Typography>Đang tải thông tin nhà cung cấp...</Typography>
                    </Box>
                ) : (
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
                                            {isActive ? 'Nhà cung cấp đang hoạt động' : 'Nhà cung cấp không hoạt động'}
                                        </Typography>
                                    </Box>
                                }
                            />
                            <Box sx={{ mt: 1 }}>
                                <Chip
                                    label={isActive ? 'Đang hoạt động' : 'Không hoạt động'}
                                    color={isActive ? 'success' : 'error'}
                                    variant="outlined"
                                    size="small"
                                />
                            </Box>
                        </Box>
                    </form>
                )}
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
                    disabled={loading || fetching || !supplierName.trim()}
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
                    {loading ? 'Đang cập nhật...' : 'Cập nhật Nhà Cung Cấp'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default EditSupplierModal;