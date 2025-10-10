import React, { useState, useEffect } from "react";
import {
    Drawer,
    Box,
    Typography,
    IconButton,
    CircularProgress,
    Grid,
    Paper,
    Avatar,
    Divider,
    Chip,
} from "@mui/material";
import {
    IoMdClose,
} from "react-icons/io";
import {
    FaUserCircle,
    FaMapMarkerAlt,
    FaMoneyBill,
    FaCalendarAlt,
} from "react-icons/fa";
import {
    AiOutlinePhone,
    AiOutlineMail,
    AiOutlineBank,
} from "react-icons/ai";
import { motion } from "framer-motion";
import { getDataApi } from '../../utils/api';

const SupplierDetailOffcanvas = ({ open, onClose, supplier, context }) => {
    const [detail, setDetail] = useState(null);
    const [loading, setLoading] = useState(false);

    const formatCurrency = (amount) =>
        amount == null
            ? "N/A"
            : new Intl.NumberFormat("vi-VN", {
                style: "currency",
                currency: "VND",
            }).format(amount);

    const formatDate = (dateString) => {
        if (!dateString) return "N/A";
        try {
            return new Date(dateString).toLocaleDateString("vi-VN", {
                year: "numeric",
                month: "2-digit",
                day: "2-digit",
                hour: "2-digit",
                minute: "2-digit",
            });
        } catch {
            return dateString;
        }
    };

    const fetchDetail = async (id) => {
        setLoading(true);
        setDetail(null);
        try {
            const response = await getDataApi(`/admin/suppliers/${id}`);

            if (response.success && response.data) {
                setDetail(response.data);
            } else {
                context.openAlertBox('error', response?.data?.detail?.message || 'Không tìm thấy chi tiết nhà cung cấp.');
            }
        } catch (error) {
            console.error('Error fetching supplier detail:', error);
            context.openAlertBox('error', 'Lỗi hệ thống khi tải chi tiết.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (open && supplier?.id) {
            fetchDetail(supplier.id);
        } else if (!open) {
            setDetail(null);
        }
    }, [open, supplier?.id]);


    return (
        <Drawer
            anchor="right"
            open={open}
            onClose={onClose}
            PaperProps={{
                sx: {
                    width: { xs: '100%', sm: 500, md: 600 },
                    borderRadius: { xs: 0, sm: '16px 0 0 16px' },
                    bgcolor: 'background.paper',
                    overflow: 'hidden',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                },
            }}
        >
            <motion.div
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, ease: 'easeOut' }}
                style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
            >
                {/* Header */}
                <Box
                    sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        px: 3,
                        py: 2.5,
                        bgcolor: 'primary.main',
                        color: 'primary.contrastText',
                        borderBottom: 'none',
                    }}
                >
                    <Typography variant="h6" sx={{ fontWeight: 700 }}>
                        Chi tiết Nhà Cung Cấp
                    </Typography>
                    <IconButton
                        onClick={onClose}
                        sx={{
                            color: 'inherit',
                            '&:hover': { transform: 'rotate(90deg)', bgcolor: 'rgba(255,255,255,0.1)' },
                            transition: 'transform 0.2s, background 0.2s',
                        }}
                    >
                        <IoMdClose size={24} />
                    </IconButton>
                </Box>

                {/* Content */}
                {loading ? (
                    <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <CircularProgress color="primary" />
                    </Box>
                ) : !detail ? (
                    <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', px: 3 }}>
                        <Typography color="text.secondary">Không có dữ liệu chi tiết nhà cung cấp.</Typography>
                    </Box>
                ) : (
                    <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 3, bgcolor: 'grey.50' }}>
                        {/* Profile Card */}
                        <Paper
                            sx={{
                                p: 3,
                                borderRadius: 4,
                                mb: 3,
                                display: 'flex',
                                alignItems: 'center',
                                gap: 3,
                                boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                                bgcolor: 'white',
                            }}
                        >
                            <Avatar
                                sx={{
                                    width: 80,
                                    height: 80,
                                    fontSize: 32,
                                    bgcolor: 'primary.main',
                                    color: 'white',
                                    fontWeight: 700,
                                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                                }}
                            >
                                {detail.name?.[0] || 'N'}
                            </Avatar>
                            <Box sx={{ flexGrow: 1 }}>
                                <Typography variant="h5" sx={{ fontWeight: 700, color: 'text.primary' }}>
                                    {detail.name}
                                </Typography>
                                <Typography variant="body2" sx={{ color: 'text.secondary', mt: 0.5 }}>
                                    Mã NCC: {detail.code}
                                </Typography>
                                <Chip
                                    label={detail.is_active ? 'Đang hoạt động' : 'Không hoạt động'}
                                    sx={{
                                        mt: 1,
                                        fontWeight: 600,
                                        color: 'white',
                                        bgcolor: detail.is_active ? 'success.main' : 'error.main',
                                        '&:hover': { opacity: 0.9 },
                                    }}
                                />
                            </Box>
                        </Paper>

                        {/* Contact Info */}
                        <InfoSection title="Liên hệ" icon={<FaUserCircle size={20} />}>
                            <InfoRow label="Người liên hệ" value={detail.contact_person} />
                            <InfoRow label="Số điện thoại" value={detail.phone} />
                            <InfoRow label="Email" value={detail.email} />
                            <InfoRow label="Địa chỉ" value={detail.address} />
                        </InfoSection>

                        {/* Accounting Info */}
                        <InfoSection title="Kế toán" icon={<AiOutlineBank size={20} />}>
                            <InfoRow label="Số TK Ngân hàng" value={detail.bank_account} />
                            <InfoRow label="Tên Ngân hàng" value={detail.bank_name} />
                            <InfoRow label="Hạn mức công nợ" value={formatCurrency(detail.credit_limit)} />
                            <InfoRow label="Công nợ hiện tại" value={formatCurrency(detail.current_debt)} />
                        </InfoSection>

                        {/* Notes */}
                        <InfoSection title="Ghi chú" icon={<FaMoneyBill size={20} />}>
                            <Paper
                                variant="outlined"
                                sx={{
                                    p: 2,
                                    bgcolor: 'white',
                                    borderColor: 'grey.300',
                                    borderRadius: 2,
                                    minHeight: 80,
                                    maxHeight: 200,
                                    overflowY: 'auto',
                                    color: 'text.secondary',
                                    whiteSpace: 'pre-wrap',
                                    boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.05)',
                                }}
                            >
                                {detail.notes || 'Không có ghi chú.'}
                            </Paper>
                        </InfoSection>

                        <Divider sx={{ my: 3, borderColor: 'grey.300' }} />
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, justifyContent: 'center' }}>
                            <FaCalendarAlt size={16} color="grey.600" />
                            <Typography variant="caption" sx={{ color: 'text.secondary', fontStyle: 'italic' }}>
                                Ngày tạo: {formatDate(detail.created_at)}
                            </Typography>
                        </Box>
                    </Box>
                )}
            </motion.div>
        </Drawer>
    );
};

const InfoSection = ({ title, icon, children }) => (
    <Paper
        sx={{
            p: 3,
            mb: 3,
            borderRadius: 4,
            boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
            bgcolor: 'white',
        }}
    >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box sx={{ color: 'primary.main', mr: 1.5 }}>{icon}</Box>
            <Typography variant="h6" sx={{ fontWeight: 600, color: 'text.primary' }}>
                {title}
            </Typography>
        </Box>
        <Grid container spacing={2}>
            {children}
        </Grid>
    </Paper>
);

const InfoRow = ({ label, value }) => (
    <Grid item xs={12} sm={6}>
        <Box>
            <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 500, mb: 0.5 }}>
                {label}
            </Typography>
            <Typography variant="body1" sx={{ color: 'text.primary', fontWeight: 600, wordBreak: 'break-word' }}>
                {value || 'N/A'}
            </Typography>
        </Box>
    </Grid>
);

export default SupplierDetailOffcanvas;