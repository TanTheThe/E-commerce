import React, { useState, useEffect, useContext } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Rating,
    Avatar,
    Chip,
    Divider,
    CircularProgress,
    Box,
    Typography,
    Card,
    CardContent,
    Grid
} from '@mui/material';
import {
    Person,
    ShoppingBag,
    Receipt,
    CalendarToday,
    Star,
    Comment,
    Image as ImageIcon
} from '@mui/icons-material';
import { MyContext } from '../../App';
import { getDataApi } from '../../utils/api';


const ReviewDetailDialog = ({ open, onClose, reviewId }) => {
    const [reviewDetail, setReviewDetail] = useState(null);
    const [loading, setLoading] = useState(false);
    const context = useContext(MyContext);

    const fetchReviewDetail = async (id) => {
        if (!id) return;

        try {
            setLoading(true);
            const response = await getDataApi(`/admin/evaluate/${id}`);

            if (response.success) {
                const data = response.data || response.content;
                setReviewDetail(data);
            } else {
                context.openAlertBox("error", "Không thể tải thông tin chi tiết đánh giá");
            }
        } catch (error) {
            console.error('Error fetching review detail:', error);
            context.openAlertBox("error", "Lỗi hệ thống khi tải chi tiết đánh giá");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (open && reviewId) {
            fetchReviewDetail(reviewId);
        }
    }, [open, reviewId]);

    const handleClose = () => {
        setReviewDetail(null);
        onClose();
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return 'N/A';
        return new Date(dateStr).toLocaleDateString('vi-VN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getCustomerName = (customer) => {
        if (!customer) return 'N/A';
        return `${customer.first_name || ''} ${customer.last_name || ''}`.trim() || 'N/A';
    };

    const getProductInfo = (product) => {
        if (!product) return { name: 'N/A', size: null, color: null };
        return {
            name: product.name || 'N/A',
            size: product.size,
            color: product.color_name
        };
    };

    return (
        <Dialog
            open={open}
            onClose={handleClose}
            maxWidth="md"
            fullWidth
            PaperProps={{
                sx: { borderRadius: 2, maxHeight: '90vh' }
            }}
        >
            <DialogTitle sx={{ pb: 1, borderBottom: '1px solid #e0e0e0' }}>
                <Box display="flex" alignItems="center" gap={1}>
                    <Star color="primary" />
                    <Typography variant="h6" component="span">
                        Chi tiết đánh giá
                    </Typography>
                </Box>
            </DialogTitle>

            <DialogContent sx={{ p: 0 }}>
                {loading ? (
                    <Box display="flex" justifyContent="center" alignItems="center" py={8}>
                        <CircularProgress />
                    </Box>
                ) : reviewDetail ? (
                    <Box sx={{ p: 3, maxHeight: '70vh', overflowY: 'auto' }}>
                        <Grid container spacing={3} sx={{ mb: 3 }}>
                            <Grid item xs={12} md={6}>
                                <Card variant="outlined" sx={{ height: '100%' }}>
                                    <CardContent>
                                        <Box display="flex" alignItems="center" gap={2} mb={2}>
                                            <Avatar sx={{ bgcolor: 'primary.main' }}>
                                                <Person />
                                            </Avatar>
                                            <Typography variant="h6" color="primary">
                                                Khách hàng
                                            </Typography>
                                        </Box>
                                        <Typography variant="body1" fontWeight="medium">
                                            {getCustomerName(reviewDetail.customer)}
                                        </Typography>
                                        <Box display="flex" alignItems="center" gap={1} mt={1}>
                                            <Receipt fontSize="small" color="action" />
                                            <Typography variant="body2" color="text.secondary">
                                                Mã đơn: {reviewDetail.code || 'N/A'}
                                            </Typography>
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>

                            <Grid item xs={12} md={6}>
                                <Card variant="outlined" sx={{ height: '100%' }}>
                                    <CardContent>
                                        <Box display="flex" alignItems="center" gap={2} mb={2}>
                                            <Avatar sx={{ bgcolor: 'secondary.main' }}>
                                                <ShoppingBag />
                                            </Avatar>
                                            <Typography variant="h6" color="secondary">
                                                Sản phẩm
                                            </Typography>
                                        </Box>
                                        <Typography variant="body1" fontWeight="medium">
                                            {getProductInfo(reviewDetail.product).name}
                                        </Typography>
                                        <Box display="flex" gap={1} mt={1} flexWrap="wrap">
                                            {getProductInfo(reviewDetail.product).size && (
                                                <Chip
                                                    label={`Size: ${getProductInfo(reviewDetail.product).size}`}
                                                    size="small"
                                                    variant="outlined"
                                                />
                                            )}
                                            {getProductInfo(reviewDetail.product).color && (
                                                <Chip
                                                    label={`Màu: ${getProductInfo(reviewDetail.product).color}`}
                                                    size="small"
                                                    variant="outlined"
                                                />
                                            )}
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>

                        <Divider sx={{ my: 3 }} />

                        <Box mb={3}>
                            <Typography variant="h6" gutterBottom color="primary" display="flex" alignItems="center" gap={1}>
                                <Star />
                                Đánh giá ban đầu
                            </Typography>
                            <Card sx={{ bgcolor: 'primary.50'}}>
                                <CardContent>
                                    <Box display="flex" alignItems="center" gap={2} mb={2}>
                                        <Rating
                                            value={reviewDetail.rate || 0}
                                            readOnly
                                            precision={0.5}
                                        />
                                        <Typography variant="body2" color="text.secondary">
                                            ({reviewDetail.rate || 0}/5)
                                        </Typography>
                                        <Box display="flex" alignItems="center" gap={1} ml="auto">
                                            <CalendarToday fontSize="small" color="action" />
                                            <Typography variant="body2" color="text.secondary">
                                                {formatDate(reviewDetail.created_at)}
                                            </Typography>
                                        </Box>
                                    </Box>

                                    {reviewDetail.comment && (
                                        <Box mb={2}>
                                            <Box display="flex" alignItems="center" gap={1} mb={1}>
                                                <Comment fontSize="small" color="action" />
                                                <Typography variant="subtitle2">Bình luận:</Typography>
                                            </Box>
                                            <Typography
                                                variant="body2"
                                                sx={{
                                                    bgcolor: 'white',
                                                    p: 2,
                                                    borderRadius: 1,
                                                    border: '1px solid #e0e0e0'
                                                }}
                                            >
                                                {reviewDetail.comment}
                                            </Typography>
                                        </Box>
                                    )}

                                    {reviewDetail.image && (
                                        <Box>
                                            <Box display="flex" alignItems="center" gap={1} mb={2}>
                                                <ImageIcon fontSize="small" color="action" />
                                                <Typography variant="subtitle2">Hình ảnh:</Typography>
                                            </Box>
                                            <Box
                                                component="img"
                                                src={reviewDetail.image}
                                                alt="Review"
                                                sx={{
                                                    maxWidth: '100%',
                                                    maxHeight: '200px',
                                                    borderRadius: 1,
                                                    border: '1px solid #e0e0e0',
                                                    objectFit: 'cover'
                                                }}
                                            />
                                        </Box>
                                    )}
                                </CardContent>
                            </Card>
                        </Box>

                        {(reviewDetail.additional_comment || reviewDetail.additional_image) && (
                            <Box>
                                <Typography variant="h6" gutterBottom color="success.main" display="flex" alignItems="center" gap={1}>
                                    <Star />
                                    Đánh giá bổ sung
                                </Typography>
                                <Card sx={{ bgcolor: 'success.50', border: '1px solid', borderColor: 'success.200' }}>
                                    <CardContent>
                                        <Box display="flex" alignItems="center" gap={1} mb={2}>
                                            <CalendarToday fontSize="small" color="action" />
                                            <Typography variant="body2" color="text.secondary">
                                                Bổ sung vào: {formatDate(reviewDetail.additional_created_at)}
                                            </Typography>
                                        </Box>

                                        {reviewDetail.additional_comment && (
                                            <Box mb={2}>
                                                <Box display="flex" alignItems="center" gap={1} mb={1}>
                                                    <Comment fontSize="small" color="action" />
                                                    <Typography variant="subtitle2">Bình luận bổ sung:</Typography>
                                                </Box>
                                                <Typography
                                                    variant="body2"
                                                    sx={{
                                                        bgcolor: 'white',
                                                        p: 2,
                                                        borderRadius: 1,
                                                        border: '1px solid #e0e0e0'
                                                    }}
                                                >
                                                    {reviewDetail.additional_comment}
                                                </Typography>
                                            </Box>
                                        )}

                                        {reviewDetail.additional_image && (
                                            <Box>
                                                <Box display="flex" alignItems="center" gap={1} mb={2}>
                                                    <ImageIcon fontSize="small" color="action" />
                                                    <Typography variant="subtitle2">Hình ảnh bổ sung:</Typography>
                                                </Box>
                                                <Box
                                                    component="img"
                                                    src={reviewDetail.additional_image}
                                                    alt="Additional Review"
                                                    sx={{
                                                        maxWidth: '100%',
                                                        maxHeight: '200px',
                                                        borderRadius: 1,
                                                        border: '1px solid #e0e0e0',
                                                        objectFit: 'cover'
                                                    }}
                                                />
                                            </Box>
                                        )}
                                    </CardContent>
                                </Card>
                            </Box>
                        )}
                    </Box>
                ) : (
                    <Box display="flex" justifyContent="center" alignItems="center" py={8}>
                        <Typography color="text.secondary">
                            Không có dữ liệu để hiển thị
                        </Typography>
                    </Box>
                )}
            </DialogContent>

            <DialogActions sx={{ p: 2, borderTop: '1px solid #e0e0e0' }}>
                <Button
                    onClick={handleClose}
                    variant="contained"
                    sx={{ minWidth: 100 }}
                >
                    Đóng
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default ReviewDetailDialog;